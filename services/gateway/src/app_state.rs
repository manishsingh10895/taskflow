use std::sync::Arc;

use crate::config::GatewayConfig;

#[derive(Clone)]
pub struct AppState {
    pub config: Arc<GatewayConfig>,
}

impl AppState {
    pub fn new(config: GatewayConfig) -> Self {
        AppState {
            config: Arc::new(config),
        }
    }

    pub fn get_config(&self) -> Arc<GatewayConfig> {
        self.config.clone()
    }
}
