from main import app
import uvicorn
import threading
from consumer import consume_task_created, consume_task_deleted

if __name__ == "__main__":
    threading.Thread(target=consume_task_created).start()
    threading.Thread(target=consume_task_deleted).start()
    uvicorn.run(app, host="0.0.0.0", port=4002)
