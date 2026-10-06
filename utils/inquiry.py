# """문의 화면용 도우미.

# 상태 변경·AI 분류·초안 생성·자동 종료는 모두 백엔드가 처리합니다.
# 이 파일은 API 응답을 화면에 보여주기 쉽게 꺼내 쓰는 함수만 둡니다.
# """
# import math

# from utils.api import ApiError

# STATUS_LABEL = {"REVIEWING": "검토대기", "ANSWERED": "답변완료", "CLOSED": "상담 종료"}
# ANSWERED_BY_LABEL = {"AI": "AI 답변", "ADMIN": "관리자 답변"}
# DEFAULT_CATEGORIES = ["배송", "결제", "교환/환불", "주문", "기타"]


# # ---------------------------------------------------------------- 상태
# def status_code(inquiry: dict | None) -> str | None:
#     if not inquiry:
#         return None
#     return inquiry.get("status_code")


# def status_label(inquiry: dict) -> str:
#     return inquiry.get("status_label") or STATUS_LABEL.get(status_code(inquiry) or "", "-")


# def answered_by_label(inquiry: dict) -> str:
#     return inquiry.get("answered_by_label") or ANSWERED_BY_LABEL.get(inquiry.get("answered_by") or "", "")


# def is_closed(inquiry: dict | None) -> bool:
#     """채팅이 종료됐는지 (입력창이 잠기는 유일한 경우)."""
#     return bool(inquiry) and (bool(inquiry.get("input_locked")) or inquiry.get("status") == "CLOSED"
#                               or status_code(inquiry) == "CLOSED")


# def is_review_pending(inquiry: dict | None) -> bool:
#     return bool(inquiry) and (bool(inquiry.get("review_pending")) or status_code(inquiry) == "REVIEWING")


# # ---------------------------------------------------------------- 표시용 값
# def first_question(inquiry: dict) -> str:
#     msg = next((m for m in inquiry.get("messages") or [] if m.get("role") == "CUSTOMER"), None)
#     return (msg or {}).get("content") or inquiry.get("preview") or ""


# def category(inquiry: dict) -> str:
#     return inquiry.get("category") or "미분류"


# def product(inquiry: dict) -> str:
#     return inquiry.get("product_name") or "주문 상품 미선택"


# def admin_messages(inquiry: dict) -> list[dict]:
#     return [m for m in inquiry.get("messages") or [] if m.get("role") == "ADMIN"]


# def categories(admin: bool = True) -> list[str]:
#     if not admin:
#         return DEFAULT_CATEGORIES
#     from utils import api
#     try:
#         meta = api.meta() or {}
#     except ApiError:
#         return DEFAULT_CATEGORIES
#     raw = meta.get("categories") or meta.get("category") or []
#     names = [c if isinstance(c, str) else (c.get("name") or c.get("label")) for c in raw]
#     return [n for n in names if n] or DEFAULT_CATEGORIES


# # ---------------------------------------------------------------- 목록 응답
# def items_of(res: dict | list | None) -> list[dict]:
#     if isinstance(res, list):
#         return res
#     res = res or {}
#     for key in ("items", "results", "conversations", "reviews", "data"):
#         if isinstance(res.get(key), list):
#             return res[key]
#     return []


# def total_pages(res: dict | None, size: int) -> int:
#     res = res or {}
#     page = res.get("page") if isinstance(res.get("page"), dict) else {}
#     if page.get("total_pages"):
#         return max(1, int(page["total_pages"]))
#     total = page.get("total", page.get("total_items", res.get("total")))
#     if total is None:
#         total = len(items_of(res))
#     return max(1, math.ceil(int(total) / size))


# # ---------------------------------------------------------------- 자동 갱신 비교값
# def change_signature(inquiry: dict | None) -> tuple:
#     if not inquiry:
#         return ()
#     messages = inquiry.get("messages") or []
#     review = inquiry.get("review_question") or {}
#     return (status_code(inquiry), inquiry.get("input_locked"), inquiry.get("review_pending"),
#             inquiry.get("answering"), len(messages), messages[-1].get("id") if messages else None,
#             review.get("question_id"), bool(review.get("review")),
#             tuple((m.get("id"), m.get("edited_at")) for m in messages if m.get("edited_at")),
#             tuple(q.get("status") for q in inquiry.get("questions") or []))


# def list_signature(res: dict | None) -> tuple:
#     res = res or {}
#     rows = tuple((i.get("inquiry_no"), status_code(i), i.get("answered_at")) for i in items_of(res))
#     counts = tuple(sorted((res.get("counts") or {}).items()))
#     return rows + counts


