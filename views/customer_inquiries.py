import math
from html import escape

import streamlit as st

from components.ui import badge, page_header, render_html, type_pill
from data.dummy import CUSTOMER_STATUSES
from components.ui import badge, icon, page_header, render_html, type_pill                   
from utils.inquiry import change_signature, customer_status, first_question, latest_activity  
from utils.live import live_watch
from utils.navigation import go
from utils.session import current_user, customer_inquiries

PAGE_SIZE = 5


def _set_page(n: int) -> None:
    st.session_state.history_page = n


def render() -> None:
    page_header("문의 내역", "지금까지 남긴 문의와 답변을 확인할 수 있어요.")
    st.session_state.setdefault("history_page", 1)
    if st.session_state.get("history_status") not in ["전체", *CUSTOMER_STATUSES, None]:
        st.session_state.history_status = "전체"
    st.session_state.setdefault("history_status", "전체")

    name = current_user()["name"]
    live_watch("history", lambda: tuple(change_signature(i) for i in customer_inquiries(name)))

    with st.container(key="card_history_filters"):
        status_col, search_col = st.columns([1.15, 1.85], vertical_alignment="bottom")
        with status_col:
            st.segmented_control("상담 상태", ["전체", *CUSTOMER_STATUSES], key="history_status",
                                 on_change=_set_page, args=(1,))
        with search_col:
            keyword = st.text_input("검색", placeholder="문의 내용 검색", icon=":material/search:",
                                    key="history_search", on_change=_set_page, args=(1,))

    items = customer_inquiries(name)
    status = st.session_state.history_status or "전체"
    if status != "전체":
        items = [i for i in items if customer_status(i) == status]
    if keyword:
        items = [i for i in items if keyword in first_question(i)]

    items = sorted(items, key=latest_activity, reverse=True)

    with st.container(key="card_history_list"):
        if not items:
            st.info("조건에 맞는 문의가 없어요.")
            return

        total = max(1, math.ceil(len(items) / PAGE_SIZE))
        current = min(st.session_state.history_page, total)
        for item in items[(current - 1) * PAGE_SIZE: current * PAGE_SIZE]:
            _render_card(item)

        with st.container(key="pagination", horizontal=True, horizontal_alignment="center", gap="small"):
            st.button("", icon=":material/chevron_left:", key="pg_prev", disabled=current == 1,
                      on_click=_set_page, args=(current - 1,))
            for n in range(1, total + 1):
                st.button(str(n), key=f"pg_{n}", type="primary" if n == current else "secondary",
                          on_click=_set_page, args=(n,))
            st.button("", icon=":material/chevron_right:", key="pg_next", disabled=current == total,
                      on_click=_set_page, args=(current + 1,))


def _render_card(item: dict) -> None:
    with st.container(key=f"hist_item_{item['id']}"):  
        body, action = st.columns([5, 1], vertical_alignment="center")
        with body:
            render_html(f"""
                <div class="hist-top">{badge(customer_status(item))}{type_pill(item["type"])}
                  <span class="hist-id">#{item["id"]}</span></div>
                <p class="hist-question">{escape(first_question(item))}</p>
                <div class="hist-time">{icon("clock")}<span>최근 대화 {latest_activity(item):%Y.%m.%d %H:%M}</span></div>
            """)
        with action:
            if st.button("보기", key=f"view_{item['id']}", width="stretch"):
                go("customer_detail", id=item["id"])