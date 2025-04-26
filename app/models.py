from pydantic import BaseModel, EmailStr

class EmailRequest(BaseModel):
    to: EmailStr
    subject: str
    body: str

class EventResponse(BaseModel):
    email_id: str
    event: str
    url: str | None
    timestamp: str

class EmailResponse(BaseModel):
    email_id: str
    direction: str
    from_addr: str
    to_addr: str
    subject: str
    body: str
    sent_at: str

class MCPFunctionCall(BaseModel):
    name: str
    arguments: dict