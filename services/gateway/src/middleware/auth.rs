use axum::http::StatusCode;
use axum::{http::Request, middleware::Next, response::Response, body::Body};
use jsonwebtoken::{DecodingKey, Validation};
use serde::{Deserialize, Serialize};
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct Claims {
    pub sub: String,
    pub exp: usize,
}

pub async fn auth_middleware(
    req: Request<Body>,
    next: Next,
) -> Result<Response<Body>, (StatusCode, String)>  {
    if let Some(auth_header) = req.headers().get("Authorization") {
        if let Ok(auth_str) = auth_header.to_str() {
            if auth_str.starts_with("Bearer ") {
                let token = &auth_str[7..];

                let secret =
                    std::env::var("JWT_SECRET").unwrap_or_else(|_| "supersecret".to_string());

                let decoded = jsonwebtoken::decode::<Claims>(
                    token,
                    &DecodingKey::from_secret(secret.as_ref()),
                    &Validation::default(),
                );

                match decoded {
                    Ok(claims) => {
                        // Token is valid, proceed with the request
                        println!("Token is valid: {:?}", claims);
                        return Ok(next.run(req).await);
                    }
                    Err(_) => {
                        // Token is invalid, return 401 Unauthorized
                        return Err((StatusCode::UNAUTHORIZED, "Invalid token".to_string()));
                    }
                }
            } else {
                // Invalid authorization scheme
                return Err((
                    StatusCode::UNAUTHORIZED,
                    "Invalid authorization scheme".to_string(),
                ));
            }
        }
        // No authorization header present
    }

    return Err((
        StatusCode::UNAUTHORIZED,
        "Missing authorization header".to_string(),
    ));
}
