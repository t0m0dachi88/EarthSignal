from datetime import datetime, timezone
from uuid import uuid4

def utcnow():
    return datetime.now(timezone.utc)

def new_id() -> str:
    return str(uuid4())
