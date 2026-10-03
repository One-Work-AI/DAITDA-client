from html import escape

import streamlit as st

from components.ui import badge, card_title, kv_table, render_html, resolved_badge, text, transcript
from utils.inquiry import (admin_messages, answer_question, change_signature, customer_status,
                           edit_admin_message, first_question, pending_questions, waiting_minutes)
from utils.live import live_watch
from utils.navigation import go
from utils.session import current_user, customer_inquiries, get_inquiry


def render() -> None:


    inquiry = get_inquiry(st.query_params.get("id"))
    if inquiry is None:
        st.warning("문의를 찾을 수 없어요.")
        return
    live_watch(f"admin_{inquiry['id']}", lambda: change_signature(get_inquiry(inquiry["id"])))

    head, info_btn = st.columns([4, 1.1], vertical_alignment="center")
    with head:
        render_html(f"""
            <div class="detail-head">
              <div class="detail-head-left"><span class="detail-id">#{inquiry["id"]}</span>
                {badge(inquiry["status"])} {resolved_badge(inquiry)}
                <span class="muted">고객: {customer_status(inquiry)} · 접수일 {inquiry["created_at"]}</span></div>
            </div>
        """)
    with info_btn:
        if st.button("고객 · 문의 정보", icon=":material/person_search:", width="stretch", key="open_info"):
            _info_dialog(inquiry["id"])

    left, right = st.columns([1.25, 1], gap="medium")
    with left, st.container(key="card_admin_transcript"):
        sub = (f"{inquiry['end_reason']} · {inquiry['ended_at']}" if inquiry.get("ended_at")
               else "고객이 채팅 중이에요 · 새 메시지는 자동으로 표시돼요")
        card_title("채팅 내역", "messages-square", subtitle=sub)
        with st.container(height=520, key="admin_transcript_scroll"):
            transcript(inquiry["messages"])

    with right:
        if inquiry["status"] == "검토대기":
            _render_wait_info(inquiry)
        _render_review(inquiry)

    _render_previous(inquiry)


@st.dialog("고객 · 문의 정보")
def _info_dialog(inquiry_id: str) -> None:
    inquiry = get_inquiry(inquiry_id)
    kv_table([
        ("고객명", escape(inquiry["customer"])),
        ("이메일", escape(inquiry["email"])),
        ("연락처", escape(inquiry["phone"])),
        ("문의 유형", inquiry["type"]),
        ("상품명", escape(inquiry["product"])),
        ("주문번호", inquiry.get("order_no") or "-"),
        ("CS 번호", inquiry.get("cs_no") or "-"),
        ("접수일", inquiry["created_at"]),
        ("답변완료 시간", inquiry["answered_at"] or "-"),
        ("상담 종료", f'{inquiry.get("end_reason") or "-"} {inquiry.get("ended_at") or ""}'),
    ])


def _render_wait_info(inquiry: dict) -> None:
    wait = waiting_minutes(inquiry)
    reasons = "".join(f"<li>{escape(r)}</li>" for r in inquiry.get("review_reasons") or ["사유 미기록"])
    with st.container(key="card_admin_wait"):
        card_title("검토 요청 정보", "alarm-clock",
                   right=f'<span class="badge badge-warning">대기 {wait if wait is not None else "-"}분</span>')
        render_html(f'<p class="field-label">검토로 넘어온 이유</p><ul class="reason-list">{reasons}</ul>')


