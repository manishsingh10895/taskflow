import uvicorn
from fastapi import FastAPI

from main import app as main_app

if __name__ == "__main__":
    uvicorn.run(main_app, host="0.0.0.0", port=4003)
