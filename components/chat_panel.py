"""고객 채팅창 (고객 문의 화면과 문의 상세 화면이 같이 사용).

- 말풍선 목록 + 빠른 질문 버튼 + 입력창 + AI 답변 대기 말풍선 + 5분 자동 종료
- inquiry가 None이면 '새 채팅' (첫 메시지를 보내는 순간 문의가 만들어짐)
"""
import time
from collections.abc import Callable

import streamlit as st

from components.ui import bubble_html, icon, render_html, typing_bubble_html
from utils.chat import QUICK_PROMPTS, WELCOME, ai_reply, pause_timer, seconds_left, tick_timer
from utils.inquiry import (add_customer_message, apply_ai_reply, change_signature, end_chat, mark_seen_by_customer,
                           start_inquiry)
from utils.live import live_watch
from utils.session import current_user, get_inquiry


def _quick(prompt: str) -> None:
    st.session_state.quick_prompt = prompt


@st.fragment(run_every=5)
def _auto_close_watcher(inquiry_id: str | None) -> None:
    """5초마다 이 부분만 다시 실행 = '이 채팅을 보고 있음' 신호.
    화면이 열려 있는 동안만 시간이 줄고, 나갔다 오면 남은 시간부터 이어서 카운트."""
    inquiry = get_inquiry(inquiry_id)
    left = tick_timer(inquiry)
    if left is None:
        msg = ("담당자 확인 중에는 자동 종료되지 않아요." if inquiry and inquiry["status"] == "검토대기"
               else "마지막 메시지 후 5분 동안 입력이 없으면 채팅이 자동 종료돼요.")
        render_html(f'<p class="chat-hint">{icon("clock")}<span>{msg}</span></p>')
        return
    if left == 0:
        end_chat(inquiry, "자동 종료")
        st.rerun(scope="app")
    render_html(f'<p class="chat-hint">{icon("clock")}<span>{left // 60}:{left % 60:02d} 후 자동 종료</span></p>')


def _paused_hint(inquiry: dict) -> None:
    left = seconds_left(inquiry)
    msg = ("담당자 확인 중이에요. 자동 종료되지 않아요." if inquiry["status"] == "검토대기"
           else f"자동 종료 멈춤 · 남은 시간 {left // 60}:{left % 60:02d} (이어서 채팅하면 다시 카운트돼요)"
           if left is not None else "이어서 채팅하면 자동 종료 카운트가 시작돼요.")
    render_html(f'<p class="chat-hint">{icon("pause")}<span>{msg}</span></p>')


def _date_divider(inquiry: dict) -> str:
    date_text = (inquiry.get("created_at") or "").split(" ")[0]
    return (f'<div class="chat-session-divider"><div class="chat-session-date">'
            f'<span>{date_text}</span></div></div>')


def _end_notice(inquiry: dict) -> str:
    reason = ("5분 동안 메시지가 없어 채팅이 자동 종료되었어요." if inquiry.get("end_reason") == "자동 종료"
              else "채팅이 종료되었어요.")
    return bubble_html({"role": "system", "content": f"{reason}\n상담 내용은 문의 내역에서 다시 확인할 수 있어요."})


def render_chat_panel(
    inquiry: dict | None,
    *,
    interactive: bool,
    show_welcome: bool = True,
    show_date: bool = False,
    footer: Callable[[dict | None], None] | None = None,
) -> None:
    """채팅창 하나를 그림.

    interactive=True  : 입력창/빠른 질문/자동 종료까지 동작 (상담 중일 때만)
    interactive=False : 대화 내용만 보여줌 (입력 없음)
    footer            : 입력창 대신(또는 상담 종료 후) 카드 아래에 그릴 버튼 등
    """
    ended = bool(inquiry) and inquiry.get("chat_state") == "ended"
    live = interactive and not ended          # 입력창이 열린 '채팅 중' 상태에서만 5분 카운트

    if live and inquiry:
        mark_seen_by_customer(inquiry)   # 채팅을 시작한 시점에 관리자 답변을 확인한 것으로 보고 5분 카운트
        # 관리자 답변 등 변경이 생기면 자동으로 화면 갱신
        live_watch(f"chat_{inquiry['id']}", lambda: change_signature(get_inquiry(inquiry["id"])))

    with st.container(key="card_chat"):
        box = st.container(height=620, key="chat_box", autoscroll=True)
        with box:
            if show_date and inquiry:
                render_html(_date_divider(inquiry))
            if show_welcome:
                render_html(bubble_html({"role": "ai", "content": WELCOME, "at": ""}))
            for msg in (inquiry["messages"] if inquiry else []):
                render_html(bubble_html(msg))
            if ended:
                render_html(_end_notice(inquiry))

        if not live:
            if inquiry and not ended:    # 읽기 모드: 카운트 멈춤 + 남은 시간만 안내
                pause_timer(inquiry)
                _paused_hint(inquiry)
            if footer:
                footer(inquiry)
            return

        with st.container(key="quick_prompts", horizontal=True, gap="small"):
            for i, q in enumerate(QUICK_PROMPTS):
                st.button(q, key=f"quick_{i}", on_click=_quick, args=(q,))
        prompt = st.chat_input("메시지를 입력하세요", key="chat_input", max_chars=1000)
        prompt = prompt or st.session_state.pop("quick_prompt", None)
        _auto_close_watcher(inquiry["id"] if inquiry else None)
        if footer:
            footer(inquiry)
        if prompt:
            _send(inquiry, prompt, box)


def _send(inquiry: dict | None, prompt: str, box) -> None:
    if inquiry is None:   # 첫 메시지 → 문의 생성
        inquiry = start_inquiry(current_user(), None)
        st.session_state.chat_id = inquiry["id"]

    add_customer_message(inquiry, prompt.strip())
    with box:
        render_html(bubble_html(inquiry["messages"][-1]))
        pending = st.empty()
        pending.markdown(typing_bubble_html(), unsafe_allow_html=True)   # 답변 대기 말풍선
        time.sleep(1.2)                                                   # 더미 AI 응답 시간
        answer, needs_review, reason = ai_reply(prompt)
        pending.empty()
    apply_ai_reply(inquiry, answer, needs_review, reason)
    st.rerun()

