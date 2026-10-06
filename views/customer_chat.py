"""고객 문의 - ChatGPT 형태의 채팅 화면.

- 메뉴로 들어오면 항상 새 채팅(소개 인사만 보임)으로 시작 → 첫 메시지 순간 문의 생성
  (진행 중이던 채팅은 그대로 열려 있고, 각 채팅은 5분 무응답이면 따로 자동 종료)
- 예전 채팅은 [문의 내역 > 보기 > 이어서 채팅하기]로 들어올 때만 이어서 보여줌 (resume_chat_id)
- 채팅 종료하기 = POST /close?reason=USER, 종료 후 '새 채팅하기' / '문의 목록 보기'
"""
import streamlit as st

from components.chat_panel import render_chat_panel
from components.ui import page_header
from utils import api
from utils.api import ApiError
from utils.inquiry import is_closed
from utils.navigation import go
from utils.session import run_action, show_error


def _current_chat() -> dict | None:
    if st.session_state.get("page_entered"):     # 메뉴로 들어오면 새 채팅, '이어서 채팅하기'로 오면 그 채팅
        st.session_state.chat_id = st.session_state.pop("resume_chat_id", None)
        st.query_params.clear()

    chat_id = st.session_state.get("chat_id")
    if not chat_id:
        return None
    try:
        return api.get_conversation(chat_id)
    except ApiError as err:
        if err.status != 404:
            show_error(err)
        st.session_state.chat_id = None
        return None


def _end(inquiry_no: str) -> None:
    ok, _ = run_action(api.close_conversation, inquiry_no, "USER")
    if ok:
        st.toast("채팅을 종료했어요. 문의 내역에서 다시 확인할 수 있어요.", icon=":material/check_circle:")


def _new_chat() -> None:
    st.session_state.chat_id = None


def _ended_footer(inquiry: dict | None) -> None:
    c1, c2 = st.columns(2)
    c1.button("새 채팅하기", icon=":material/add_comment:", type="primary", width="stretch",
              key="new_chat", on_click=_new_chat)
    if c2.button("문의 목록 보기", icon=":material/receipt_long:", width="stretch", key="go_history"):
        go("customer_inquiries")


def render() -> None:
    inquiry = _current_chat()
    ended = is_closed(inquiry)

    head_left, head_right = st.columns([4, 1], vertical_alignment="bottom")
    with head_left:
        page_header("고객 문의", "DAITDA AI 상담사가 바로 답변해 드려요.")
    with head_right:
        if inquiry and not ended:
            st.button("채팅 종료하기", icon=":material/logout:", key="end_chat", width="stretch",
                      on_click=_end, args=(inquiry["inquiry_no"],))

    render_chat_panel(inquiry, interactive=True, show_welcome=True,
                      footer=_ended_footer if ended else None)