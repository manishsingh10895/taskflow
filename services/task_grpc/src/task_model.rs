#[derive(sqlx::FromRow)]
struct Task {
    id: u32,
    name: String,
    description: String,
    completed: bool,
    user_id: u32,
    project_id: Option<u32>,
}
