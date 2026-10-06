# """백엔드 API 클라이언트.

# 화면 코드는 이 파일의 함수만 호출합니다. (data/dummy.py, utils/store.py 대체)
# - 서버 주소: 환경변수 DAITDA_API_URL (기본 http://localhost:8000)
# - 토큰: st.session_state["access_token"] → 모든 요청에 Authorization: Bearer
# - 실패 시 ApiError(code, message)를 던집니다. 401이면 토큰을 지웁니다.
# - 서버 시각은 UTC → 화면에서는 to_kst()/fmt_time()으로 한국 시간 표시
# """
# from __future__ import annotations

# import os
# from datetime import datetime, timedelta, timezone
# from typing import Any

# import requests
# import streamlit as st

# BASE_URL = os.environ.get("DAITDA_API_URL", "http://localhost:8000").rstrip("/")
# TIMEOUT = 10          
# AI_TIMEOUT = 90    
# UPLOAD_TIMEOUT = 120 
# TOKEN_KEY = "access_token"
# KST = timezone(timedelta(hours=9))


# # ---------------------------------------------------------------- 에러
# class ApiError(Exception):
#     def __init__(self, status: int, code: str, message: str, details: Any = None):
#         super().__init__(message)
#         self.status, self.code, self.message, self.details = status, code, message, details

#     @property
#     def unauthorized(self) -> bool:
#         return self.code == "UNAUTHORIZED" or self.status == 401


# def _to_error(res: requests.Response, method: str, path: str) -> ApiError:
#     body, detail = {}, None
#     try:
#         data = res.json()
#         body = data.get("error") or {}
#         detail = data.get("detail")           
#     except (ValueError, AttributeError):
#         detail = (res.text or "").strip()[:200] or None
#     code = body.get("code") or ("UNAUTHORIZED" if res.status_code == 401 else f"HTTP_{res.status_code}")
#     message = body.get("message")
#     if not message:
#         message = f"요청을 처리하지 못했어요. (HTTP {res.status_code} · {method} {path})"
#         if detail:
#             message += f" — {detail if isinstance(detail, str) else str(detail)[:200]}"
#     if res.status_code == 401:
#         st.session_state.pop(TOKEN_KEY, None)
#     return ApiError(res.status_code, code, message, body.get("details") or detail)


# # ---------------------------------------------------------------- 공통 요청
# @st.cache_resource
# def _http() -> requests.Session:
#     return requests.Session()


# def token() -> str | None:
#     return st.session_state.get(TOKEN_KEY)


# def _request(method: str, path: str, *, params: dict | None = None, json: Any = None,
#              files: dict | None = None, data: dict | None = None, timeout: int = TIMEOUT,
#              auth: bool = True, raw: bool = False) -> Any:
#     headers = {}
#     if auth and token():
#         headers["Authorization"] = f"Bearer {token()}"
#     params = {k: v for k, v in (params or {}).items() if v not in (None, "")}
#     try:
#         res = _http().request(method, f"{BASE_URL}{path}", params=params, json=json, files=files,
#                               data=data, headers=headers, timeout=timeout)
#     except requests.RequestException as exc:
#         raise ApiError(0, "NETWORK_ERROR",
#                        f"서버에 연결하지 못했어요. ({BASE_URL} · {type(exc).__name__})") from exc
#     if res.status_code >= 400:
#         raise _to_error(res, method, path)
#     if raw:
#         return res.content
#     if res.status_code == 204 or not res.content:
#         return None
#     return res.json()


# # ---------------------------------------------------------------- 시간 (UTC → KST)
# def to_kst(value: str | None) -> datetime | None:
#     if not value:
#         return None
#     dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
#     if dt.tzinfo is None:
#         dt = dt.replace(tzinfo=timezone.utc)
#     return dt.astimezone(KST)


# def fmt_time(value: str | None, pattern: str = "%Y.%m.%d %H:%M", empty: str = "-") -> str:
#     dt = to_kst(value)
#     return dt.strftime(pattern) if dt else empty


# def seconds_until(value: str | None) -> int | None:
#     """auto_close_at까지 남은 초 (없으면 None)."""
#     dt = to_kst(value)
#     if dt is None:
#         return None
#     return max(0, int((dt - datetime.now(KST)).total_seconds()))


# # ---------------------------------------------------------------- 로그인 (체험 입장)
# def demo_login(role: str) -> dict:
#     """role: 'customer' | 'admin' → {"access_token", "role", "name"}"""
#     return _request("POST", f"/api/demo/{role}", auth=False)


# # ---------------------------------------------------------------- 고객: 채팅
# def current_conversation() -> dict | None:
#     return _request("GET", "/api/conversations/current")


