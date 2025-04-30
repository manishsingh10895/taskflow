use dotenvy::dotenv;
use serde::Deserialize;
use serde_json::json;
use std::collections::HashMap;
use std::env;
#[derive(Debug, Deserialize, Clone)]
pub struct GatewayConfig {
    pub addr: String,
    pub services: HashMap<String, ServiceConfig>,
}

#[derive(Debug, Deserialize, Clone)]
pub struct ServiceConfig {
    pub path_prefix: String,
    pub targets: Vec<String>,
}

impl GatewayConfig {
    pub fn from_env() -> Self {
        let mut services = HashMap::new();
        dotenv().ok();

        let env_map = HashMap::from([
            (
                "auth",
                json!({
                    "path_prefix": "/auth",
                    "targets": ["http://localhost:8080"]
                }),
            ),
            (
                "user",
                json!({
                    "path_prefix": "/user",
                    "targets": ["http://localhost:8081"]
                }),
            ),
            (
                "order",
                json!({
                    "path_prefix": "/order",
                    "targets": ["http://localhost:8082"]
                }),
            ),
        ]);

        for (key, value) in env_map {
            let path_prefix = value["path_prefix"]
                .as_str()
                .unwrap_or_default()
                .to_string();
            let targets = value["targets"]
                .as_array()
                .unwrap_or(&vec![])
                .iter()
                .filter_map(|t| t.as_str())
                .map(|t| t.to_string())
                .collect();

            services.insert(
                key.to_string(),
                ServiceConfig {
                    path_prefix,
                    targets,
                },
            );
        }

        let addr = env::var("GATEWAY_ADDR").unwrap_or_else(|_| "http://localhost:4004".to_string());

        GatewayConfig { services, addr }
    }
}
