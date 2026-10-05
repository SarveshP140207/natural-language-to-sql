from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from app.api.auth import router as auth_router
from app.api.business_rule import router as business_rule_router
from app.api.conversation import router as conversation_router
from app.api.database import router as database_router
from app.api.history import router as history_router
from app.api_schema import router as schema_router
from app.core.dependencies import get_current_user
from app.database.models import User
from app.services.connection_service import get_user_connection
from app.services.conversation_service import (
    create_conversation,
    get_user_conversation,
)
from app.services.history_service import save_query_history
from app.services.query_service import process_query


app = FastAPI(
    title="Natural Language to SQL",
    description="AI-powered natural language interface for MySQL databases",
    version="0.1.0"
)

templates = Jinja2Templates(directory="templates")

app.include_router(schema_router)
app.include_router(auth_router)
app.include_router(database_router)
app.include_router(history_router)
app.include_router(conversation_router)
app.include_router(business_rule_router)


class QueryRequest(BaseModel):
    question: str = Field(min_length=1)
    connection_id: int = Field(gt=0)
    conversation_id: int | None = Field(default=None, gt=0)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="query.html",
        context={}
    )


@app.post("/query")
def query_database(
    request: QueryRequest,
    current_user: User = Depends(get_current_user),
):
    connection = get_user_connection(
        user_id=current_user.user_id,
        connection_id=request.connection_id,
    )

    if not connection:
        raise HTTPException(
            status_code=404,
            detail="Database connection not found.",
        )

    if request.conversation_id is not None:
        conversation = get_user_conversation(
            user_id=current_user.user_id,
            conversation_id=request.conversation_id,
        )

        if not conversation:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found.",
            )

        if conversation.connection_id != connection.connection_id:
            raise HTTPException(
                status_code=400,
                detail="Conversation belongs to a different database connection.",
            )

    else:
        conversation = create_conversation(
            user_id=current_user.user_id,
            connection_id=connection.connection_id,
            title=request.question[:255],
        )

    try:
        result = process_query(
            question=request.question,
            database_connection=connection,
            user_id=current_user.user_id,
            conversation_id=conversation.conversation_id,
        )

        history = save_query_history(
            user_id=current_user.user_id,
            connection_id=connection.connection_id,
            question=request.question,
            sql_query=result["sql"],
            result=result["result"],
            execution_time_ms=result["execution_time_ms"],
        )

        result["history_id"] = history.history_id
        result["conversation_id"] = conversation.conversation_id

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Query processing failed: {error}",
        )