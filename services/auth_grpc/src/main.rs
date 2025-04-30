use self::auth::{
    auth_service_server::{AuthService, AuthServiceServer},
    DeleteUserResponse, UserRequest, UserResponse,
};
use sqlx::PgPool;
use std::env;
use tonic::{transport::Server, Request, Response, Status};
pub mod auth {
    tonic::include_proto!("auth");
}

pub mod user;

pub struct TFAuthService {
    db: PgPool,
}

impl TFAuthService {
    pub fn new(db: PgPool) -> Self {
        TFAuthService { db }
    }
}

const GRPC_ADDRESS: &str = "[::1]:50051";

#[tonic::async_trait]
impl AuthService for TFAuthService {
    async fn get_user_info(
        &self,
        request: Request<UserRequest>,
    ) -> Result<Response<UserResponse>, Status> {
        let user_id = request.into_inner().user_id;

        let row = sqlx::query!(
            "SELECT id, email, username FROM users where id = $1",
            user_id
        )
        .fetch_one(&self.db)
        .await
        .map_err(|e| match e {
            sqlx::Error::RowNotFound => tonic::Status::not_found("User not found"),
            _ => tonic::Status::internal(format!("Database error: {}", e)),
        })?;

        let reply = tonic::Response::new(UserResponse {
            user_id: row.id,
            email: row.email,
            username: row.username,
        });

        Ok(reply)
    }

    async fn delete_user(
        &self,
        request: Request<UserRequest>,
    ) -> Result<Response<DeleteUserResponse>, Status> {
        let user_id = request.into_inner().user_id;

        sqlx::query!("DELETE FROM users WHERE id = $1", user_id)
            .execute(&self.db)
            .await
            .map_err(|e| match e {
                sqlx::Error::RowNotFound => tonic::Status::not_found("User not found"),
                _ => tonic::Status::internal(format!("Database error: {}", e)),
            })?;

        let reply = tonic::Response::new(DeleteUserResponse {
            success: true,
            message: "User deleted successfully".to_string(),
        });

        Ok(reply)
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    dotenv::dotenv().ok();
    let addr = GRPC_ADDRESS.parse()?;
    let db_url = env::var("DATABASE_URL")?;
    let db_pool = PgPool::connect(&db_url).await?;
    let auth_service = TFAuthService::new(db_pool);

    println!("Server listening on {}", addr);

    Server::builder()
        .add_service(AuthServiceServer::new(auth_service))
        .serve(addr)
        .await?;

    Ok(())
}
