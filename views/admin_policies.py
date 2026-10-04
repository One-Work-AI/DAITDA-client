"""관리자 - 정책 문서 관리 (PDF 첨부 전용).

- 왼쪽 카드: 정책 문서 목록(선택/삭제) + 새 PDF 등록
- 오른쪽 카드: PDF 미리보기 (한 페이지씩, 이전/다음 버튼)
- 두 카드 모두 사이드바 높이에 맞추고, 넘치는 부분은 카드 안에서만 스크롤
- 데이터: GET/POST/DELETE /api/admin/policies, 미리보기 GET /api/admin/policies/{id}/file
"""
from html import escape
from io import BytesIO
from pathlib import Path

import pypdfium2 as pdfium
import streamlit as st

from components.ui import card_title, icon, render_html
from utils import api
from utils.api import ApiError, fmt_time
from utils.session import load, run_action

DUPLICATE_MESSAGE = "같은 파일 이름의 문서가 이미 있어요."


def _meta(p: dict) -> str:
    return f'{p.get("filename") or "-"} · {_size(p.get("size_bytes"))} · {fmt_time(p.get("created_at"))}'


def _size(num: int | None) -> str:
    num = num or 0
    return f"{num / 1024:.0f} KB" if num < 1024 * 1024 else f"{num / 1024 / 1024:.1f} MB"


def _uploader_key(name: str) -> str:
    return f"{name}_{st.session_state.get('upload_nonce', 0)}"


def _reset_uploaders() -> None:
    st.session_state.upload_nonce = st.session_state.get("upload_nonce", 0) + 1


@st.cache_data(show_spinner=False, max_entries=64)
def _page_count(data: bytes) -> int:
    return len(pdfium.PdfDocument(data))


@st.cache_data(show_spinner=False, max_entries=64)
def _render_page(data: bytes, index: int) -> bytes:
    page = pdfium.PdfDocument(data)[index]
    image = page.render(scale=2).to_pil()  
    buf = BytesIO()
    image.save(buf, format="PNG")
    return buf.getvalue()


def _page_key(policy_id: str) -> str:
    return f"pdf_page_{policy_id}"


def _select(policy_id: str) -> None:
    st.session_state.policy_id = policy_id


def _move_page(policy_id: str, step: int, total: int) -> None:
    key = _page_key(policy_id)
    st.session_state[key] = min(max(st.session_state.get(key, 0) + step, 0), total - 1)


def _register() -> None:
    file = st.session_state.get(_uploader_key("pdf_new"))
    if file is None:
        return
    title = st.session_state.get("pdf_new_title", "").strip() or Path(file.name).stem
    ok, res = run_action(api.create_policy, file.name, file.getvalue(), title,
                         messages={"DUPLICATE_POLICY": DUPLICATE_MESSAGE})
    if not ok:
        return
    if res and res.get("id") is not None:
        st.session_state.policy_id = res["id"]
    st.session_state.pdf_new_title = ""
    _reset_uploaders()
    st.toast("PDF 문서를 등록했어요.", icon=":material/upload_file:")


def _delete(policy_id) -> None:
    ok, _ = run_action(api.delete_policy, policy_id)
    if not ok:
        return
    if str(st.session_state.get("policy_id")) == str(policy_id):
        st.session_state.policy_id = None
    st.toast("문서를 삭제했어요.", icon=":material/delete:")


def render() -> None:
    render_html("""
        <div class="page-header"><div><h1>정책 문서 관리</h1>
        <p>AI 상담과 관리자 답변에 참고하는 정책 문서를 PDF로 관리해요.</p></div></div>
    """)
    policies = load(api.list_policies)
    selected = next((p for p in policies if str(p["id"]) == str(st.session_state.get("policy_id"))), None)
    if policies and selected is None:
        selected = policies[0]
        st.session_state.policy_id = selected["id"]

    left, right = st.columns([1, 1.5], gap="small")  
    with left:
        _render_left(policies, selected)
    with right:
        _render_preview(selected)


def _render_left(policies: list[dict], selected: dict | None) -> None:
    with st.container(key="card_pdf_list"):
        card_title("정책 문서", "folder-open", subtitle=f"PDF {len(policies)}개")

        with st.container(key="pdf_list_scroll"):
            if not policies:
                render_html('<p class="muted">등록된 문서가 없어요.</p>')
            for p in policies:
                state = "-selected" if selected and p["id"] == selected["id"] else ""
                with st.container(key=f"policyitem{state}-{p['id']}"):
                    c1, c2 = st.columns([6, 1], vertical_alignment="center")
                    c1.button(p.get("title") or p.get("filename") or "-", icon=":material/picture_as_pdf:", key=f"pol_sel_{p['id']}",
                              type="tertiary", width="stretch", on_click=_select, args=(p["id"],))
                    c2.button("", icon=":material/delete:", key=f"pol_del_{p['id']}", type="tertiary",
                              help="문서 삭제", on_click=_delete, args=(p["id"],))
                    render_html(f'<p class="policy-meta">{escape(_meta(p))}</p>')

        with st.container(key="pdf_upload_area"):
            render_html(f'<p class="field-label">{icon("upload")}<span>새 PDF 등록</span></p>')
            st.file_uploader("PDF 파일", type=["pdf"], key=_uploader_key("pdf_new"), label_visibility="collapsed")

            st.button("등록하기", icon=":material/upload_file:", type="primary", width="stretch", key="pdf_register",
                      disabled=not st.session_state.get(_uploader_key("pdf_new")), on_click=_register)


def _render_preview(selected: dict | None) -> None:
    with st.container(key="card_pdf_preview"):
        if selected is None:
            card_title("PDF 미리보기", "eye")
            render_html('<div class="empty-box">등록된 PDF가 없어요. 왼쪽에서 문서를 업로드해 주세요.</div>')
            return

        card_title(selected.get("title") or "-", "eye", subtitle=_meta(selected))
        try:
            data = api.policy_file(selected["id"])
            total = _page_count(data)
        except ApiError as err:
            render_html(f'<div class="empty-box">{escape(err.message)}</div>')
            return
        except Exception:
            render_html('<div class="empty-box">PDF를 열 수 없어요.</div>')
            return
        key = _page_key(selected["id"])
        current = min(st.session_state.get(key, 0), total - 1)

        with st.container(key="pdf_page_view"):
            st.image(_render_page(data, current), width="stretch")

        with st.container(key="pdf_pager", horizontal=True, horizontal_alignment="center",
                          vertical_alignment="center", gap="small"):
            st.button("이전", icon=":material/chevron_left:", key="pdf_prev", disabled=current == 0,
                      on_click=_move_page, args=(selected["id"], -1, total))
            render_html(f'<span class="pdf-page-no">{current + 1} / {total}</span>')
            st.button("다음", icon=":material/chevron_right:", icon_position="right", key="pdf_next",
                      disabled=current >= total - 1, on_click=_move_page, args=(selected["id"], 1, total))