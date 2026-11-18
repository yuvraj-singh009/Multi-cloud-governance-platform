from fastapi import FastAPI

app = FastAPI(
    title="Cloud Governance Scanner",
    description="Cloud resource discovery and governance API",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "Cloud Governance Scanner is running",
        "status": "healthy"
    }


@app.get("/health")
def health():
    return {
        "service": "scanner-service",
        "status": "healthy"
    }