"""FastAPI 应用入口：CORS、路由注册、全局异常处理。"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routers import anomaly

app = FastAPI(title="气象气温距平分析 API", version="1.0.0")

# 允许前端开发服务器跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(anomaly.router)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """统一异常处理：返回 {success:false, message}。"""
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": f"服务器内部错误: {exc}"},
    )