"""자동 갱신: 다른 브라우저(관리자/고객)에서 데이터가 바뀌면 현재 화면을 다시 그림.

Streamlit은 서버가 화면에 먼저 알려주는 기능이 없어서, 몇 초마다 API로 '변경 여부'만 확인하고
바뀌었을 때만 전체 화면을 새로 그립니다.
- initial: 화면을 그릴 때 이미 받아 온 데이터의 비교값. 넘기면 첫 확인에서 API를 한 번 더 부르지 않아 빨라짐
- 조회 실패 시에는 이번 확인만 건너뜀
"""
from collections.abc import Callable

import streamlit as st

_MISSING = object()


def live_watch(key: str, signature: Callable[[], object], interval: int = 3, initial: object = _MISSING) -> None:
    state_key = f"_live_{key}"
    skip_key = f"_live_skip_{key}"
    if initial is not _MISSING:
        st.session_state[state_key] = initial
        st.session_state[skip_key] = True

    @st.fragment(run_every=interval)
    def _watch() -> None:
        if st.session_state.pop(skip_key, False):   
            return
        try:
            current = signature()
        except Exception:   
            return
        if state_key not in st.session_state:
            st.session_state[state_key] = current
        elif st.session_state[state_key] != current:
            st.session_state[state_key] = current
            st.rerun(scope="app")

    _watch()