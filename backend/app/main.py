from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import traceback
from app.db_config import init_db
from app.api import auth
from app.database import document
from app.core import EDA
from app.core import clean
from app.core import visualize
app = FastAPI(
    title="Data Analysis: v1",
    description="Made by Yassine",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="")
app.include_router(document.router, prefix="/api")
app.include_router(EDA.router)
app.include_router(clean.router)
app.include_router(visualize.router)


@app.get("/health")
async def health_check():
    health_status = {
        "status": "healthy",
        "service": "Data Analysis API.",
        "version": "1.0.0"
    }
    return health_status

@app.get("/")
async def root():
    root_info = {
        "message": "Data Analysis API is running",
        "docs": "/docs",
        "health": "/health"
    }
    return root_info

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"Uncaught exception: {exc}")
    print(traceback.format_exc())
    
    error_response = {
        "detail": "Internal server error",
        "type": type(exc).__name__
    }
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response
    )

@app.on_event("startup")
async def startup():
     await init_db()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    
    for error in exc.errors():
        error_detail = {
            "loc": error["loc"],
            "msg": error["msg"],
            "type": error["type"]
        }
        errors.append(error_detail)
    
    response_content = {
        "detail": "Validation error",
        "errors": errors
    }
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response_content
    ) 