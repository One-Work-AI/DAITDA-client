"""고객 - 문의 내역. GET /api/conversations (서버에서 상태·유형·검색·페이지 처리, 최근 대화순)

필터 영역(상태 + 건수 / 검색 / 문의 유형)은 관리자 '문의 검토'와 같은 구성입니다.
- 상담 중: 채팅이 열려 있음 / 답변완료: 고객이 채팅을 종료했거나 5분 동안 메시지가 없어 자동 종료됨
"""
from html import escape

import streamlit as st

from components.ui import badge, icon, page_header, pagination, render_html, type_pill
from utils import api
from utils.api import fmt_time
from utils.inquiry import categories, category, items_of, list_signature, status_label, total_pages
from utils.live import live_watch
from utils.navigation import go
from utils.session import load

PAGE_SIZE = 5
STATUS_TABS = ["전체", "상담 중", "답변완료"]
STATUS_CODE = {"전체": None, "상담 중": "CHATTING", "답변완료": "ANSWERED"}   
COUNT_KEY = {"전체": "all", "상담 중": "CHATTING", "답변완료": "ANSWERED"}


def _set_page(n: int) -> None:
    st.session_state.history_page = n


def _reset_page() -> None:
    st.session_state.history_page = 1


def render() -> None:
    page_header("문의 내역", "지금까지 남긴 문의와 답변을 확인할 수 있어요.")
    st.session_state.setdefault("history_page", 1)
    if st.session_state.get("history_status") not in [*STATUS_TABS, None]:
        st.session_state.history_status = "전체"
    st.session_state.setdefault("history_status", "전체")
    st.session_state.setdefault("history_type", "전체")

    status = STATUS_CODE.get(st.session_state.history_status or "전체")
    cat = None if st.session_state.history_type in (None, "전체") else st.session_state.history_type
    q = (st.session_state.get("history_search") or "").strip() or None
    page = st.session_state.history_page

    res = load(api.list_conversations, status, q, page, PAGE_SIZE, cat)
    total = total_pages(res, PAGE_SIZE)
    if page > total:
        st.session_state.history_page = total
        st.rerun()
    live_watch("history", lambda: list_signature(api.list_conversations(status, q, page, PAGE_SIZE, cat)),
               interval=5, initial=list_signature(res))

    raw_counts = res.get("counts") or {}
    counts = {label: raw_counts.get(key, 0) for label, key in COUNT_KEY.items()}

    with st.container(key="card_history_filters"):
        f1, f2 = st.columns(
            [1, 1.3],
            vertical_alignment="bottom",
        )

        with f1:
            st.segmented_control(
                "문의 상태",
                STATUS_TABS,
                key="history_status",
                format_func=lambda s: f"{s} {counts[s]}",
                on_change=_reset_page,
            )

            st.text_input(
                "검색",
                placeholder="문의 내용, 상품명 검색",
                icon=":material/search:",
                key="history_search",
                on_change=_reset_page,
            )

        with f2:
            st.pills(
                "문의 유형",
                ["전체", *categories(admin=False)],
                key="history_type",
                on_change=_reset_page,
            )

    items = items_of(res)

    with st.container(key="card_history_list"):
        render_html(
            f"""
            <p class="table-caption">
                <b>{len(items)}건</b>
            </p>
            """
        )

        if not items:
            st.info("조건에 맞는 문의가 없어요.")
        else:
            for item in items:
                _render_card(item)

            pagination(page, total, _set_page)


def _render_card(item: dict) -> None:
    no = item["inquiry_no"]
    with st.container(key=f"hist_item_{no}"):
        body, action = st.columns([5, 1], vertical_alignment="center")
        with body:
            render_html(f"""
                <div class="hist-top">{badge(status_label(item))}{type_pill(category(item))}
                  <span class="hist-id">#{escape(no)}</span></div>
                <p class="hist-question">{escape(item.get("preview") or "")}</p>
                <div class="hist-time">{icon("clock")}<span>최근 대화 {fmt_time(item.get("last_message_at") or item.get("created_at"))}</span></div>
            """)
        with action:
            if st.button("보기", key=f"view_{no}", width="stretch"):
                go("customer_detail", id=no)