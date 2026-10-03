import streamlit as st

PAGES: dict = {}
HOME_PAGE = {"customer": "customer_chat", "admin": "admin_review"}


def register(pages: dict) -> None:
    PAGES.clear()
    PAGES.update(pages)


def page(key: str):
    return PAGES[key]


def go(key: str, **query) -> None:
    st.switch_page(PAGES[key], query_params=query or None)