def _render_review(inquiry: dict) -> None:
    with st.container(key="card_admin_review"):
        questions = pending_questions(inquiry) if inquiry["status"] == "검토대기" else []

        head, pager = st.columns([3, 1.3], vertical_alignment="center")
        with head:
            card_title("AI 답변 · 관리자 검토", "sparkles")
        if len(questions) > 1:
            with pager, st.container(key="q_pager", horizontal=True, horizontal_alignment="right",
                                     vertical_alignment="center", gap="small"):
                idx = _question_index(inquiry["id"], len(questions))
                st.button("", icon=":material/chevron_left:", key="q_prev", type="tertiary", disabled=idx == 0,
                          on_click=_move_question, args=(inquiry["id"], -1, len(questions)))
                render_html(f'<span class="q-page-no">{idx + 1} / {len(questions)}</span>')
                st.button("", icon=":material/chevron_right:", key="q_next", type="tertiary",
                          disabled=idx >= len(questions) - 1,
                          on_click=_move_question, args=(inquiry["id"], 1, len(questions)))

        if inquiry["status"] == "검토대기":
            if not questions:
                render_html('<div class="empty-box">답변할 질문이 없어요.</div>')
                return
            q = questions[_question_index(inquiry["id"], len(questions))]
            render_html(f'<p class="q-line"><b>Q.</b> {text(q["content"])}</p>')
            render_html('<p class="field-label">AI 답변 초안</p>')
            render_html(f'<div class="content-box">{text(q.get("ai_draft") or inquiry.get("ai_draft", ""))}</div>')
            draft_key = f"draft_q_{q['id']}"
            st.session_state.setdefault(draft_key, q.get("ai_draft") or inquiry.get("ai_draft", ""))
            st.text_area("최종 답변 (검토 후 수정)", key=draft_key, height=180)
            st.button("승인하기", icon=":material/check_circle:", type="primary", width="stretch",
                      key=f"approve_{q['id']}", on_click=_send_answer, args=(inquiry["id"], q["id"]))
            return

        answers = admin_messages(inquiry)
        if not answers:
            render_html('<div class="answer-box soft">AI 상담사가 채팅에서 바로 답변한 문의예요. '
                        "왼쪽 채팅 내역에서 AI 답변을 확인할 수 있어요.</div>")
            return

        latest = answers[-1]
        edited = f" · 수정됨 {latest['edited_at']}" if latest.get("edited_at") else ""
        render_html(f'<div class="answer-box"><span class="answer-label">{escape(latest.get("author", "관리자"))} 답변 · '
                    f'{latest["at"]}{edited}</span><div>{text(latest["content"])}</div></div>')

        edit_key = f"edit_{latest['id']}"
        if st.toggle("답변 수정하기", key=f"edit_toggle_{latest['id']}"):
            st.session_state.setdefault(edit_key, latest["content"])
            st.text_area("수정할 답변", key=edit_key, height=160)
            st.button("수정 저장", icon=":material/save:", type="primary", width="stretch",
                      key=f"save_edit_{latest['id']}", on_click=_save_edit, args=(inquiry["id"], latest["id"]))


def _question_index(inquiry_id: str, total: int) -> int:
    key = f"q_idx_{inquiry_id}"
    st.session_state[key] = min(max(st.session_state.get(key, 0), 0), total - 1)
    return st.session_state[key]


def _move_question(inquiry_id: str, step: int, total: int) -> None:
    key = f"q_idx_{inquiry_id}"
    st.session_state[key] = min(max(st.session_state.get(key, 0) + step, 0), total - 1)


def _send_answer(inquiry_id: str, question_id: str) -> None:
    answer = st.session_state.get(f"draft_q_{question_id}", "").strip()
    if not answer:
        st.toast("답변 내용을 입력해 주세요.", icon=":material/error:")
        return
    remaining = answer_question(get_inquiry(inquiry_id), question_id, answer, current_user()["name"])
    st.session_state.pop(f"draft_q_{question_id}", None)
    st.toast("모든 질문에 답변했어요. 답변완료로 변경돼요." if remaining == 0
             else f"답변을 보냈어요. 남은 질문 {remaining}건", icon=":material/check_circle:")


def _save_edit(inquiry_id: str, message_id: str) -> None:
    new_text = st.session_state.get(f"edit_{message_id}", "").strip()
    if not new_text:
        st.toast("답변 내용을 입력해 주세요.", icon=":material/error:")
        return
    edit_admin_message(get_inquiry(inquiry_id), message_id, new_text, current_user()["name"])
    st.session_state.pop(f"edit_{message_id}", None)
    st.session_state[f"edit_toggle_{message_id}"] = False
    st.toast("답변을 수정했어요. 고객 화면에 '수정됨'으로 표시돼요.", icon=":material/edit:")


def _toggle_previous() -> None:
    st.session_state.prev_open = not st.session_state.get("prev_open", False)


def _render_previous(inquiry: dict) -> None:
    previous = [i for i in customer_inquiries(inquiry["customer"]) if i["id"] != inquiry["id"]]
    is_open = st.session_state.get("prev_open", False)
    with st.container(key="card_admin_previous"):
        head, action = st.columns([8, 1], vertical_alignment="center")
        with head:
            card_title("이전 문의 내역", "history", subtitle=f"{inquiry['customer']} 고객의 다른 문의 {len(previous)}건")
        if not previous:
            return
        with action, st.container(key="prev_toggle_wrap", horizontal=True, horizontal_alignment="right"):
            st.button("", icon=":material/keyboard_arrow_up:" if is_open else ":material/keyboard_arrow_down:",
                      key="prev_toggle", type="tertiary", on_click=_toggle_previous)
        if not is_open:       
            return
        with st.container(key="admin_previous_list"):
            for prev in previous:
                label = f"{prev['created_at']} · {prev['type']} · {prev['status']} — {first_question(prev)[:30]}"
                with st.expander(label, key=f"prev_exp_{prev['id']}"):
                    with st.container(key=f"prev_scroll_{prev['id']}", height=260):
                        transcript(prev["messages"])
