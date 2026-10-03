"""고객 - 문의 상세.

- 상담 종료: 채팅창을 그대로 보여주고 입력은 막음 + '새 채팅하기'
- 상담 중:   채팅창 + '이어서 채팅하기' → 이 화면에서 바로 입력창이 열려 이어서 채팅
"""
from html import escape

import streamlit as st

from components.chat_panel import render_chat_panel
from components.ui import badge, info_grid, render_html
from utils.inquiry import change_signature, customer_status, end_chat, first_question
from utils.live import live_watch
from utils.navigation import go
from utils.session import current_user, get_inquiry


def render() -> None:
    inquiry = get_inquiry(st.query_params.get("id"))
    if inquiry is None or inquiry["customer"] != current_user()["name"]: 
        st.warning("문의를 찾을 수 없어요.")
        return
    ended = customer_status(inquiry) == "상담 종료"

    with st.container(key="card_summary"):
        render_html(f"""
            <div class="summary-top">{badge(customer_status(inquiry))}</div>
            <h2 class="summary-title">{escape(first_question(inquiry))}</h2>
        """)
        info_grid([ 
            ("문의번호", inquiry["id"]),
            ("문의 유형", inquiry["type"]),
            ("상담 상태", customer_status(inquiry)),
            ("등록일", inquiry["created_at"]),
            ("최근 답변", inquiry.get("answered_at") or "-"),
            ("종료일", inquiry.get("ended_at") or "상담 진행 중"),
        ])

    resume_key = f"resume_{inquiry['id']}"
    if st.session_state.get("page_entered"):       
        st.session_state.pop(resume_key, None)
    resumed = st.session_state.get(resume_key, False) and not ended

    if not resumed:   
        live_watch(f"detail_{inquiry['id']}", lambda: change_signature(get_inquiry(inquiry["id"])))

    render_chat_panel(inquiry, interactive=resumed, show_welcome=False, show_date=True, footer=_footer)


def _start_resume(inquiry_id: str) -> None:
    st.session_state[f"resume_{inquiry_id}"] = True


def _end(inquiry_id: str) -> None:
    inquiry = get_inquiry(inquiry_id)
    if inquiry:
        end_chat(inquiry, "고객 종료")
    st.session_state.pop(f"resume_{inquiry_id}", None)


def _footer(inquiry: dict) -> None:
    if inquiry.get("chat_state") == "ended": 
        if st.button("새 채팅하기", icon=":material/add_comment:", type="primary", width="stretch",
                     key="detail_new_chat"):
            st.session_state.chat_id = None
            go("customer_chat")
    elif st.session_state.get(f"resume_{inquiry['id']}"):
        st.button("채팅 종료하기", icon=":material/logout:", width="stretch", key="detail_end_chat",
                  on_click=_end, args=(inquiry["id"],))
    else:
        st.button("이어서 채팅하기", icon=":material/chat:", type="primary", width="stretch",
                  key="detail_resume", on_click=_start_resume, args=(inquiry["id"],))

