"""자동 갱신: 다른 브라우저(관리자/고객)에서 데이터가 바뀌면 현재 화면을 다시 그림.

Streamlit은 서버가 화면에 먼저 알려주는 기능이 없어서, 몇 초마다 '변경 여부'만 가볍게 확인하고
바뀌었을 때만 전체 화면을 새로 그립니다.
"""
from collections.abc import Callable

import streamlit as st


def live_watch(key: str, signature: Callable[[], object], interval: int = 3) -> None:
    @st.fragment(run_every=interval)
    def _watch() -> None:
        current = signature()
        state_key = f"_live_{key}"
        if state_key not in st.session_state:
            st.session_state[state_key] = current
        elif st.session_state[state_key] != current:
            st.session_state[state_key] = current
            st.rerun(scope="app")

    _watch()
