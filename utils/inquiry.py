"""문의 관련 규칙 (나중에 백엔드 API로 옮길 부분).

상태는 두 가지 관점으로 나뉩니다.
- 관리자 상태 (status):     검토대기 / 답변완료
- 고객 상태 (customer_status): 상담 중 / 상담 종료  ← chat_state로 계산
- 고객이 채팅을 종료하면 관리자 상태도 바로 답변완료로 이동
"""
from datetime import datetime

KEYWORDS = {
    "배송": ["배송", "택배", "도착", "송장", "출고", "언제 와"],
    "결제": ["결제", "카드", "입금", "영수증"],
    "교환/환불": ["교환", "환불", "반품", "파손", "불량"],
    "주문": ["주문", "옵션", "변경", "배송지", "수량"],
}

AI_DRAFT_TEMPLATES = {
    "배송": "문의하신 주문건의 배송 현황을 확인했습니다. 택배사 인계 후 1~2일 내 받아보실 수 있습니다.",
    "결제": "결제 내역을 확인했습니다. 중복/오류 결제로 확인되는 경우 영업일 기준 3~5일 내 자동 취소 처리됩니다.",
    "교환/환불": "불편을 드려 죄송합니다. 확인 결과 교환/환불 접수가 가능하며, 회수 후 빠르게 처리해 드리겠습니다.",
    "주문": "출고 전 주문은 옵션 및 배송지 변경이 가능합니다. 요청하신 내용으로 변경 처리해 드리겠습니다.",
    "기타": "문의 주신 내용을 확인했습니다. 담당 부서 확인 후 상세히 안내드리겠습니다.",
}

HANDOFF_MESSAGE = "담당자가 확인 후 답변드릴게요. 기다리시는 동안 다른 궁금한 점도 편하게 물어보세요."


def now() -> datetime:
    return datetime.now()


def now_str() -> str:
    return now().strftime("%Y.%m.%d %H:%M")


