"""앱 전체(모든 브라우저 세션)가 함께 쓰는 저장소.

st.session_state는 브라우저마다 따로라서, 관리자 창과 고객 창이 같은 데이터를 보려면
st.cache_resource로 서버에 하나만 만들어 공유해야 합니다. (서버 재시작 시 초기화)
실서비스에서는 이 파일을 DB 접근 코드로 교체하면 됩니다.
"""
import copy
import threading
import uuid
from datetime import datetime, timedelta

import streamlit as st

from data.dummy import INQUIRIES, POLICIES, POLICY_DIR
from utils.inquiry import HANDOFF_MESSAGE, classify_type, generate_ai_draft, now


def new_message_id() -> str:
    return uuid.uuid4().hex[:8]


def _mark_pending_questions(item: dict) -> None:
    msgs = item["messages"]
    for i, m in enumerate(msgs):
        nxt = msgs[i + 1] if i + 1 < len(msgs) else None
        if m["role"] == "customer" and nxt and nxt["role"] == "ai" and nxt["content"] == HANDOFF_MESSAGE:
            m["pending_admin"] = True
            m["review_reason"] = (item.get("review_reasons") or [None])[0]
            m["ai_draft"] = generate_ai_draft(classify_type(m["content"]))


@st.cache_resource
def _store() -> dict:
    inquiries = copy.deepcopy(INQUIRIES)
    for item in inquiries:
        item.setdefault("ai_draft", generate_ai_draft(item["type"]))
        item.setdefault("chat_state", "ended")
        item.setdefault("review_reasons", [])
        item.setdefault("review_round", 1 if item["status"] == "검토대기" else 0)
        wait = item.pop("review_wait_min", None)
        item["review_requested_ts"] = now() - timedelta(minutes=wait) if wait is not None else None
        item["last_activity_ts"] = now()
        for m in item["messages"]:
            m.setdefault("id", new_message_id())
            last_customer = next((m["at"] for m in reversed(item["messages"]) if m["role"] == "customer"), None)
            item["last_customer_ts"] = datetime.strptime(last_customer or item["created_at"], "%Y.%m.%d %H:%M")
        if item["status"] == "검토대기":
            _mark_pending_questions(item)

    policies = copy.deepcopy(POLICIES)
    for p in policies:
        p["data"] = (POLICY_DIR / p["file_name"]).read_bytes()
        p["size"] = len(p["data"])

    return {"inquiries": inquiries, "policies": policies, "lock": threading.RLock()}


def inquiries() -> list[dict]:
    return _store()["inquiries"]


def policies() -> list[dict]:
    return _store()["policies"]


def lock() -> threading.RLock:
    return _store()["lock"]
