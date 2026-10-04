"""고객 채팅창 (고객 문의 화면과 문의 상세 화면이 같이 사용).

- 말풍선·상태는 모두 백엔드 '채팅 응답' 기준
- inquiry가 None이면 '새 채팅' (첫 메시지를 보내는 순간 POST /api/conversations)
- 새 채팅에서는 '문의할 주문 상품'을 고를 수 있음 (GET /api/orders → order_no). 고른 상품은 AI에도 전달됨
- 5분 자동 종료는 서버가 처리. 화면은 auto_close_at까지 남은 시간을 표시하고,
  시간이 다 되면 서버에 다시 조회해 바로 종료 상태를 반영 (관리자 화면에도 바로 답변완료로 보임)
"""
from collections.abc import Callable
from html import escape

import streamlit as st

from components.ui import bubble_html, icon, render_html, typing_bubble_html, with_reply_quotes
from utils import api
from utils.api import ApiError, seconds_until
from utils.chat import QUICK_PROMPTS, WELCOME
from utils.inquiry import change_signature, is_closed, is_review_pending
from utils.live import live_watch
from utils.navigation import go
from utils.session import logout


def _quick(prompt: str) -> None:
    st.session_state.quick_prompt = prompt


@st.fragment(run_every=5)
def _auto_close_hint(inquiry_no: str | None, auto_close_at: str | None, review_pending: bool) -> None:
    if review_pending:
        ic, msg = "pause", "담당자 확인 중인 질문이 있어 자동 종료되지 않아요."
    else:
        left = seconds_until(auto_close_at)
        ic = "clock"
        if left is None:
            msg = "답변 후 5분 동안 메시지가 없으면 채팅이 자동 종료돼요."
        elif left == 0:
            try:
                closed = inquiry_no and is_closed(api.get_conversation(inquiry_no))
            except ApiError:
                closed = False
            if closed:
                st.rerun(scope="app")
            msg = "곧 채팅이 자동 종료돼요."
        else:
            msg = f"{left // 60}:{left % 60:02d} 후 자동 종료"
    render_html(f'<p class="chat-hint">{icon(ic)}<span>{msg}</span></p>')


def _order_picker() -> None:
    """새 채팅에서만: 문의할 주문 상품 선택 (주문이 없거나 조회 실패면 표시 안 함)."""
    orders = st.session_state.get("_orders_cache")
    if orders is None:                  
        try:
            orders = api.list_orders()
        except ApiError:
            return
        st.session_state._orders_cache = orders
    if not orders:
        return
    labels = {o["order_no"]: f'{o["product_name"]} · {api.fmt_time(o.get("ordered_at"), "%Y.%m.%d", "")} 주문'
              for o in orders}
    st.selectbox("문의할 주문 상품", [None, *labels], key="chat_order_no",
                 format_func=lambda v: "선택 안 함" if v is None else labels.get(v, v),
                 help="상품을 고르면 AI 상담사가 해당 주문을 기준으로 답변해요.")


def _product_line(inquiry: dict) -> None:
    name = inquiry.get("product_name")
    text = f"문의 상품 · {escape(name)}" if name else "문의 상품 · 선택 안 함"
    render_html(f'<p class="chat-hint">{icon("package")}<span>{text}</span></p>')


def _date_divider(inquiry: dict) -> str:
    date_text = api.fmt_time(inquiry.get("created_at"), "%Y.%m.%d", "")
    return (f'<div class="chat-session-divider"><div class="chat-session-date">'
            f'<span>{date_text}</span></div></div>')


def _end_notice(inquiry: dict) -> str:
    reason = inquiry.get("close_reason_label") or ""
    timeout = inquiry.get("close_reason") == "TIMEOUT" or "자동" in reason
    head = "5분 동안 메시지가 없어 채팅이 자동 종료되었어요." if timeout else "채팅이 종료되었어요."
    return bubble_html({"role": "system",
                        "content": f"{head}\n문의번호 #{inquiry['inquiry_no']}로 저장되었어요. "
                                   "상담 내용은 문의 내역에서 다시 확인할 수 있어요."})


def render_chat_panel(
    inquiry: dict | None,
    *,
    interactive: bool,
    show_welcome: bool = True,
    show_date: bool = False,
    footer: Callable[[dict | None], None] | None = None,
) -> None:

    ended = is_closed(inquiry)
    live = interactive and not ended

    if inquiry and (not ended or is_review_pending(inquiry)):
        no = inquiry["inquiry_no"]
        live_watch(f"chat_{no}", lambda: change_signature(api.get_conversation(no)), initial=change_signature(inquiry))

    with st.container(key="card_chat"):
        if live and inquiry is None:
            _order_picker()
        elif interactive and inquiry:
            _product_line(inquiry)
        box = st.container(height=620, key="chat_box", autoscroll=True)
        with box:
            if show_date and inquiry:
                render_html(_date_divider(inquiry))
            if show_welcome:
                render_html(bubble_html({"role": "ai", "content": WELCOME}))
            for msg in with_reply_quotes((inquiry or {}).get("messages") or []):
                render_html(bubble_html(msg))
            if inquiry and inquiry.get("answering") and not ended:
                render_html(typing_bubble_html())
            if ended:
                render_html(_end_notice(inquiry))

        if not live:
            if inquiry and not ended:
                _auto_close_hint(inquiry["inquiry_no"], inquiry.get("auto_close_at"),
                                 bool(inquiry.get("review_pending")))
            if footer:
                footer(inquiry)
            return

        with st.container(key="quick_prompts", horizontal=True, gap="small"):
            for i, q in enumerate(QUICK_PROMPTS):
                st.button(q, key=f"quick_{i}", on_click=_quick, args=(q,))
        prompt = st.chat_input("메시지를 입력하세요", key="chat_input", max_chars=1000)
        prompt = prompt or st.session_state.pop("quick_prompt", None)
        if inquiry:
            _auto_close_hint(inquiry["inquiry_no"], inquiry.get("auto_close_at"), bool(inquiry.get("review_pending")))
        else:
            render_html(f'<p class="chat-hint">{icon("clock")}'
                        "<span>답변 후 5분 동안 메시지가 없으면 채팅이 자동 종료돼요.</span></p>")
        if footer:
            footer(inquiry)
        if prompt and prompt.strip():
            _send(inquiry, prompt.strip(), box)


def _send(inquiry: dict | None, prompt: str, box) -> None:
    with box:
        render_html(bubble_html({"role": "customer", "content": prompt}))
        pending = st.empty()
        pending.markdown(typing_bubble_html(), unsafe_allow_html=True)  
    try:
        if inquiry is None:                     
            result = api.start_conversation(prompt, st.session_state.get("chat_order_no"))
        else:
            result = api.send_message(inquiry["inquiry_no"], prompt)
    except ApiError as err:
        pending.empty()
        if err.unauthorized:
            logout()
            go("login")
        st.toast(err.message, icon=":material/error:")
        return
    st.session_state.chat_id = result["inquiry_no"]
    st.rerun()