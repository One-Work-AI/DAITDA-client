"""고객 - 문의 상세. GET /api/conversations/{문의번호}

- 상담 종료: 채팅창을 그대로 보여주고 입력은 막음 + '새 채팅하기' / '문의 목록 보기'
- 상담 중:   채팅창 + '이어서 채팅하기' → 이 화면에서 바로 입력창이 열려 이어서 채팅
"""
from html import escape

import streamlit as st

from components.chat_panel import render_chat_panel
from components.ui import badge, info_grid, render_html, resolved_badge
from utils import api
from utils.api import fmt_time
from utils.inquiry import category, first_question, is_closed, product, status_label
from utils.navigation import go
from utils.session import load, run_action


def render() -> None:
    no = st.query_params.get("id")
    if not no:
        st.warning("문의를 찾을 수 없어요.")
        return
    inquiry = load(api.get_conversation, no, not_found="문의를 찾을 수 없어요.")
    ended = is_closed(inquiry)

    with st.container(key="card_summary"):
        render_html(f"""
            <div class="summary-top">{badge(status_label(inquiry))}{resolved_badge(inquiry)}</div>
            <h2 class="summary-title">{escape(first_question(inquiry))}</h2>
        """)
        info_grid([
            ("문의번호", escape(inquiry["inquiry_no"])),
            ("문의 유형", escape(category(inquiry))),
            ("주문 상품", escape(product(inquiry))),
            ("등록일", fmt_time(inquiry.get("created_at"))),
            ("답변완료", fmt_time(inquiry.get("answered_at"))),
            ("종료일", fmt_time(inquiry.get("closed_at"), empty="진행 중")),
        ])

    resume_key = f"resume_{inquiry['inquiry_no']}"
    if st.session_state.get("page_entered"):       
        st.session_state.pop(resume_key, None)
    resumed = st.session_state.get(resume_key, False) and not ended

    render_chat_panel(inquiry, interactive=resumed, show_welcome=False, show_date=True, footer=_footer)


def _start_resume(inquiry_no: str) -> None:
    st.session_state[f"resume_{inquiry_no}"] = True


def _end(inquiry_no: str) -> None:
    ok, _ = run_action(api.close_conversation, inquiry_no, "USER")
    st.session_state.pop(f"resume_{inquiry_no}", None)
    if ok:
        st.toast("채팅을 종료했어요. 답변완료로 이동했어요.", icon=":material/check_circle:")


def _new_chat() -> None:
    st.session_state.chat_id = None
    st.session_state.pop("resume_chat_id", None)


def _footer(inquiry: dict) -> None:
    no = inquiry["inquiry_no"]
    if is_closed(inquiry):
        c1, c2 = st.columns(2)
        if c1.button("새 채팅하기", icon=":material/add_comment:", type="primary", width="stretch",
                     key="detail_new_chat", on_click=_new_chat):
            go("customer_chat")
        if c2.button("문의 목록 보기", icon=":material/receipt_long:", width="stretch", key="detail_go_list"):
            go("customer_inquiries")
    elif st.session_state.get(f"resume_{no}"):
        st.button("채팅 종료하기", icon=":material/logout:", width="stretch", key="detail_end_chat",
                  on_click=_end, args=(no,))
    else:
        st.button("이어서 채팅하기", icon=":material/chat:", type="primary", width="stretch",
                  key="detail_resume", on_click=_start_resume, args=(no,))