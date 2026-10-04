from collections.abc import Callable
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from components.sidebar import render_sidebar
from utils.navigation import go
from utils.session import current_user

STYLE_PATH = Path(__file__).resolve().parent.parent / "styles" / "global.css"

HEADER_CLICK_FIX = """
header[data-testid="stHeader"], [data-testid="stToolbar"] { pointer-events: none !important; }
[data-testid="stExpandSidebarButton"], [data-testid="stToolbar"] button { pointer-events: auto !important; }
"""


def load_global_styles() -> None:
    css = STYLE_PATH.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}{HEADER_CLICK_FIX}</style>", unsafe_allow_html=True)


def render_layout(content: Callable[[], None], page_key: str) -> None:
    if current_user() is None:
        go("login")

    with st.sidebar:
        render_sidebar(page_key, prefix="drawer_")
        if st.session_state.get("page_entered"):
            _close_drawer_on_small_screen()

    side, main = st.columns([1, 5], gap="medium")
    with side:
        render_sidebar(page_key)
    with main:
        with st.container(key="main"):
            content()

_CLOSE_DRAWER_JS = """
<script>
  // nonce: {nonce}  (내용이 매번 달라야 Streamlit이 스크립트를 다시 실행함)
  setTimeout(() => {
    const doc = window.parent.document;
    if (window.parent.innerWidth <= 1024) {
      const bar = doc.querySelector('[data-testid="stSidebar"]');
      const btn = doc.querySelector('[data-testid="stSidebarCollapseButton"] button');
      if (bar && bar.getAttribute('aria-expanded') === 'true' && btn) btn.click();
    }
  }, 150);
</script>
"""


def _close_drawer_on_small_screen() -> None:
    st.session_state._drawer_nonce = st.session_state.get("_drawer_nonce", 0) + 1
    components.html(_CLOSE_DRAWER_JS.replace("{nonce}", str(st.session_state._drawer_nonce)), height=0)