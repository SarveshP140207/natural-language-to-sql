from typing import Any


class ConversationState:
    def __init__(self):
        self.messages: list[dict[str, Any]] = []

    def add_message(
        self,
        question: str,
        sql: str,
        result: dict[str, Any],
    ):
        self.messages.append({
            "question": question,
            "sql": sql,
            "result": result,
        })

    def get_recent_messages(self, limit: int = 5):
        return self.messages[-limit:]

    def clear(self):
        self.messages.clear()


conversation_state = ConversationState()