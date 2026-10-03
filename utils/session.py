import streamlit as st

from data.dummy import USERS
from utils.store import inquiries, policies


def init_session_state() -> None:
    st.session_state.setdefault("user", None)
    st.session_state.setdefault("policy_id", None)
    st.session_state.setdefault("chat_id", None)  

def login(email: str, password: str) -> bool:
    account = USERS.get(email.strip().lower())
    if account is None or account["password"] != password:
        return False
    st.session_state.user = {k: v for k, v in account.items() if k != "password"}
    return True


def logout() -> None:
    st.session_state.user = None
    st.session_state.chat_id = None


def current_user() -> dict | None:
    return st.session_state.get("user")


def get_inquiry(inquiry_id: str | None) -> dict | None:
    return next((i for i in inquiries() if i["id"] == inquiry_id), None)


def customer_inquiries(name: str) -> list[dict]:
    return [i for i in inquiries() if i["customer"] == name]


def get_policy(policy_id: str | None) -> dict | None:
    return next((p for p in policies() if p["id"] == policy_id), None)
