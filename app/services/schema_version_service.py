import hashlib
import json

from sqlalchemy import select

from app.database.app_connection import AppSessionLocal
from app.database.introspector import get_database_schema
from app.database.models import DatabaseConnection, SchemaVersion


def build_schema_snapshot(
    database_connection: DatabaseConnection,
) -> dict:
    return get_database_schema(
        database_connection
    )


def calculate_schema_hash(
    schema: dict,
) -> str:
    normalized_schema = json.dumps(
        schema,
        sort_keys=True,
        default=str,
        separators=(",", ":"),
    )

    return hashlib.sha256(
        normalized_schema.encode("utf-8")
    ).hexdigest()


def get_latest_schema_version(
    connection_id: int,
):
    db = AppSessionLocal()

    try:
        return db.scalar(
            select(SchemaVersion)
            .where(
                SchemaVersion.connection_id
                == connection_id
            )
            .order_by(
                SchemaVersion.created_at.desc(),
                SchemaVersion.schema_version_id.desc(),
            )
            .limit(1)
        )

    finally:
        db.close()


def create_schema_version(
    connection_id: int,
    schema: dict,
    version_hash: str,
):
    db = AppSessionLocal()

    try:
        version = SchemaVersion(
            connection_id=connection_id,
            version_hash=version_hash,
            schema_json=json.dumps(
                schema,
                default=str,
            ),
        )

        db.add(version)
        db.commit()
        db.refresh(version)

        return version

    finally:
        db.close()


def check_schema_changed(
    database_connection: DatabaseConnection,
) -> tuple[bool, dict, str]:
    schema = build_schema_snapshot(
        database_connection
    )

    version_hash = calculate_schema_hash(
        schema
    )

    latest = get_latest_schema_version(
        database_connection.connection_id
    )

    if latest is None:
        return True, schema, version_hash

    return (
        latest.version_hash != version_hash,
        schema,
        version_hash,
    )


def sync_schema_version(
    database_connection: DatabaseConnection,
):
    changed, schema, version_hash = check_schema_changed(
        database_connection
    )

    if not changed:
        latest = get_latest_schema_version(
            database_connection.connection_id
        )

        return {
            "changed": False,
            "version": latest,
            "schema": schema,
            "version_hash": version_hash,
            "indexed_documents": None,
        }

    # Import the embedding/indexing stack only when
    # the schema actually needs to be reindexed.
    from app.rag.indexer import index_schema

    indexed_documents = index_schema(
        database_connection,
        rebuild=True,
    )

    version = create_schema_version(
        connection_id=database_connection.connection_id,
        schema=schema,
        version_hash=version_hash,
    )

    return {
        "changed": True,
        "version": version,
        "schema": schema,
        "version_hash": version_hash,
        "indexed_documents": indexed_documents,
    }