# def list_orders() -> list[dict]:
#     """문의할 주문 상품 목록 (최신 주문순) → [{"order_no", "product_name", "ordered_at"}]"""
#     return _request("GET", "/api/orders") or []


# def start_conversation(content: str, order_no: str | None = None) -> dict:
#     body = {"content": content, **({"order_no": order_no} if order_no else {})}
#     return _request("POST", "/api/conversations", params={"wait": "true"}, json=body, timeout=AI_TIMEOUT)


# def send_message(inquiry_no: str, content: str) -> dict:
#     return _request("POST", f"/api/conversations/{inquiry_no}/messages", params={"wait": "true"},
#                                 json={"content": content}, timeout=AI_TIMEOUT)


# def close_conversation(inquiry_no: str, reason: str = "USER") -> dict | None:
#     """reason: USER(채팅 종료하기) | NEW_CHAT(새 채팅하기)"""
#     return _request("POST", f"/api/conversations/{inquiry_no}/close", params={"reason": reason})


# # ---------------------------------------------------------------- 고객: 문의 내역 / 상세
# def list_conversations(status: str | None = None, q: str | None = None,
#                        page: int = 1, size: int = 10, category: str | None = None) -> dict:
#     """→ {"items", "page", "counts": {"all", "CHATTING", "ANSWERED"}}"""
#     return _request("GET", "/api/conversations",
#                     params={"status": status, "q": q, "category": category, "page": page, "size": size})


# def get_conversation(inquiry_no: str) -> dict:
#     return _request("GET", f"/api/conversations/{inquiry_no}")


# # ---------------------------------------------------------------- 관리자: 문의 검토
# def list_reviews(tab: str = "pending", q: str | None = None, category: str | None = None,
#                  page: int = 1, size: int = 20) -> dict:
#     """tab: pending | all | done"""
#     return _request("GET", "/api/admin/reviews",
#                     params={"tab": tab, "q": q, "category": category, "page": page, "size": size})


# def get_review(inquiry_no: str) -> dict:
#     return _request("GET", f"/api/admin/reviews/{inquiry_no}")


# def edit_answer(inquiry_no: str, question_id: int | str, response_text: str) -> dict:
#     """답변 수정하기 → 고객 채팅에 '수정됨'으로 표시 (PUT .../questions/{id}/answer)"""
#     return _request("PUT", f"/api/admin/reviews/{inquiry_no}/questions/{question_id}/answer",
#                     json={"response_text": response_text})


# def approve(inquiry_no: str, question_id: int | str, response_text: str) -> dict | None:
#     return _request("POST", f"/api/admin/reviews/{inquiry_no}/questions/{question_id}/approve",
#                     json={"response_text": response_text})


# # ---------------------------------------------------------------- 관리자: 대시보드 / 메타
# def dashboard() -> dict:
#     return _request("GET", "/api/admin/dashboard")


# @st.cache_data(ttl=3600, show_spinner=False)
# def _meta_cached(_token: str | None) -> dict:
#     return _request("GET", "/api/admin/meta")


# def meta() -> dict:
#     return _meta_cached(token())


# # ---------------------------------------------------------------- 관리자: 정책 문서
# def list_policies(q: str | None = None) -> list[dict]:
#     res = _request("GET", "/api/admin/policies", params={"q": q})
#     return res.get("items", res) if isinstance(res, dict) else (res or [])


# def get_policy(policy_id: int | str) -> dict:
#     return _request("GET", f"/api/admin/policies/{policy_id}")


# @st.cache_data(ttl=600, max_entries=32, show_spinner=False)
# def _policy_file_cached(policy_id: str, _token: str | None) -> bytes:
#     # 파일을 교체하면 id가 바뀌므로 id 기준 캐시가 안전합니다.
#     return _request("GET", f"/api/admin/policies/{policy_id}/file", raw=True)


# def policy_file(policy_id: int | str) -> bytes:
#     return _policy_file_cached(str(policy_id), token())


# def create_policy(file_name: str, data: bytes, title: str | None = None) -> dict:
#     return _request("POST", "/api/admin/policies", files={"file": (file_name, data, "application/pdf")},
#                     data={"title": title} if title else None, timeout=UPLOAD_TIMEOUT)


# def replace_policy_file(policy_id: int | str, file_name: str, data: bytes) -> dict:
#     return _request("PUT", f"/api/admin/policies/{policy_id}/file",
#                     files={"file": (file_name, data, "application/pdf")}, timeout=UPLOAD_TIMEOUT)


# def delete_policy(policy_id: int | str) -> None:
#     _request("DELETE", f"/api/admin/policies/{policy_id}")


