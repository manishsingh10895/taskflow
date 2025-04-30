use app_state::AppState;
// src/main.rs
use axum::extract::{Request, State};
use axum::routing::get;
use axum::{
    Router, body::Body, extract::OriginalUri, http::Method, response::Response, routing::any,
};
use std::net::SocketAddr;
use std::sync::Arc;
use tokio::sync::RwLock;
use tower_http::trace::TraceLayer;

mod config;
mod middleware;
mod proxy;
mod router;
mod app_state;

use config::GatewayConfig;
use middleware::auth::auth_middleware;
use proxy::proxy_request;




#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    tracing_subscriber::fmt::init();

    let config = GatewayConfig::from_env();
    let state = AppState::new(config.clone());
    let app = Router::new() // Create a new router first
        // .with_state(config.clone()) // Then add the state
        .layer(TraceLayer::new_for_http())
        // The state is now managed by `with_state`, no need for Extension layer here
        .layer(axum::middleware::from_fn(auth_middleware))
        .fallback(forward_handler)
        .with_state(state);

    let default_addr = SocketAddr::from(([0, 0, 0, 0], 8000));
    println!("🚀 Gateway attempting to run on {}", config.addr);

    let addr = config.addr.parse::<SocketAddr>().unwrap_or(default_addr);

    let listener = tokio::net::TcpListener::bind(addr)
        .await
        .expect("Failed to bind to address");

    println!("🚀 Gateway running on http://{}", listener.local_addr()?); // Use listener's local address

    // Pass the router directly to axum::serve
    axum::serve(listener, app).await?;
    let app = Router::new().route("/", get(|| async { "Hello, World!" }));

    // run our app with hyper, listening globally on port 3000
    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();
    axum::serve(listener, app).await.unwrap();
    Ok(())
}

#[axum::debug_handler]
async fn forward_handler(
    State(state): State<AppState>, // State extractor works with Router::with_state
    req: Request<Body>,
) -> Result<Response, axum::response::Response> {
    let method = req.method().clone();
    // Handle potential missing OriginalUri gracefully
    // Extract the OriginalUri struct itself
    let original_uri = req
        .extensions()
        .get::<OriginalUri>()
        .cloned() // Clone the OriginalUri struct
        .ok_or_else(|| {
            tracing::error!("Missing OriginalUri extension");
            axum::response::Response::builder()
                .status(500)
                .body(axum::body::Body::from(
                    "Internal Server Error: Missing OriginalUri",
                ))
        }).unwrap();

    let body = req.into_body();
    
    // Pass the OriginalUri struct
    proxy_request(method, original_uri, body, state.get_config())
        .await
        .map_err(|err| {
            tracing::error!("Proxy request failed: {}", err); // Add tracing for proxy errors
            tracing::error!("Proxy request failed: {}", err); // Add tracing for proxy errors
            axum::response::Response::builder()
                .status(500)
                .body(axum::body::Body::from(format!(
                    "Internal Server Error: {}",
                    err
                )))
                .unwrap()
        })
}
