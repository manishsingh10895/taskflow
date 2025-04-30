#[derive(sqlx::FromRow)]
struct User {
    id: u32,
    username: String,
    email: String,
}

#[derive(sqlx::FromRow)]
struct UserProfile {
    user_id: u32,
    avatar: String,
}
