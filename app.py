import streamlit as st

from components.layout import load_global_styles, render_layout
from utils.navigation import HOME_PAGE, register
from utils.session import current_user, init_session_state
from views import (admin_dashboard, admin_detail, admin_policies, admin_review, customer_chat, customer_detail,
                   customer_inquiries, login)

st.set_page_config(
    page_title="daitda",
    page_icon=":material/storefront:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

PAGE_DEFS = {
    "login": (login.render, "login", "로그인", None),
    "customer_chat": (customer_chat.render, "inquiry", "고객 문의", "customer"),
    "customer_inquiries": (customer_inquiries.render, "my-inquiries", "문의 내역", "customer"),
    "customer_detail": (customer_detail.render, "my-inquiry", "문의 상세", "customer"),
    "admin_review": (admin_review.render, "admin-review", "문의 검토", "admin"),
    "admin_detail": (admin_detail.render, "admin-inquiry", "문의 상세", "admin"),
    "admin_dashboard": (admin_dashboard.render, "admin-dashboard", "운영 대시보드", "admin"),
    "admin_policies": (admin_policies.render, "admin-policies", "정책 문서 관리", "admin"),
}


def build_pages() -> dict:
    return {
        key: st.Page(fn, title=f"{title} · daitda", url_path=url, default=(key == "login"))
        for key, (fn, url, title, _) in PAGE_DEFS.items()
    }


def main() -> None:
    init_session_state()
    pages = build_pages()
    register(pages)

    current = st.navigation(list(pages.values()), position="hidden")
    key = next(k for k, p in pages.items() if p.url_path == current.url_path)

    user = current_user()
    required_role = PAGE_DEFS[key][3]
    if user is None and required_role is not None:
        st.switch_page(pages["login"])
    if user is not None and required_role != user["role"]:
        st.switch_page(pages[HOME_PAGE[user["role"]]])

    st.session_state.page_entered = st.session_state.get("_current_page") != key
    st.session_state._current_page = key

    load_global_styles()
    
    
    load_global_styles()
    if key == "login":
        current.run()
    else:
        render_layout(current.run, key)


if __name__ == "__main__":
    main()
