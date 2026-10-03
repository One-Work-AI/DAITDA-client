# from collections.abc import Callable
# from pathlib import Path

# import streamlit as st

# from components.sidebar import render_sidebar

# STYLE_PATH = Path(__file__).resolve().parent.parent / "styles" / "global.css"


# def load_global_styles() -> None:
#     css = STYLE_PATH.read_text(encoding="utf-8")
#     st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


# def render_layout(content: Callable[[], None], page_key: str) -> None:
#     side, main = st.columns([1, 5], gap="medium")
#     with side:
#         render_sidebar(page_key)
#     with main:
#         with st.container(key="main"):
#             content()


from collections.abc import Callable
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from components.sidebar import render_sidebar

STYLE_PATH = Path(__file__).resolve().parent.parent / "styles" / "global.css"


def load_global_styles() -> None:
    css = STYLE_PATH.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def render_layout(content: Callable[[], None], page_key: str) -> None:
    # 태블릿·모바일: Streamlit 기본 사이드바를 '서랍'으로 사용 (왼쪽 위 > 버튼으로 열고 닫음)
    # PC에서는 CSS로 숨기고, 아래의 고정 사이드바를 그대로 사용
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


# 서랍 메뉴로 페이지를 옮기면 서랍을 자동으로 닫음 (태블릿·모바일에서만)
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
