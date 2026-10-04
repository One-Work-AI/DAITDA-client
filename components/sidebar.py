from html import escape

import streamlit as st

from components.ui import brand, icon, render_html
from utils.navigation import go, page
from utils.session import current_user, logout

MENUS = {
    "customer": [
        ("customer_chat", ":material/chat:", "고객 문의"),
        ("customer_inquiries", ":material/receipt_long:", "문의 내역"),
    ],
    "admin": [
        ("admin_review", ":material/fact_check:", "문의 검토"),
        ("admin_dashboard", ":material/monitoring:", "운영 대시보드"),
        ("admin_policies", ":material/picture_as_pdf:", "정책 문서 관리"),
    ],
}

PARENT_PAGE = {"customer_detail": "customer_inquiries", "admin_detail": "admin_review"}


def render_sidebar(page_key: str, prefix: str = "") -> None:
    user = current_user()
    active = PARENT_PAGE.get(page_key, page_key)

    with st.container(key=f"{prefix}sidebar"):
        render_html(brand())

        with st.container(key=f"{prefix}sidebar_nav"):
            for key, menu_icon, label in MENUS[user["role"]]:
                state = "active" if key == active else "idle"
                with st.container(key=f"{prefix}navitem-{state}-{key}"):
                    st.page_link(page(key), label=label, icon=menu_icon, width="stretch")

        with st.container(key=f"{prefix}sidebar_bottom"):
            desc = "고객 계정" if user["role"] == "customer" else "관리자 계정"
            render_html(f"""
                <div class="user-card">
                  <span class="avatar">{icon("user-round", 18)}</span>
                  <div><div class="user-name">{escape(user["name"])}님</div><div class="user-desc">{desc}</div></div>
                </div>
            """)
            if st.button("로그아웃", icon=":material/logout:", key=f"{prefix}logout", width="stretch"):
                logout()
                go("login")