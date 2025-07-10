from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from resumix.backend.controller.agent_controller import router as agent_router
from resumix.backend.controller.score_controller import router as score_router
import uvicorn

app = FastAPI()

# CORS允许跨源请求（如Streamlit前端请求FastAPI）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 或限制为 ["http://localhost:8501"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agent_router)
app.include_router(score_router)


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000)