def classify_type(text: str) -> str:
    """더미 AI 분류기 (키워드 매칭). 추후 AI팀 API로 교체."""
    scores = {t: sum(word in text for word in words) for t, words in KEYWORDS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "기타"


def generate_ai_draft(inquiry_type: str) -> str:
    """관리자 검토용 AI 답변 초안 (더미)."""
    body = AI_DRAFT_TEMPLATES.get(inquiry_type, AI_DRAFT_TEMPLATES["기타"])
    return f"안녕하세요, 고객님.\n{body}\n\n추가 문의사항이 있으시면 언제든 남겨주세요.\n감사합니다."

def first_question(inquiry: dict) -> str:
    return next((m["content"] for m in inquiry["messages"] if m["role"] == "customer"), "")


def customer_status(inquiry: dict) -> str:
    return "상담 종료" if inquiry.get("chat_state") == "ended" else "상담 중"


def waiting_minutes(inquiry: dict) -> int | None:
    ts = inquiry.get("review_requested_ts")
    if inquiry["status"] != "검토대기" or ts is None:
        return None
    return int((now() - ts).total_seconds() // 60)


def admin_messages(inquiry: dict) -> list[dict]:
    return [m for m in inquiry["messages"] if m["role"] == "admin"]


def latest_activity(inquiry: dict) -> datetime:
    ts = inquiry.get("last_customer_ts")
    return ts if ts is not None else datetime.strptime(inquiry["created_at"], "%Y.%m.%d %H:%M")


def pending_questions(inquiry: dict) -> list[dict]:
    return [m for m in inquiry["messages"] if m["role"] == "customer" and m.get("pending_admin")]


def change_signature(inquiry: dict | None) -> tuple:
    if inquiry is None:
        return ()
    return (inquiry["status"], inquiry.get("chat_state"), len(inquiry["messages"]), len(pending_questions(inquiry)),
            tuple(m.get("edited_at") for m in inquiry["messages"] if m["role"] == "admin"))

def _message(role: str, content: str) -> dict:
    from utils.store import new_message_id
    return {"id": new_message_id(), "role": role, "at": now_str(), "content": content}


def start_inquiry(customer: dict, order: dict | None) -> dict:
    from utils.store import inquiries, lock
    with lock():
        items = inquiries()
        seq = len(items) + 1
        ts = now()
        inquiry = {
            "id": f"Q{ts:%Y%m%d}-{seq:03d}",
            "cs_no": f"CS{ts:%y%m%d}{seq:04d}",
            "customer": customer["name"], "email": customer["email"], "phone": customer["phone"],
            "product": (order or {}).get("product", "-"), "order_no": (order or {}).get("order_no"),
            "type": "기타", "status": "답변완료", "resolved_by": None,
            "chat_state": "active", "created_at": now_str(), "answered_at": None,
            "ended_at": None, "end_reason": None,
            "review_reasons": [], "review_round": 0, "review_requested_ts": None,
            "last_activity_ts": ts, "last_customer_ts": ts, "messages": [], "ai_draft": "",
        }
        items.insert(0, inquiry)
    return inquiry


def add_customer_message(inquiry: dict, content: str) -> None:
    from utils.store import lock
    with lock():
        inquiry["messages"].append(_message("customer", content))
        inquiry["last_activity_ts"] = now()
        inquiry["last_customer_ts"] = now()        
        inquiry["awaiting_customer_view"] = False   
        from utils.chat import reset_timer
        reset_timer(inquiry)                         
        text = " ".join(m["content"] for m in inquiry["messages"] if m["role"] == "customer")
        inquiry["type"] = classify_type(text)


def apply_ai_reply(inquiry: dict, answer: str, needs_review: bool, reason: str | None) -> None:
    from utils.store import lock
    with lock():
        if needs_review:
            question = next((m for m in reversed(inquiry["messages"]) if m["role"] == "customer"), None)
            if question is not None:                     
                question["pending_admin"] = True
                question["review_reason"] = reason
                question["ai_draft"] = generate_ai_draft(classify_type(question["content"]))
            inquiry["messages"].append(_message("ai", HANDOFF_MESSAGE))
            if inquiry["status"] != "검토대기":           
                inquiry["review_round"] = inquiry.get("review_round", 0) + 1
                inquiry["review_reasons"] = []
                inquiry["review_requested_ts"] = now()
            if reason and reason not in inquiry["review_reasons"]:
                inquiry["review_reasons"].append(reason)
            inquiry["status"] = "검토대기"
            inquiry["ai_draft"] = generate_ai_draft(inquiry["type"])
        else:
            inquiry["messages"].append(_message("ai", answer))
            if inquiry["resolved_by"] is None:           
                inquiry["resolved_by"] = "AI"
                inquiry["answered_at"] = now_str()


def approve_inquiry(inquiry: dict, answer: str, admin_name: str) -> None:
    from utils.store import lock
    with lock():
        msg = _message("admin", answer.strip())
        msg["author"] = admin_name
        inquiry["messages"].append(msg)
        inquiry["status"] = "답변완료"
        inquiry["resolved_by"] = "관리자"
        inquiry["answered_at"] = msg["at"]
        inquiry["review_requested_ts"] = None
        inquiry["awaiting_customer_view"] = True


def answer_question(inquiry: dict, question_id: str, answer: str, admin_name: str) -> int:
    from utils.store import lock
    with lock():
        question = next((m for m in inquiry["messages"] if m["id"] == question_id), None)
        if question is None or not question.get("pending_admin"):
            return len(pending_questions(inquiry))
        msg = _message("admin", answer.strip())
        msg["author"] = admin_name
        msg["reply_to"] = question_id
        msg["reply_to_text"] = question["content"]      
        inquiry["messages"].append(msg)
        question["pending_admin"] = False
        question["answered_at"] = msg["at"]
        inquiry["resolved_by"] = "관리자"
        inquiry["answered_at"] = msg["at"]

        remaining = len(pending_questions(inquiry))
        if remaining == 0:                              
            inquiry["status"] = "답변완료"
            inquiry["review_requested_ts"] = None
            inquiry["awaiting_customer_view"] = True     
        return remaining


def mark_seen_by_customer(inquiry: dict) -> None:
    from utils.store import lock
    with lock():
        if inquiry.get("awaiting_customer_view"):
            inquiry["awaiting_customer_view"] = False
            inquiry["last_activity_ts"] = now()
            from utils.chat import reset_timer
            reset_timer(inquiry)                     


def edit_admin_message(inquiry: dict, message_id: str, content: str, admin_name: str) -> None:
    from utils.store import lock
    with lock():
        for m in inquiry["messages"]:
            if m["id"] == message_id and m["role"] == "admin":
                m["content"] = content.strip()
                m["edited_at"] = now_str()
                m["edited_by"] = admin_name


def end_chat(inquiry: dict, reason: str) -> None:
    from utils.store import lock
    with lock():
        if inquiry.get("chat_state") == "ended":
            return
        inquiry["chat_state"] = "ended"
        inquiry["ended_at"] = now_str()
        inquiry["end_reason"] = reason
        inquiry["status"] = "답변완료"
        inquiry["answered_at"] = inquiry.get("answered_at") or inquiry["ended_at"]
        inquiry["review_requested_ts"] = None