"""백엔드 API 클라이언트.

화면 코드는 이 파일의 함수만 호출합니다. (data/dummy.py, utils/store.py 대체)
- 서버 주소: 환경변수 DAITDA_API_URL (기본 http://localhost:8000)
- 토큰: st.session_state["access_token"] → 모든 요청에 Authorization: Bearer
- 실패 시 ApiError(code, message)를 던집니다. 401이면 토큰을 지웁니다.
- 서버 시각은 UTC → 화면에서는 to_kst()/fmt_time()으로 한국 시간 표시
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any

import requests
import streamlit as st

BASE_URL = os.environ.get("DAITDA_API_URL", "http://localhost:8000").rstrip("/")
TIMEOUT = 15          # 일반 요청 (AI 답변은 기다리지 않음 → 화면이 몇 초마다 다시 조회)
UPLOAD_TIMEOUT = 120  # PDF 업로드
TOKEN_KEY = "access_token"
KST = timezone(timedelta(hours=9))


# ---------------------------------------------------------------- 에러
class ApiError(Exception):
    def __init__(self, status: int, code: str, message: str, details: Any = None):
        super().__init__(message)
        self.status, self.code, self.message, self.details = status, code, message, details

    @property
    def unauthorized(self) -> bool:
        return self.code == "UNAUTHORIZED" or self.status == 401


def _to_error(res: requests.Response, method: str, path: str) -> ApiError:
    body, detail = {}, None
    try:
        data = res.json()
        body = data.get("error") or {}
        detail = data.get("detail")           
    except (ValueError, AttributeError):
        detail = (res.text or "").strip()[:200] or None
    code = body.get("code") or ("UNAUTHORIZED" if res.status_code == 401 else f"HTTP_{res.status_code}")
    message = body.get("message")
    if not message:
        message = f"요청을 처리하지 못했어요. (HTTP {res.status_code} · {method} {path})"
        if detail:
            message += f" — {detail if isinstance(detail, str) else str(detail)[:200]}"
    if res.status_code == 401:
        st.session_state.pop(TOKEN_KEY, None)
    return ApiError(res.status_code, code, message, body.get("details") or detail)


# ---------------------------------------------------------------- 공통 요청
@st.cache_resource
def _http() -> requests.Session:
    return requests.Session()


def token() -> str | None:
    return st.session_state.get(TOKEN_KEY)


def _request(method: str, path: str, *, params: dict | None = None, json: Any = None,
             files: dict | None = None, data: dict | None = None, timeout: int = TIMEOUT,
             auth: bool = True, raw: bool = False) -> Any:
    headers = {}
    if auth and token():
        headers["Authorization"] = f"Bearer {token()}"
    params = {k: v for k, v in (params or {}).items() if v not in (None, "")}
    try:
        res = _http().request(method, f"{BASE_URL}{path}", params=params, json=json, files=files,
                              data=data, headers=headers, timeout=timeout)
    except requests.RequestException as exc:
        raise ApiError(0, "NETWORK_ERROR",
                       f"서버에 연결하지 못했어요. ({BASE_URL} · {type(exc).__name__})") from exc
    if res.status_code >= 400:
        raise _to_error(res, method, path)
    if raw:
        return res.content
    if res.status_code == 204 or not res.content:
        return None
    return res.json()


# ---------------------------------------------------------------- 시간 (UTC → KST)
def to_kst(value: str | None) -> datetime | None:
    if not value:
        return None
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(KST)


def fmt_time(value: str | None, pattern: str = "%Y.%m.%d %H:%M", empty: str = "-") -> str:
    dt = to_kst(value)
    return dt.strftime(pattern) if dt else empty


def seconds_until(value: str | None) -> int | None:
    """auto_close_at까지 남은 초 (없으면 None)."""
    dt = to_kst(value)
    if dt is None:
        return None
    return max(0, int((dt - datetime.now(KST)).total_seconds()))


# ---------------------------------------------------------------- 로그인 (체험 입장)
def demo_login(role: str) -> dict:
    """role: 'customer' | 'admin' → {"access_token", "role", "name"}"""
    return _request("POST", f"/api/demo/{role}", auth=False)


# ---------------------------------------------------------------- 고객: 채팅
def current_conversation() -> dict | None:
    return _request("GET", "/api/conversations/current")


def list_orders() -> list[dict]:
    """문의할 주문 상품 목록 (최신 주문순) → [{"order_no", "product_name", "ordered_at"}]"""
    return _request("GET", "/api/orders") or []


# AI 답변은 기다리지 않습니다 (wait=false). 서버가 바로 answering=true 로 응답하고,
# 채팅창(chat_panel)의 live_watch가 몇 초마다 다시 조회해 AI 답변이 붙으면 화면을 갱신합니다.
# wait=true 로 바꾸면 AI 서버 시간(AI_TIMEOUT_SECONDS, 기본 120초) 동안 화면이 멈춥니다.
def start_conversation(content: str, order_no: str | None = None) -> dict:
    body = {"content": content, **({"order_no": order_no} if order_no else {})}
    return _request("POST", "/api/conversations", json=body)


def send_message(inquiry_no: str, content: str) -> dict:
    return _request("POST", f"/api/conversations/{inquiry_no}/messages", json={"content": content})


def close_conversation(inquiry_no: str, reason: str = "USER") -> dict | None:
    """reason: USER(채팅 종료하기) | NEW_CHAT(새 채팅하기)"""
    return _request("POST", f"/api/conversations/{inquiry_no}/close", params={"reason": reason})


# ---------------------------------------------------------------- 고객: 문의 내역 / 상세
def list_conversations(status: str | None = None, q: str | None = None,
                       page: int = 1, size: int = 10, category: str | None = None) -> dict:
    """→ {"items", "page", "counts": {"all", "CHATTING", "ANSWERED"}}"""
    return _request("GET", "/api/conversations",
                    params={"status": status, "q": q, "category": category, "page": page, "size": size})


def get_conversation(inquiry_no: str) -> dict:
    return _request("GET", f"/api/conversations/{inquiry_no}")


# ---------------------------------------------------------------- 관리자: 문의 검토
def list_reviews(tab: str = "pending", q: str | None = None, category: str | None = None,
                 page: int = 1, size: int = 20) -> dict:
    """tab: pending | all | done"""
    return _request("GET", "/api/admin/reviews",
                    params={"tab": tab, "q": q, "category": category, "page": page, "size": size})


def get_review(inquiry_no: str) -> dict:
    return _request("GET", f"/api/admin/reviews/{inquiry_no}")


def edit_answer(inquiry_no: str, question_id: int | str, response_text: str) -> dict:
    """답변 수정하기 → 고객 채팅에 '수정됨'으로 표시 (PUT .../questions/{id}/answer)"""
    return _request("PUT", f"/api/admin/reviews/{inquiry_no}/questions/{question_id}/answer",
                    json={"response_text": response_text})


def approve(inquiry_no: str, question_id: int | str, response_text: str, *,
            category: str | None = None, intent: str | None = None,
            use_for_training: bool = False, remark: str | None = None) -> dict | None:
    """승인하기. category/intent는 AI 분류가 없거나 잘못됐을 때 반드시 보내야 함 (안 보내면 422 LABEL_REQUIRED)."""
    body = {"response_text": response_text, "use_for_training": use_for_training}
    if category:
        body["category"] = category
    if intent:
        body["intent"] = intent
    if remark and remark.strip():
        body["remark"] = remark.strip()
    return _request("POST", f"/api/admin/reviews/{inquiry_no}/questions/{question_id}/approve", json=body)


# ---------------------------------------------------------------- 관리자: 대시보드 / 메타
def dashboard() -> dict:
    return _request("GET", "/api/admin/dashboard")


@st.cache_data(ttl=3600, show_spinner=False)
def _meta_cached(_token: str | None) -> dict:
    return _request("GET", "/api/admin/meta")


def meta() -> dict:
    return _meta_cached(token())


# ---------------------------------------------------------------- 관리자: 정책 문서
def list_policies(q: str | None = None) -> list[dict]:
    res = _request("GET", "/api/admin/policies", params={"q": q})
    return res.get("items", res) if isinstance(res, dict) else (res or [])


def get_policy(policy_id: int | str) -> dict:
    return _request("GET", f"/api/admin/policies/{policy_id}")


@st.cache_data(ttl=600, max_entries=32, show_spinner=False)
def _policy_file_cached(policy_id: str, _token: str | None) -> bytes:
    # 파일을 교체하면 id가 바뀌므로 id 기준 캐시가 안전합니다.
    return _request("GET", f"/api/admin/policies/{policy_id}/file", raw=True)


def policy_file(policy_id: int | str) -> bytes:
    return _policy_file_cached(str(policy_id), token())


def create_policy(file_name: str, data: bytes, title: str | None = None) -> dict:
    return _request("POST", "/api/admin/policies", files={"file": (file_name, data, "application/pdf")},
                    data={"title": title} if title else None, timeout=UPLOAD_TIMEOUT)


def replace_policy_file(policy_id: int | str, file_name: str, data: bytes) -> dict:
    return _request("PUT", f"/api/admin/policies/{policy_id}/file",
                    files={"file": (file_name, data, "application/pdf")}, timeout=UPLOAD_TIMEOUT)


def delete_policy(policy_id: int | str) -> None:
    _request("DELETE", f"/api/admin/policies/{policy_id}")