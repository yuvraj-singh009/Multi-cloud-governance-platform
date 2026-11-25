from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.scan import router as scan_router
from app.api.resources import router as resource_router
from fastapi.middleware.cors import CORSMiddleware





app = FastAPI(
    title="Cloud Governance Platform",
    description="Cloud resource discovery and governance API",
    version="1.0.0"
)


origins = [
    "https://cloud-governance-platform.vercel.app",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():

    return {
        "message": "Cloud Governance Platform API",
        "status": "running"
    }


@app.get("/health")
def health():

    return {
        "service": "scanner-service",
        "status": "healthy"
    }




app.include_router(scan_router)
app.include_router(resource_router)