from fastapi import FastAPI

from app.api_schema import router as schema_router


app = FastAPI(
    title="Natural Language to SQL",
    description="AI-powered natural language interface for MySQL databases",
    version="0.1.0"
)


app.include_router(schema_router)


@app.get("/")
def root():
    return {
        "message": "Natural Language to SQL API is running",
        "status": "ok"
    }