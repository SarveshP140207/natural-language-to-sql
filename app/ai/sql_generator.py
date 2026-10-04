from app.ai.llm import generate_response
from app.ai.prompts import build_sql_prompt
from app.database.introspector import get_database_schema
from app.rag.retriever import retrieve_schema_context
from app.validation.sql_cleaner import clean_sql_response


def generate_sql(
    question: str,
    conversation_context: str = ""
) -> str:
    schema = get_database_schema()

    retrieved_documents = retrieve_schema_context(
        question,
        top_k=5
    )

    rag_context = "\n\n".join(
        document["content"]
        for document in retrieved_documents
    )

    prompt = build_sql_prompt(
        schema=schema,
        question=question,
        rag_context=rag_context,
        conversation_context=conversation_context
    )

    response = generate_response(prompt)

    return clean_sql_response(response)