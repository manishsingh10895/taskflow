use crate::config::GatewayConfig;

/// This function matches the incoming request path with the configured service paths
/// and returns the name of the service if a match is found.
/// 
/// # Arguments
/// 
/// * `path` - The request path to match.
/// * `config` - The configuration containing the service paths.
/// # Returns
/// 
/// * `Option<String>` - The name of the matched service, or `None` if no match is found.
///
/// # Example
/// 
/// ```
/// use crate::router::match_service;
/// use crate::config::GatewayConfig;
/// 
/// let config = GatewayConfig {
///    services: HashMap::new(),
/// };
/// 
/// let path = "/auth/login";
/// 
/// let matched_service = match_service(path, &config);
/// 
/// assert_eq!(matched_service, Some("auth".to_string()));
/// ```
pub fn match_service(path: &str, config: &GatewayConfig) -> Option<String> {
    for (name, service) in &config.services {
        if path.starts_with(&service.path_prefix) {
            return Some(name.clone());
        }
    }
    None
}
