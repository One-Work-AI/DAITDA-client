"""고객 문의 - ChatGPT 형태의 채팅 화면.

- 메뉴로 들어올 때마다 항상 새 채팅(소개 인사만 보임)으로 시작
- 진행 중인 예전 채팅은 [문의 내역 > 보기 > 이어서 채팅하기]에서 그 화면 그대로 이어서 진행
- 첫 메시지 순간 문의가 공유 저장소에 저장됨 → 관리자 화면에 바로 표시
"""
import streamlit as st

from components.chat_panel import render_chat_panel
from components.ui import page_header
from utils.inquiry import end_chat
from utils.session import current_user, get_inquiry


def _current_chat() -> dict | None:
    if st.session_state.get("page_entered"):   
        st.session_state.chat_id = None
        st.query_params.clear()
        return None
    inquiry = get_inquiry(st.session_state.get("chat_id"))
    if inquiry is None or inquiry["customer"] != current_user()["name"]:
        return None
    return inquiry


def _end(inquiry_id: str) -> None:
    inquiry = get_inquiry(inquiry_id)
    if inquiry:
        end_chat(inquiry, "고객 종료")


def _new_chat_footer(inquiry: dict | None) -> None:
    """상담이 끝난 뒤: 새 채팅하기."""
    if st.button("새 채팅하기", icon=":material/add_comment:", type="primary", width="stretch", key="new_chat"):
        st.session_state.chat_id = None
        st.rerun()


def render() -> None:
    inquiry = _current_chat()
    ended = bool(inquiry) and inquiry.get("chat_state") == "ended"

    head_left, head_right = st.columns([4, 1], vertical_alignment="bottom")
    with head_left:
        page_header("고객 문의", "daitda AI 상담사가 바로 답변해 드려요.")
    with head_right:
        if inquiry and not ended:
            st.button("채팅 종료하기", icon=":material/logout:", key="end_chat", width="stretch",
                      on_click=_end, args=(inquiry["id"],))

    render_chat_panel(inquiry, interactive=True, show_welcome=True,
                      footer=_new_chat_footer if ended else None)
