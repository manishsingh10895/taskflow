use sqlx::PgPool;
pub mod task_model;
use self::task::task_service_server::TaskServiceServer;
use tonic::{transport::Server, Request, Response, Status};
use task::task_service_server::TaskService;
pub struct TFTaskService {
    db: PgPool,
}

pub mod task {
    tonic::include_proto!("task");
}

impl TFTaskService {
    pub fn new(db: PgPool) -> Self {
        TFTaskService { db }
    }
}

const GRPC_ADDRESS: &str = "[::1]:50052";

#[tonic::async_trait]
impl TaskService for TFTaskService {
    async fn get_tasks_for_user_project(
        &self, 
        request: Request<self::task::GetTasksForUserProjectRequest>,
    ) -> Result<Response<self::task::GetTasksForUserProjectResponse>, Status> {
        let inner_request = request.into_inner();
         let user_id = inner_request.user_id;
            let project_id = inner_request.project_id;

       let rows = sqlx::query!(
           "SELECT id, title, description, completed FROM tasks WHERE user_id = $1 AND project_id = $2",
           user_id,
           project_id
       ).fetch_all(&self.db) 
         .await;

         let tasks = rows.map(|rows| {
              rows.into_iter().map(|row| {
                self::task::Task {
                     id: row.id,
                     project_id: Some(project_id),
                     title: row.title.unwrap_or(String::new()),
                     description: row.description.unwrap_or(String::new()),
                     completed: row.completed.unwrap_or(false),
                     user_id,
                }
              }).collect()
            });

        return match tasks {
            Ok(tasks) => Ok(Response::new(self::task::GetTasksForUserProjectResponse { tasks })),
            Err(e) => Err(Status::internal(format!("Internal server error: {}", e))),
        };
    }

    async fn get_tasks_for_project(
        &self,
        request: Request<self::task::GetProjectTasksRequest>
    ) -> Result<Response<self::task::GetProjectTasksResponse>, Status> {
        let project_id = request.into_inner().project_id;

        let rows = sqlx::query!(
            "SELECT id, title, description, completed, user_id FROM tasks WHERE project_id = $1",
            project_id
        ).fetch_all(&self.db)
        .await
        .map_err(|e| match e {
            sqlx::Error::RowNotFound => Status::not_found("Project not found"),
            _ => Status::internal("Internal server error"),
        });

        let tasks = rows.map(|rows| {
            rows.into_iter().map(|row| {
                self::task::Task {
                    id: row.id,
                    project_id: Some(project_id),
                    title: row.title.unwrap_or(String::new()),
                    description: row.description.unwrap_or(String::new()),
                    completed: row.completed.unwrap_or(false),
                    user_id: row.user_id.unwrap_or(0),
                }
            }).collect()
        });

        return match tasks {
            Ok(tasks) => Ok(Response::new(self::task::GetProjectTasksResponse { tasks })),
            Err(e) => Err(e),
        };
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    dotenv::dotenv().ok();
    let db_url = std::env::var("DATABASE_URL").expect("DATABASE_URL must be set");
    let addr: std::net::SocketAddr = GRPC_ADDRESS.parse()?;
    let db_pool = PgPool::connect(&db_url).await?;
    let task_service = TFTaskService::new(db_pool); 

    Server::builder()
        .add_service(TaskServiceServer::new(task_service))
        .serve(addr)
        .await?;
    println!("gRPC server listening on {}", GRPC_ADDRESS);
    Ok(())
}