"""문의 화면용 도우미.

상태 변경·AI 분류·초안 생성·자동 종료는 모두 백엔드가 처리합니다.
이 파일은 API 응답을 화면에 보여주기 쉽게 꺼내 쓰는 함수만 둡니다.
"""
import math

from utils.api import ApiError

STATUS_LABEL = {"REVIEWING": "검토대기", "ANSWERED": "답변완료", "CLOSED": "상담 종료"}
ANSWERED_BY_LABEL = {"AI": "AI 답변", "ADMIN": "관리자 답변"}
DEFAULT_CATEGORIES = ["배송", "결제", "교환/환불", "주문", "기타"]


# ---------------------------------------------------------------- 상태
def status_code(inquiry: dict | None) -> str | None:
    if not inquiry:
        return None
    return inquiry.get("status_code")


def status_label(inquiry: dict) -> str:
    return inquiry.get("status_label") or STATUS_LABEL.get(status_code(inquiry) or "", "-")


def answered_by_label(inquiry: dict) -> str:
    return inquiry.get("answered_by_label") or ANSWERED_BY_LABEL.get(inquiry.get("answered_by") or "", "")


def is_closed(inquiry: dict | None) -> bool:
    """채팅이 종료됐는지 (입력창이 잠기는 유일한 경우)."""
    return bool(inquiry) and (bool(inquiry.get("input_locked")) or inquiry.get("status") == "CLOSED"
                              or status_code(inquiry) == "CLOSED")


def is_review_pending(inquiry: dict | None) -> bool:
    return bool(inquiry) and (bool(inquiry.get("review_pending")) or status_code(inquiry) == "REVIEWING")


# ---------------------------------------------------------------- 표시용 값
def first_question(inquiry: dict) -> str:
    msg = next((m for m in inquiry.get("messages") or [] if m.get("role") == "CUSTOMER"), None)
    return (msg or {}).get("content") or inquiry.get("preview") or ""


def category(inquiry: dict) -> str:
    return inquiry.get("category") or "미분류"


def product(inquiry: dict) -> str:
    return inquiry.get("product_name") or "주문 상품 미선택"


def admin_messages(inquiry: dict) -> list[dict]:
    return [m for m in inquiry.get("messages") or [] if m.get("role") == "ADMIN"]


def categories(admin: bool = True) -> list[str]:
    if not admin:
        return DEFAULT_CATEGORIES
    from utils import api
    try:
        meta = api.meta() or {}
    except ApiError:
        return DEFAULT_CATEGORIES
    return [n for n in meta.get("display_categories") or [] if n] or DEFAULT_CATEGORIES


def category_intents() -> dict[str, list[str]]:
    """승인할 때 고를 수 있는 DB 카테고리 → 의도 목록 (GET /api/admin/meta). 실패하면 빈 dict."""
    from utils import api
    try:
        return (api.meta() or {}).get("category_intents") or {}
    except ApiError:
        return {}


# ---------------------------------------------------------------- 목록 응답
def items_of(res: dict | list | None) -> list[dict]:
    if isinstance(res, list):
        return res
    res = res or {}
    for key in ("items", "results", "conversations", "reviews", "data"):
        if isinstance(res.get(key), list):
            return res[key]
    return []


def total_pages(res: dict | None, size: int) -> int:
    res = res or {}
    page = res.get("page") if isinstance(res.get("page"), dict) else {}
    if page.get("total_pages"):
        return max(1, int(page["total_pages"]))
    total = page.get("total", page.get("total_items", res.get("total")))
    if total is None:
        total = len(items_of(res))
    return max(1, math.ceil(int(total) / size))


# ---------------------------------------------------------------- 자동 갱신 비교값
def change_signature(inquiry: dict | None) -> tuple:
    if not inquiry:
        return ()
    messages = inquiry.get("messages") or []
    review = inquiry.get("review_question") or {}
    return (status_code(inquiry), inquiry.get("input_locked"), inquiry.get("review_pending"),
            inquiry.get("answering"), len(messages), messages[-1].get("id") if messages else None,
            review.get("question_id"), bool(review.get("review")),
            tuple((m.get("id"), m.get("edited_at")) for m in messages if m.get("edited_at")),
            tuple(q.get("status") for q in inquiry.get("questions") or []))


def list_signature(res: dict | None) -> tuple:
    res = res or {}
    rows = tuple((i.get("inquiry_no"), status_code(i), i.get("answered_at")) for i in items_of(res))
    counts = tuple(sorted((res.get("counts") or {}).items()))
    return rows + counts