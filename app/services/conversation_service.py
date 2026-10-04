from typing import Any


MAX_RESULT_ROWS = 20


class ConversationState:
    def __init__(self):
        self.messages: list[dict[str, Any]] = []

    def add_message(
        self,
        question: str,
        sql: str,
        result: dict[str, Any],
    ):
        result_snapshot = {
            "columns": result.get("columns", []),
            "rows": result.get("rows", [])[:MAX_RESULT_ROWS],
            "row_count": result.get("row_count", 0),
        }

        self.messages.append({
            "question": question,
            "sql": sql,
            "result": result_snapshot,
        })

    def get_recent_messages(self, limit: int = 5):
        return self.messages[-limit:]

    def clear(self):
        self.messages.clear()


conversation_state = ConversationState()