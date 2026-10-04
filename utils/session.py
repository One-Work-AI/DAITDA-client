"""로그인 상태와 API 호출 도우미.

- 로그인 = 체험 입장 API로 받은 토큰을 st.session_state에 저장
- load():       화면을 그릴 때 쓰는 조회. 실패하면 안내 후 화면을 멈춤 (401이면 로그인 화면으로)
- run_action(): 버튼 콜백에서 쓰는 변경 요청. 실패하면 토스트로 안내하고 (False, None) 반환
"""
from collections.abc import Callable
from typing import Any

import streamlit as st

from utils import api
from utils.api import ApiError
from utils.navigation import go


def init_session_state() -> None:
    st.session_state.setdefault("user", None)
    st.session_state.setdefault("policy_id", None)
    st.session_state.setdefault("chat_id", None)


def demo_login(role: str) -> None:
    """role: 'customer' | 'admin'. 실패하면 ApiError."""
    res = api.demo_login(role)
    st.session_state[api.TOKEN_KEY] = res["access_token"]
    st.session_state.user = {"name": res.get("name") or "", "role": res.get("role") or role}


def logout() -> None:
    st.session_state.pop(api.TOKEN_KEY, None)
    st.session_state.user = None
    st.session_state.chat_id = None
    st.session_state.policy_id = None
    st.session_state.pop("_orders_cache", None)


def current_user() -> dict | None:
    if not api.token():
        return None
    return st.session_state.get("user")


def show_error(err: ApiError, not_found: str | None = None) -> None:
    """화면 조회 실패 안내 후 멈춤 (401이면 로그인 화면으로)."""
    if err.unauthorized:
        logout()
        go("login")
    if not_found and err.status == 404:
        st.warning(not_found)
    else:
        st.error(err.message, icon=":material/error:")
    st.stop()


def load(fn: Callable, *args: Any, not_found: str | None = None, **kwargs: Any) -> Any:
    try:
        return fn(*args, **kwargs)
    except ApiError as err:
        show_error(err, not_found)


def run_action(fn: Callable, *args: Any, messages: dict[str, str] | None = None,
               **kwargs: Any) -> tuple[bool, Any]:
    try:
        return True, fn(*args, **kwargs)
    except ApiError as err:
        if err.unauthorized:
            logout()   
        st.toast((messages or {}).get(err.code, err.message), icon=":material/error:")
        return False, None