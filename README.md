\# Natural Language to SQL



An AI-powered system that allows users to query a MySQL database using natural language.



\## Overview



The system converts natural-language questions into SQL, validates the generated SQL for correctness and security, executes safe read-only queries against MySQL, and presents the results in an understandable format.



Example:



> Which 10 products generated the highest revenue?



The system processes the question through intent analysis, schema retrieval, SQL generation, SQL validation, database execution, and result analysis.



\## Main Features



\- Natural language to SQL

\- Automatic database schema introspection

\- RAG-based schema retrieval

\- SQL validation and security checks

\- Read-only query execution

\- SQL error repair

\- Conversational follow-up queries

\- Query history

\- Natural-language result explanations

\- Data visualization

\- Authentication

\- Schema viewer



\## Technology Stack



\- Python

\- FastAPI

\- MySQL

\- SQLAlchemy

\- OpenAI API

\- Qdrant

\- SQLGlot

\- Jinja2

\- HTMX

\- Plotly

\- pytest

\- Docker



\## Project Status



Currently under development.



The system is being developed incrementally, starting with the backend foundation and database integration.



\## Security



Generated SQL is never executed directly.



Every generated query must pass SQL parsing, security validation, schema validation, and query-limit checks before execution.



The initial system operates in read-only mode.



\## Development



The project uses a Python virtual environment:



```text

.venv/

