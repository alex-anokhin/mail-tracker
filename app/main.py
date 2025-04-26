from fastapi import FastAPI
from fastapi.responses import JSONResponse
from api import router as api_router
from mcp import router as mcp_router, MCP_MANIFEST
from db import init_db

app = FastAPI(
    title="📨 FastAPI Email Gateway with MCP tool support",
    description="Send emails with open/click tracking, store metrics, and view basic stats — all self-hosted.",
    version="1.0.0"
)

init_db()

app.include_router(api_router)
app.include_router(mcp_router)

@app.get("/", summary="🏠 Home", description="Welcome to the FastAPI Email Tracker!")
def read_root():
    return {"message": "Welcome to the FastAPI Email Tracker!"}

@app.get("/.well-known/mcp.json", summary="MCP Manifest", description="Manifest for MCP tool integration.")
async def mcp_manifest_root():
    return JSONResponse(content=MCP_MANIFEST)