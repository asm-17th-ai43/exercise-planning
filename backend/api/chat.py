"""/agent/chat SSE 라우터. B(박장우) ↔ C(이유준) 합의로 구현."""
from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse

from schemas.models import ChatRequest

router = APIRouter()


@router.post("/chat")
async def chat(request: ChatRequest) -> EventSourceResponse:
    """ChatChunk(JSON) 시퀀스를 SSE로 스트리밍.

    type ∈ {"text", "tool_call", "proposal", "done", "error"}.
    """
    raise HTTPException(status_code=501, detail="not implemented")
