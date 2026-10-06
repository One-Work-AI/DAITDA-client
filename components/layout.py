from collections.abc import Callable
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from components.sidebar import render_sidebar
from utils.navigation import go
from utils.session import current_user

STYLE_PATH = Path(__file__).resolve().parent.parent / "styles" / "global.css"


# Streamlit 상단 헤더는 높이가 0이어도 안의 요소가 넘쳐서, 오른쪽 위 버튼(예: '고객 · 문의 정보') 클릭을 가로챔
# → 헤더는 클릭을 통과시키고, 헤더 안의 버튼만 클릭되게 (global.css와 별개로 항상 적용)
HEADER_CLICK_FIX = """
header[data-testid="stHeader"], [data-testid="stToolbar"] { pointer-events: none !important; }
[data-testid="stExpandSidebarButton"], [data-testid="stToolbar"] button { pointer-events: auto !important; }
"""


# 화면별 여백 조정 (모두 해당 카드 key로 범위를 한정해서 다른 화면에는 영향 없음)
LAYOUT_TWEAKS = """
/* 관리자 상세: '최종 답변' / '수정할 답변' 입력칸이 카드의 남은 높이를 채움 (아래 빈 여백 없앰) */
.st-key-card_admin_review [class*="st-key-draft_q_"],
.st-key-card_admin_review [class*="st-key-edit_"]:has(textarea) {
  flex: 1 1 auto !important; min-height: 160px; display: flex; flex-direction: column;
}
.st-key-card_admin_review [class*="st-key-draft_q_"] [data-testid="stTextArea"],
.st-key-card_admin_review [class*="st-key-edit_"]:has(textarea) [data-testid="stTextArea"] {
  flex: 1 1 auto; height: auto !important; display: flex; flex-direction: column;
}
.st-key-card_admin_review [class*="st-key-draft_q_"] [data-testid="stTextAreaRootElement"],
.st-key-card_admin_review [class*="st-key-edit_"]:has(textarea) [data-testid="stTextAreaRootElement"] {
  flex: 1 1 auto; height: auto !important;
}
.st-key-card_admin_review [class*="st-key-draft_q_"] textarea,
.st-key-card_admin_review [class*="st-key-edit_"] textarea {
  height: 100% !important;
}

/* 운영 대시보드: 시간대별 차트가 카드의 남은 높이를 채움 */
.st-key-card_hourly > [data-testid="stElementContainer"]:has([data-testid="stVegaLiteChart"]) {
  flex: 1 1 auto !important; min-height: 230px; display: flex; flex-direction: column;
}
.st-key-card_hourly [data-testid="stVegaLiteChart"] { flex: 1 1 auto; height: 100% !important; }

/* 정책 문서 관리: 휴지통 아이콘 크게 + 가운데 */
[class="st-key-policyitem"] [data-testid="stColumn"] > [data-testid="stVerticalBlock"] { gap: 2px; }
[class="st-key-policyitem"] [class="st-key-poldel"] { display: flex !important; justify-content: center !important; }
[class="st-key-policyitem"] [class="st-key-poldel"] button {
  width: 36px !important; min-width: 36px !important; max-width: 36px !important; height: 36px !important;
  padding: 0 !important; margin: 0 auto !important; border-radius: 8px;
  display: flex !important; align-items: center !important; justify-content: center !important;
}
[class="st-key-policyitem"] [class="st-key-poldel"] button > div,
[class="st-key-policyitem"] [class="st-key-poldel"] button span {
  margin: 0 !important; gap: 0 !important; justify-content: center !important;
}
[class="st-key-policyitem"] [class="st-key-poldel"] button [data-testid="stIconMaterial"] { font-size: 1.4rem; }
[class="st-key-policyitem"] [class="st-key-poldel"] button:hover { background: var(--color-surface); }
"""


def load_global_styles() -> None:
    css = STYLE_PATH.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}{HEADER_CLICK_FIX}{LAYOUT_TWEAKS}</style>", unsafe_allow_html=True)


def render_layout(content: Callable[[], None], page_key: str) -> None:
    # 토큰이 없거나 만료(401)되면 로그인 화면으로
    if current_user() is None:
        go("login")

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