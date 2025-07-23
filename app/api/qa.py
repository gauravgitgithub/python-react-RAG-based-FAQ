from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.schemas.document import QuestionRequest, AnswerResponse
from app.services.qa_service import QAService

router = APIRouter(prefix="/qa", tags=["question-answering"])


@router.post("/ask", response_model=AnswerResponse)
async def ask_question(
    question_request: QuestionRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Ask a question and get an answer using RAG"""
    qa_service = QAService(db)
    return await qa_service.answer_question(question_request)


@router.get("/stats")
async def get_qa_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get Q&A system statistics"""
    qa_service = QAService(db)
    return await qa_service.get_qa_stats() 