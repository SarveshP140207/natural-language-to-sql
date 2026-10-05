import json
from datetime import datetime

from sqlalchemy import select

from app.database.app_connection import AppSessionLocal
from app.database.models import BusinessRule, DatabaseConnection


def _decode_list(value: str) -> list[str]:
    try:
        decoded = json.loads(value)

        if isinstance(decoded, list):
            return [str(item) for item in decoded]

    except (json.JSONDecodeError, TypeError):
        pass

    return [
        item.strip()
        for item in value.split(",")
        if item.strip()
    ]


def _encode_list(values: list[str]) -> str:
    return json.dumps(values)


def create_business_rule(
    user_id: int,
    connection_id: int,
    title: str,
    description: str,
    table_names: list[str],
    column_names: list[str],
):
    db = AppSessionLocal()

    try:
        connection = db.scalar(
            select(DatabaseConnection).where(
                (DatabaseConnection.connection_id == connection_id)
                & (DatabaseConnection.user_id == user_id)
            )
        )

        if not connection:
            raise ValueError(
                "Database connection not found."
            )

        existing = db.scalar(
            select(BusinessRule).where(
                (BusinessRule.connection_id == connection_id)
                & (BusinessRule.title == title)
            )
        )

        if existing:
            raise ValueError(
                "A business rule with this title already exists."
            )

        rule = BusinessRule(
            connection_id=connection_id,
            title=title,
            description=description,
            table_names=_encode_list(table_names),
            column_names=_encode_list(column_names),
        )

        db.add(rule)
        db.commit()
        db.refresh(rule)

        return rule

    finally:
        db.close()


def get_user_business_rules(
    user_id: int,
    connection_id: int | None = None,
):
    db = AppSessionLocal()

    try:
        statement = (
            select(BusinessRule)
            .join(
                DatabaseConnection,
                BusinessRule.connection_id
                == DatabaseConnection.connection_id,
            )
            .where(
                DatabaseConnection.user_id == user_id
            )
            .order_by(
                BusinessRule.created_at.desc()
            )
        )

        if connection_id is not None:
            statement = statement.where(
                BusinessRule.connection_id == connection_id
            )

        return db.scalars(statement).all()

    finally:
        db.close()


def get_connection_business_rules(
    connection_id: int,
):
    db = AppSessionLocal()

    try:
        return db.scalars(
            select(BusinessRule)
            .where(
                BusinessRule.connection_id == connection_id
            )
            .order_by(
                BusinessRule.created_at.asc()
            )
        ).all()

    finally:
        db.close()


def get_user_business_rule(
    user_id: int,
    rule_id: int,
):
    db = AppSessionLocal()

    try:
        return db.scalar(
            select(BusinessRule)
            .join(
                DatabaseConnection,
                BusinessRule.connection_id
                == DatabaseConnection.connection_id,
            )
            .where(
                (BusinessRule.rule_id == rule_id)
                & (DatabaseConnection.user_id == user_id)
            )
        )

    finally:
        db.close()


def update_business_rule(
    user_id: int,
    rule_id: int,
    title: str,
    description: str,
    table_names: list[str],
    column_names: list[str],
):
    db = AppSessionLocal()

    try:
        rule = db.scalar(
            select(BusinessRule)
            .join(
                DatabaseConnection,
                BusinessRule.connection_id
                == DatabaseConnection.connection_id,
            )
            .where(
                (BusinessRule.rule_id == rule_id)
                & (DatabaseConnection.user_id == user_id)
            )
        )

        if not rule:
            return None

        duplicate = db.scalar(
            select(BusinessRule).where(
                (BusinessRule.connection_id == rule.connection_id)
                & (BusinessRule.title == title)
                & (BusinessRule.rule_id != rule_id)
            )
        )

        if duplicate:
            raise ValueError(
                "A business rule with this title already exists."
            )

        rule.title = title
        rule.description = description
        rule.table_names = _encode_list(table_names)
        rule.column_names = _encode_list(column_names)
        rule.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(rule)

        return rule

    finally:
        db.close()


def delete_business_rule(
    user_id: int,
    rule_id: int,
) -> bool:
    db = AppSessionLocal()

    try:
        rule = db.scalar(
            select(BusinessRule)
            .join(
                DatabaseConnection,
                BusinessRule.connection_id
                == DatabaseConnection.connection_id,
            )
            .where(
                (BusinessRule.rule_id == rule_id)
                & (DatabaseConnection.user_id == user_id)
            )
        )

        if not rule:
            return False

        db.delete(rule)
        db.commit()

        return True

    finally:
        db.close()


def serialize_business_rule(
    rule: BusinessRule,
) -> dict:
    return {
        "rule_id": rule.rule_id,
        "connection_id": rule.connection_id,
        "title": rule.title,
        "description": rule.description,
        "table_names": _decode_list(
            rule.table_names
        ),
        "column_names": _decode_list(
            rule.column_names
        ),
        "created_at": rule.created_at,
        "updated_at": rule.updated_at,
    }