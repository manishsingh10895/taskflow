use crate::config::GatewayConfig;
use crate::router::match_service;
use axum::{body::Body, extract::OriginalUri, http::Method, response::Response};
use rand::seq::{IndexedRandom, SliceRandom};
use reqwest::Client;
use std::sync::Arc;

pub async fn proxy_request(
    method: Method,
    uri: OriginalUri,
    body: Body,
    config: Arc<GatewayConfig>,
) -> Result<Response, axum::Error> {
    let path = uri.path();

    if let Some(service_name) = match_service(path, &config) {
        let service = config.services.get(&service_name).unwrap();
        let current_target = {
            let mut targets = service.targets.clone();
            let mut rng = rand::rng();
            targets.shuffle(&mut rng);

            targets.pop().unwrap_or_default()
        };

        let url = format!("{}{}", current_target, path);

        let client = Client::new();
        let body_stream = reqwest::Body::wrap_stream(body.into_data_stream());
        let request = client
            .request(method, &url)
            .body(body_stream)
            .build()
            .unwrap();

        let res = client.execute(request).await.unwrap();

        let status = res.status();
        let headers = res.headers().clone();
        let body_bytes = res.bytes().await.unwrap();

        let mut response = axum::response::Response::builder()
            .status(status)
            .body(body_bytes.into())
            .unwrap();

        for (key, value) in headers.iter() {
            response.headers_mut().insert(key, value.clone());
        }
        // Set the original request URI in the response headers
        response
            .headers_mut()
            .insert("X-Original-URI", format!("{}", url).parse().unwrap());

        return Ok(response);
    } else {
        // If no service matches, return a BAD GATEWAY response
        return Ok(Response::builder()
            .status(502)
            .body("Bad Gateway".into())
            .unwrap());
    }
}
