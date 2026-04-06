import logging
import os
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4


DEFAULT_COLLECTION_NAME = "request_metadata"
DEFAULT_MODEL_NAME = "gpt-4o-mini"
EXCLUDED_CONTENT_FIELDS = {"query", "answer", "answer_markdown", "context"}
logger = logging.getLogger(__name__)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def generate_request_id() -> str:
    return f"req_{uuid4().hex}"


def build_metadata_record(
    user_id: str,
    role: str,
    route_path: str,
    request_id: Optional[str] = None,
    session_id: Optional[str] = None,
    response_status: str = "success",
    model_name: str = DEFAULT_MODEL_NAME,
    timestamp: Optional[datetime] = None,
    workflow_mode: Optional[str] = None,
    decision_status: Optional[str] = None,
) -> dict[str, Any]:
    record = {
        "request_id": request_id or generate_request_id(),
        "session_id": session_id,
        "user_id": user_id,
        "role": role,
        "timestamp": (timestamp or datetime.now(timezone.utc)).isoformat(),
        "response_status": response_status,
        "route_path": route_path,
        "model_name": model_name,
        "workflow_mode": workflow_mode,
        "decision_status": decision_status,
    }

    for field in EXCLUDED_CONTENT_FIELDS:
        record.pop(field, None)

    return record


class MetadataStore:
    def __init__(self, client: Any, collection_name: str = DEFAULT_COLLECTION_NAME):
        self.client = client
        self.collection_name = collection_name

    def _collection(self):
        return self.client.collection(self.collection_name)

    def save_record(self, record: dict[str, Any]) -> dict[str, Any]:
        self._collection().document(record["request_id"]).set(record)
        return record

    def get_records_by_session(self, session_id: str, limit: int = 50) -> list[dict[str, Any]]:
        query = (
            self._collection()
            .where("session_id", "==", session_id)
            .order_by("timestamp", direction=_descending_direction())
            .limit(limit)
        )
        return [snapshot.to_dict() for snapshot in query.stream()]

    def list_recent_records(self, limit: int = 50) -> list[dict[str, Any]]:
        query = (
            self._collection()
            .order_by("timestamp", direction=_descending_direction())
            .limit(limit)
        )
        return [snapshot.to_dict() for snapshot in query.stream()]


def _descending_direction():
    try:
        from google.cloud.firestore import Query

        return Query.DESCENDING
    except Exception:
        return "DESCENDING"


def resolve_firestore_project_id() -> Optional[str]:
    return (
        os.environ.get("FIRESTORE_PROJECT_ID")
        or os.environ.get("GCP_PROJECT_ID")
        or os.environ.get("GOOGLE_CLOUD_PROJECT")
    )


def create_firestore_client():
    from google.cloud import firestore

    project_id = resolve_firestore_project_id()
    database_id = os.environ.get("FIRESTORE_DATABASE_ID")
    if database_id:
        return firestore.Client(project=project_id, database=database_id)
    return firestore.Client(project=project_id)


def get_metadata_store_from_env() -> Optional[MetadataStore]:
    if os.environ.get("METADATA_STORE_ENABLED", "true").lower() in {"0", "false", "no"}:
        logger.info("Metadata store disabled by METADATA_STORE_ENABLED")
        return None

    try:
        client = create_firestore_client()
    except Exception as exc:
        logger.warning(
            "Metadata store unavailable. Firestore client creation failed. "
            "Resolved project id=%r, FIRESTORE_DATABASE_ID=%r, GOOGLE_APPLICATION_CREDENTIALS_set=%s. Error=%s",
            resolve_firestore_project_id(),
            os.environ.get("FIRESTORE_DATABASE_ID"),
            bool(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")),
            exc,
        )
        return None

    collection_name = os.environ.get("FIRESTORE_METADATA_COLLECTION", DEFAULT_COLLECTION_NAME)
    logger.info(
        "Metadata store initialized with project id=%r, database id=%r, collection=%r",
        resolve_firestore_project_id(),
        os.environ.get("FIRESTORE_DATABASE_ID"),
        collection_name,
    )
    return MetadataStore(client=client, collection_name=collection_name)
