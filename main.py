# pyrefly: ignore [missing-import]
from fastapi import FastAPI
from api.routes import router

app = FastAPI(
    title="Cloud Support",
    version="1.0.0"
)

app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Cloud Support API"}

@app.get("/api/v1/health")
def health_check():
    return {"status": "healthy"}

