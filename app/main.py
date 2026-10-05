from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.api.auth import router as auth_router
from app.api_schema import router as schema_router
from app.services.query_service import process_query


app = FastAPI(
    title="Natural Language to SQL",
    description="AI-powered natural language interface for MySQL databases",
    version="0.1.0"
)

templates = Jinja2Templates(directory="templates")

app.include_router(schema_router)
app.include_router(auth_router)


class QueryRequest(BaseModel):
    question: str


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="query.html",
        context={}
    )


@app.post("/query")
def query_database(request: QueryRequest):
    try:
        return process_query(request.question)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Query processing failed: {error}"
        )