"""
Main application entry point
"""
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from contextlib import asynccontextmanager
import secrets

from app.core.config import settings
from app.core.database import Base
from app.core.exceptions import AppError
from app.api.v1 import api_router
from app.utils.response import APIResponse


# BasicAuth for Swagger
security = HTTPBasic()


def verify_swagger_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """Verify Swagger documentation credentials"""
    correct_username = secrets.compare_digest(
        credentials.username, settings.SWAGGER_USERNAME
    )
    correct_password = secrets.compare_digest(
        credentials.password, settings.SWAGGER_PASSWORD
    )
    
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting up...")
    yield
    # Shutdown
    print("👋 Shutting down...")


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url=None,  # Disable default docs
    redoc_url=None,  # Disable default redoc
    lifespan=lifespan
)


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global domain exception handler — translates AppError subclasses to JSON
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=APIResponse.error(message=exc.message, status=exc.status_code),
    )


# Protected Swagger documentation
@app.get("/docs", include_in_schema=False)
async def get_documentation(username: str = Depends(verify_swagger_credentials)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="API Docs")


@app.get("/openapi.json", include_in_schema=False)
async def openapi(username: str = Depends(verify_swagger_credentials)):
    return get_openapi(title=settings.APP_NAME, version=settings.APP_VERSION, routes=app.routes)


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "success": True,
        "status": 200,
        "message": "Application is running",
        "data": {
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.APP_ENV
        }
    }


# Include API routes
app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
