from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from models import MCPFunctionCall
from api import send_email, get_conversation, get_stats

router = APIRouter(prefix="/mcp", tags=["MCP"])

MCP_MANIFEST = {
    "schema_version": "v1",
    "id": "email-gateway",
    "name": "Simple Email Gateway",
    "description": "Send and receive emails with tracking capabilities.",
    "auth": {"type": "none"},
    "api": {"type": "openapi", "url": "/openapi.json"},
    "functions": [
        {
            "name": "send_email",
            "description": "Send an email with tracking",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string", "format": "email"},
                    "subject": {"type": "string"},
                    "body": {"type": "string"},
                },
                "required": ["to", "subject", "body"]
            }
        },
        {
            "name": "get_conversation",
            "description": "Get message history with a specific email address",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "format": "email"},
                },
                "required": ["email"]
            }
        },
        {
            "name": "get_events",
            "description": "Get all email open/click events",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    ]
}

@router.post("/call", summary="MCP function invocation")
async def mcp_call(request: Request):
    payload = await request.json()
    try:
        function_call = MCPFunctionCall(**payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid request: {e}")

    FUNCTION_MAP = {
        "send_email": send_email,
        "get_conversation": get_conversation,
        "get_events": get_stats
    }

    func = FUNCTION_MAP.get(function_call.name)
    if not func:
        raise HTTPException(status_code=404, detail=f"Function '{function_call.name}' not found.")

    result = await func(**function_call.arguments)
    return JSONResponse(content={"result": result})