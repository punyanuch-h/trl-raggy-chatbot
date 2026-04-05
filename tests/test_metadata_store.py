import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from metadata_store import MetadataStore, build_metadata_record


class FakeDocumentReference:
    def __init__(self, collection_data, document_id):
        self.collection_data = collection_data
        self.document_id = document_id

    def set(self, payload):
        self.collection_data[self.document_id] = dict(payload)


class FakeSnapshot:
    def __init__(self, payload):
        self.payload = payload

    def to_dict(self):
        return dict(self.payload)


class FakeQuery:
    def __init__(self, records):
        self.records = list(records)

    def where(self, field_name, op, value):
        assert op == "=="
        self.records = [record for record in self.records if record.get(field_name) == value]
        return self

    def order_by(self, field_name, direction=None):
        reverse = str(direction).upper().endswith("DESCENDING")
        self.records = sorted(self.records, key=lambda record: record.get(field_name, ""), reverse=reverse)
        return self

    def limit(self, limit):
        self.records = self.records[:limit]
        return self

    def stream(self):
        return [FakeSnapshot(record) for record in self.records]


class FakeCollection:
    def __init__(self):
        self.data = {}

    def document(self, document_id):
        return FakeDocumentReference(self.data, document_id)

    def where(self, field_name, op, value):
        return FakeQuery(self.data.values()).where(field_name, op, value)

    def order_by(self, field_name, direction=None):
        return FakeQuery(self.data.values()).order_by(field_name, direction)


class FakeFirestoreClient:
    def __init__(self):
        self.collections = {}

    def collection(self, name):
        return self.collections.setdefault(name, FakeCollection())


def test_build_metadata_record_excludes_transcript_content():
    timestamp = datetime(2026, 4, 4, 15, 30, tzinfo=timezone.utc)

    record = build_metadata_record(
        user_id="user-123",
        role="researcher",
        route_path="/raggy/trl",
        request_id="req-001",
        session_id="sess-001",
        response_status="success",
        model_name="gpt-4o-mini",
        timestamp=timestamp,
    )

    assert record["request_id"] == "req-001"
    assert record["session_id"] == "sess-001"
    assert record["user_id"] == "user-123"
    assert record["role"] == "researcher"
    assert record["response_status"] == "success"
    assert record["route_path"] == "/raggy/trl"
    assert record["model_name"] == "gpt-4o-mini"
    assert record["timestamp"] == "2026-04-04T15:30:00+00:00"
    assert "query" not in record
    assert "answer" not in record
    assert "answer_markdown" not in record
    assert "context" not in record


def test_metadata_store_save_record_uses_request_id_as_document_key():
    client = FakeFirestoreClient()
    store = MetadataStore(client=client, collection_name="request_metadata")
    record = {
        "request_id": "req-123",
        "session_id": "sess-123",
        "user_id": "user-123",
        "role": "admin",
        "timestamp": "2026-04-04T15:30:00+00:00",
        "response_status": "success",
        "route_path": "/raggy/trl",
        "model_name": "gpt-4o-mini",
    }

    store.save_record(record)

    stored_record = client.collection("request_metadata").data["req-123"]
    assert stored_record == record


def test_metadata_store_get_records_by_session_returns_matching_records_in_descending_timestamp_order():
    client = FakeFirestoreClient()
    store = MetadataStore(client=client, collection_name="request_metadata")
    records = [
        {
            "request_id": "req-100",
            "session_id": "sess-a",
            "user_id": "user-123",
            "role": "researcher",
            "timestamp": "2026-04-04T10:00:00+00:00",
            "response_status": "success",
            "route_path": "/raggy/trl",
            "model_name": "gpt-4o-mini",
        },
        {
            "request_id": "req-200",
            "session_id": "sess-a",
            "user_id": "user-123",
            "role": "researcher",
            "timestamp": "2026-04-04T12:00:00+00:00",
            "response_status": "success",
            "route_path": "/raggy/trl",
            "model_name": "gpt-4o-mini",
        },
        {
            "request_id": "req-300",
            "session_id": "sess-b",
            "user_id": "user-456",
            "role": "admin",
            "timestamp": "2026-04-04T11:00:00+00:00",
            "response_status": "success",
            "route_path": "/raggy/trl",
            "model_name": "gpt-4o-mini",
        },
    ]

    for record in records:
        store.save_record(record)

    session_records = store.get_records_by_session("sess-a")

    assert [record["request_id"] for record in session_records] == ["req-200", "req-100"]


def test_metadata_store_list_recent_records_limits_results():
    client = FakeFirestoreClient()
    store = MetadataStore(client=client, collection_name="request_metadata")

    for index in range(3):
        store.save_record(
            {
                "request_id": f"req-{index}",
                "session_id": "sess-a",
                "user_id": "user-123",
                "role": "researcher",
                "timestamp": f"2026-04-04T1{index}:00:00+00:00",
                "response_status": "success",
                "route_path": "/raggy/trl",
                "model_name": "gpt-4o-mini",
            }
        )

    records = store.list_recent_records(limit=2)

    assert [record["request_id"] for record in records] == ["req-2", "req-1"]
