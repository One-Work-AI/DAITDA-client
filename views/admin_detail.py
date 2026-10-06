# """관리자 - 문의 상세. 화면 구성은 그대로, 데이터는 GET /api/admin/reviews/{문의번호}

# - 검토대기 질문: questions 중 status == REVIEW_PENDING (여러 개면 1/N으로 넘겨봄)
# - 승인하기: POST /api/admin/reviews/{문의번호}/questions/{question_id}/approve
# - 이전 문의 내역: previous_inquiries (펼치면 각 문의의 채팅을 불러옴)
# """
# from datetime import datetime, timezone
# from html import escape

# import streamlit as st

# from components.ui import badge, card_title, kv_table, render_html, resolved_badge, text, transcript
# from utils import api
# from utils.api import fmt_time, to_kst
# from utils.inquiry import admin_messages, category, change_signature, status_label
# from utils.live import live_watch
# from utils.navigation import go
# from utils.session import load, run_action


# # ---------------------------------------------------------------- API 응답 → 화면 값
# def get_inquiry(inquiry_no: str) -> dict:
#     return load(api.get_review, inquiry_no, not_found="문의를 찾을 수 없어요.")


# def customer_status(inquiry: dict) -> str:
#     return "상담 종료" if inquiry.get("chat_status") == "CLOSED" else "상담 중"


# def pending_questions(inquiry: dict) -> list[dict]:
#     return [q for q in inquiry.get("questions") or [] if q.get("status") == "REVIEW_PENDING"]


# def waiting_minutes(inquiry: dict) -> int | None:
#     times = [to_kst(q.get("created_at")) for q in pending_questions(inquiry)]
#     times = [t for t in times if t]
#     if not times:
#         return None
#     return int((datetime.now(timezone.utc) - min(times)).total_seconds() // 60)


# def review_reasons(inquiry: dict) -> list[str]:
#     labels = []
#     for q in pending_questions(inquiry):
#         for r in (q.get("analysis") or {}).get("reasons") or []:
#             label = r.get("label") or r.get("code")
#             if label and label not in labels:
#                 labels.append(label)
#     return labels


# def _draft(q: dict) -> str:
#     return (q.get("ai_draft") or {}).get("text") or ""


# def _resolved(inquiry: dict) -> dict:
#     if inquiry.get("status_code") != "ANSWERED":
#         return {}
#     return {"answered_by": "ADMIN" if admin_messages(inquiry) else "AI"}


# def _author(inquiry: dict, msg: dict) -> str:
#     q = next((q for q in inquiry.get("questions") or [] if q.get("question_id") == msg.get("question_id")), None)
#     return ((q or {}).get("review") or {}).get("admin_name") or "관리자"


# def render() -> None:


#     inquiry_no = st.query_params.get("id")
#     if not inquiry_no:
#         st.warning("문의를 찾을 수 없어요.")
#         return
#     inquiry = get_inquiry(inquiry_no)
#     inquiry["id"] = inquiry["inquiry_no"]
#     live_watch(f"admin_{inquiry['id']}", lambda: change_signature(api.get_review(inquiry_no)),
#                initial=change_signature(inquiry))

#     head, info_btn = st.columns([4, 1.1], vertical_alignment="center")
#     with head:
#         render_html(f"""
#             <div class="detail-head">
#               <div class="detail-head-left"><span class="detail-id">#{inquiry["id"]}</span>
#                 {badge(status_label(inquiry))} {resolved_badge(_resolved(inquiry))}
#                 <span class="muted">고객: {customer_status(inquiry)} · 접수일 {fmt_time(inquiry["created_at"])}</span></div>
#             </div>
#         """)
#     with info_btn:
#         if st.button("고객 · 문의 정보", icon=":material/person_search:", width="stretch", key="open_info"):
#             _info_dialog(inquiry)

#     left, right = st.columns([1.25, 1], gap="medium")
#     with left, st.container(key="card_admin_transcript"):
#         sub = (f"{inquiry.get('close_reason_label') or '종료'} · {fmt_time(inquiry['closed_at'])}"
#                if inquiry.get("chat_status") == "CLOSED" and inquiry.get("closed_at")
#                else "고객이 채팅 중이에요 · 새 메시지는 자동으로 표시돼요")
#         card_title("채팅 내역", "messages-square", subtitle=sub)
#         with st.container(height=520, key="admin_transcript_scroll"):
#             transcript(inquiry["messages"])

#     with right:
#         if inquiry["status_code"] == "REVIEWING":
#             _render_wait_info(inquiry)
#         _render_review(inquiry)

#     _render_previous(inquiry)


# @st.dialog("고객 · 문의 정보")
# def _info_dialog(inquiry: dict) -> None:
#     customer = inquiry.get("customer") or {}
#     kv_table([
#         ("고객명", escape(customer.get("name") or "-")),
#         ("이메일", escape(customer.get("email") or "-")),
#         ("연락처", escape(customer.get("phone") or "-")),
#         ("문의 유형", escape(category(inquiry))),
#         ("상품명", escape(inquiry.get("product_name") or "-")),
#         ("주문번호", escape(inquiry.get("order_no") or "-")),
#         ("접수일", fmt_time(inquiry["created_at"])),
#         ("답변완료 시간", "-" if inquiry.get("status_code") == "REVIEWING" else fmt_time(inquiry.get("answered_at"))),
#         ("상담 종료", f'{escape(inquiry.get("close_reason_label") or "-")} {fmt_time(inquiry.get("closed_at"), empty="")}'),
#     ])


# def _render_wait_info(inquiry: dict) -> None:
#     wait = waiting_minutes(inquiry)
#     reasons = "".join(f"<li>{escape(r)}</li>" for r in review_reasons(inquiry) or ["사유 미기록"])
#     with st.container(key="card_admin_wait"):
#         card_title("검토 요청 정보", "alarm-clock",
#                    right=f'<span class="badge badge-warning">대기 {wait if wait is not None else "-"}분</span>')
#         render_html(f'<p class="field-label">검토로 넘어온 이유</p><ul class="reason-list">{reasons}</ul>')


# def review_pages(inquiry: dict) -> list[dict]:
#     return [q for q in inquiry.get("questions") or [] if q.get("status") in ("REVIEW_PENDING", "ADMIN_ANSWERED")]


# def _answer_of(inquiry: dict, question_id) -> dict | None:
#     return next((m for m in reversed(admin_messages(inquiry)) if m.get("question_id") == question_id), None)


# def _render_review(inquiry: dict) -> None:
#     with st.container(key="card_admin_review"):
#         pages = review_pages(inquiry)
#         first_pending = next((i for i, q in enumerate(pages) if q.get("status") == "REVIEW_PENDING"), None)
#         idx_key = f"q_idx_{inquiry['id']}"
#         idx = (_page_index(idx_key, len(pages), default=first_pending if first_pending is not None else len(pages) - 1)
#                if pages else 0)

#         head, pager = st.columns([3, 1.3], vertical_alignment="center")
#         with head:
#             card_title("AI 답변 · 관리자 검토", "sparkles")
#         if len(pages) > 1:
#             with pager, st.container(key="q_pager", horizontal=True, horizontal_alignment="right",
#                                      vertical_alignment="center", gap="small"):
#                 st.button("", icon=":material/chevron_left:", key="q_prev", type="tertiary", disabled=idx == 0,
#                           on_click=_move_page, args=(idx_key, -1, len(pages)))
#                 render_html(f'<span class="q-page-no">{idx + 1} / {len(pages)}</span>')
#                 st.button("", icon=":material/chevron_right:", key="q_next", type="tertiary",
#                           disabled=idx >= len(pages) - 1,
#                           on_click=_move_page, args=(idx_key, 1, len(pages)))

#         if not pages:
#             if inquiry["status_code"] == "REVIEWING":
#                 render_html('<div class="empty-box">답변할 질문이 없어요.</div>')
#             else:
#                 render_html('<div class="answer-box soft">AI 상담사가 채팅에서 바로 답변한 문의예요. '
#                             "왼쪽 채팅 내역에서 AI 답변을 확인할 수 있어요.</div>")
#             return

#         q = pages[idx]
#         answer = _answer_of(inquiry, q["question_id"]) if q.get("status") == "ADMIN_ANSWERED" else None

#         if answer is None:                      
#             render_html(f'<p class="q-line"><b>Q.</b> {text(q["content"])}</p>')
#             render_html('<p class="field-label">AI 답변 초안</p>')
#             render_html(f'<div class="content-box">{text(_draft(q))}</div>')
#             draft_key = f"draft_q_{q['question_id']}"
#             st.session_state.setdefault(draft_key, _draft(q))
#             st.text_area("최종 답변 (검토 후 수정)", key=draft_key, height=180)
#             st.button("승인하기", icon=":material/check_circle:", type="primary", width="stretch",
#                       key=f"approve_{q['question_id']}", on_click=_send_answer,
#                       args=(inquiry["id"], q["question_id"]))
#             return

#         edited = f" · 수정됨 {fmt_time(answer['edited_at'])}" if answer.get("edited_at") else ""
#         render_html(f'<p class="q-line"><b>Q.</b> {text(q["content"])}</p>'
#                     f'<div class="answer-box" style="margin-top:12px"><span class="answer-label">'
#                     f'{escape(_author(inquiry, answer))} 답변 · {fmt_time(answer.get("created_at"))}{edited}</span>'
#                     f'<div>{text(answer["content"])}</div></div>')

#         edit_key = f"edit_{answer['id']}"
#         if st.toggle("답변 수정하기", key=f"edit_toggle_{answer['id']}"):
#             st.session_state.setdefault(edit_key, answer["content"])
#             st.text_area("수정할 답변", key=edit_key, height=160)
#             st.button("수정 저장", icon=":material/save:", type="primary", width="stretch",
#                       key=f"save_edit_{answer['id']}", on_click=_save_edit,
#                       args=(inquiry["id"], answer["question_id"], answer["id"]))


# def _question_of(inquiry: dict, answer: dict) -> str:
#     qid = answer.get("question_id")
#     q = next((q for q in inquiry.get("questions") or [] if q.get("question_id") == qid), None)
#     if q and q.get("content"):
#         return q["content"]
#     msg = next((m for m in inquiry.get("messages") or [] if m.get("role") == "CUSTOMER" and m.get("question_id") == qid), None)
#     return (msg or {}).get("content", "")


# def _page_index(key: str, total: int, default: int = 0) -> int:
#     st.session_state[key] = min(max(st.session_state.get(key, default), 0), total - 1)
#     return st.session_state[key]


# def _move_page(key: str, step: int, total: int) -> None:
#     st.session_state[key] = min(max(st.session_state.get(key, 0) + step, 0), total - 1)


# def _send_answer(inquiry_id: str, question_id: str) -> None:
#     answer = st.session_state.get(f"draft_q_{question_id}", "").strip()
#     if not answer:
#         st.toast("답변 내용을 입력해 주세요.", icon=":material/error:")
#         return
#     ok, result = run_action(api.approve, inquiry_id, question_id, answer,
#                             messages={"NOT_REVIEW_PENDING": "이미 처리된 질문이에요."})
#     st.session_state.pop(f"draft_q_{question_id}", None)
#     if not ok:
#         return
#     remaining = len(pending_questions(result or {}))
#     st.toast("모든 질문에 답변했어요. 답변완료로 변경돼요." if remaining == 0
#              else f"답변을 보냈어요. 남은 질문 {remaining}건", icon=":material/check_circle:")


# def _save_edit(inquiry_id: str, question_id: int, message_id: str) -> None:
#     new_text = st.session_state.get(f"edit_{message_id}", "").strip()
#     if not new_text:
#         st.toast("답변 내용을 입력해 주세요.", icon=":material/error:")
#         return
#     ok, _ = run_action(api.edit_answer, inquiry_id, question_id, new_text)
#     if not ok:
#         return
#     st.session_state.pop(f"edit_{message_id}", None)
#     st.session_state[f"edit_toggle_{message_id}"] = False
#     st.toast("답변을 수정했어요. 고객 화면에 '수정됨'으로 표시돼요.", icon=":material/edit:")


# def _toggle_previous() -> None:
#     st.session_state.prev_open = not st.session_state.get("prev_open", False)


# def _render_previous(inquiry: dict) -> None:
#     previous = inquiry.get("previous_inquiries") or []
#     is_open = st.session_state.get("prev_open", False)
#     with st.container(key="card_admin_previous"):
#         head, action = st.columns([8, 1], vertical_alignment="center")
#         with head:
#             name = (inquiry.get("customer") or {}).get("name") or "고객"
#             card_title("이전 문의 내역", "history", subtitle=f"{name} 고객의 다른 문의 {len(previous)}건")
#         if not previous:
#             return
#         with action, st.container(key="prev_toggle_wrap", horizontal=True, horizontal_alignment="right"):
#             st.button("", icon=":material/keyboard_arrow_up:" if is_open else ":material/keyboard_arrow_down:",
#                       key="prev_toggle", type="tertiary", on_click=_toggle_previous)
#         if not is_open:       
#             return
#         with st.container(key="admin_previous_list"):
#             for prev in previous:
#                 prev_no = prev["inquiry_no"]
#                 label = (f"{fmt_time(prev['created_at'])} · {category(prev)} · {status_label(prev)}"
#                          f" — {(prev.get('preview') or '')[:30]}")
#                 with st.expander(label, key=f"prev_exp_{prev_no}"):
#                     with st.container(key=f"prev_scroll_{prev_no}", height=260):
#                         transcript(_previous_messages(prev_no))


# def _previous_messages(inquiry_no: str) -> list[dict]:
#     try:
#         return api.get_review(inquiry_no).get("messages") or []
#     except api.ApiError:
#         return []

"""관리자 - 문의 상세. 화면 구성은 그대로, 데이터는 GET /api/admin/reviews/{문의번호}

- 검토대기 질문: questions 중 status == REVIEW_PENDING (여러 개면 1/N으로 넘겨봄)
- 승인하기: POST /api/admin/reviews/{문의번호}/questions/{question_id}/approve
- 이전 문의 내역: previous_inquiries (펼치면 각 문의의 채팅을 불러옴)
"""
from datetime import datetime, timezone
from html import escape

import streamlit as st

from components.ui import badge, card_title, kv_table, render_html, resolved_badge, text, transcript
from utils import api
from utils.api import fmt_time, to_kst
from utils.inquiry import admin_messages, category, category_intents, change_signature, status_label
from utils.live import live_watch
from utils.navigation import go
from utils.session import load, run_action


# ---------------------------------------------------------------- API 응답 → 화면 값
def get_inquiry(inquiry_no: str) -> dict:
    return load(api.get_review, inquiry_no, not_found="문의를 찾을 수 없어요.")


def customer_status(inquiry: dict) -> str:
    return "상담 종료" if inquiry.get("chat_status") == "CLOSED" else "상담 중"


def pending_questions(inquiry: dict) -> list[dict]:
    return [q for q in inquiry.get("questions") or [] if q.get("status") == "REVIEW_PENDING"]


def waiting_minutes(inquiry: dict) -> int | None:
    times = [to_kst(q.get("created_at")) for q in pending_questions(inquiry)]
    times = [t for t in times if t]
    if not times:
        return None
    return int((datetime.now(timezone.utc) - min(times)).total_seconds() // 60)


def review_reasons(inquiry: dict) -> list[str]:
    labels = []
    for q in pending_questions(inquiry):
        for r in (q.get("analysis") or {}).get("reasons") or []:
            label = r.get("label") or r.get("code")
            if label and label not in labels:
                labels.append(label)
    return labels


def _draft(q: dict) -> str:
    return (q.get("ai_draft") or {}).get("text") or ""


def _resolved(inquiry: dict) -> dict:
    if inquiry.get("status_code") != "ANSWERED":
        return {}
    return {"answered_by": "ADMIN" if admin_messages(inquiry) else "AI"}


def _author(inquiry: dict, msg: dict) -> str:
    q = next((q for q in inquiry.get("questions") or [] if q.get("question_id") == msg.get("question_id")), None)
    return ((q or {}).get("review") or {}).get("admin_name") or "관리자"


def render() -> None:


    inquiry_no = st.query_params.get("id")
    if not inquiry_no:
        st.warning("문의를 찾을 수 없어요.")
        return
    inquiry = get_inquiry(inquiry_no)
    inquiry["id"] = inquiry["inquiry_no"]
    live_watch(f"admin_{inquiry['id']}", lambda: change_signature(api.get_review(inquiry_no)),
               initial=change_signature(inquiry))

    head, info_btn = st.columns([4, 1.1], vertical_alignment="center")
    with head:
        render_html(f"""
            <div class="detail-head">
              <div class="detail-head-left"><span class="detail-id">#{inquiry["id"]}</span>
                {badge(status_label(inquiry))} {resolved_badge(_resolved(inquiry))}
                <span class="muted">고객: {customer_status(inquiry)} · 접수일 {fmt_time(inquiry["created_at"])}</span></div>
            </div>
        """)
    with info_btn:
        if st.button("고객 · 문의 정보", icon=":material/person_search:", width="stretch", key="open_info"):
            _info_dialog(inquiry)

    left, right = st.columns([1.25, 1], gap="medium")
    with left, st.container(key="card_admin_transcript"):
        sub = (f"{inquiry.get('close_reason_label') or '종료'} · {fmt_time(inquiry['closed_at'])}"
               if inquiry.get("chat_status") == "CLOSED" and inquiry.get("closed_at")
               else "고객이 채팅 중이에요 · 새 메시지는 자동으로 표시돼요")
        card_title("채팅 내역", "messages-square", subtitle=sub)
        with st.container(height=520, key="admin_transcript_scroll"):
            transcript(inquiry["messages"])

    with right:
        if inquiry["status_code"] == "REVIEWING":
            _render_wait_info(inquiry)
        _render_review(inquiry)

    _render_previous(inquiry)


@st.dialog("고객 · 문의 정보")
def _info_dialog(inquiry: dict) -> None:
    customer = inquiry.get("customer") or {}
    kv_table([
        ("고객명", escape(customer.get("name") or "-")),
        ("이메일", escape(customer.get("email") or "-")),
        ("연락처", escape(customer.get("phone") or "-")),
        ("문의 유형", escape(category(inquiry))),
        ("상품명", escape(inquiry.get("product_name") or "-")),
        ("주문번호", escape(inquiry.get("order_no") or "-")),
        ("접수일", fmt_time(inquiry["created_at"])),
        ("답변완료 시간", "-" if inquiry.get("status_code") == "REVIEWING" else fmt_time(inquiry.get("answered_at"))),
        ("상담 종료", f'{escape(inquiry.get("close_reason_label") or "-")} {fmt_time(inquiry.get("closed_at"), empty="")}'),
    ])


def _render_wait_info(inquiry: dict) -> None:
    wait = waiting_minutes(inquiry)
    reasons = "".join(f"<li>{escape(r)}</li>" for r in review_reasons(inquiry) or ["사유 미기록"])
    with st.container(key="card_admin_wait"):
        card_title("검토 요청 정보", "alarm-clock",
                   right=f'<span class="badge badge-warning">대기 {wait if wait is not None else "-"}분</span>')
        render_html(f'<p class="field-label">검토로 넘어온 이유</p><ul class="reason-list">{reasons}</ul>')


def review_pages(inquiry: dict) -> list[dict]:
    return [q for q in inquiry.get("questions") or [] if q.get("status") in ("REVIEW_PENDING", "ADMIN_ANSWERED")]


def _answer_of(inquiry: dict, question_id) -> dict | None:
    return next((m for m in reversed(admin_messages(inquiry)) if m.get("question_id") == question_id), None)


def _render_review(inquiry: dict) -> None:
    with st.container(key="card_admin_review"):
        pages = review_pages(inquiry)
        first_pending = next((i for i, q in enumerate(pages) if q.get("status") == "REVIEW_PENDING"), None)
        idx_key = f"q_idx_{inquiry['id']}"
        idx = (_page_index(idx_key, len(pages), default=first_pending if first_pending is not None else len(pages) - 1)
               if pages else 0)

        head, pager = st.columns([3, 1.3], vertical_alignment="center")
        with head:
            card_title("AI 답변 · 관리자 검토", "sparkles")
        if len(pages) > 1:
            with pager, st.container(key="q_pager", horizontal=True, horizontal_alignment="right",
                                     vertical_alignment="center", gap="small"):
                st.button("", icon=":material/chevron_left:", key="q_prev", type="tertiary", disabled=idx == 0,
                          on_click=_move_page, args=(idx_key, -1, len(pages)))
                render_html(f'<span class="q-page-no">{idx + 1} / {len(pages)}</span>')
                st.button("", icon=":material/chevron_right:", key="q_next", type="tertiary",
                          disabled=idx >= len(pages) - 1,
                          on_click=_move_page, args=(idx_key, 1, len(pages)))

        if not pages:
            if inquiry["status_code"] == "REVIEWING":
                render_html('<div class="empty-box">답변할 질문이 없어요.</div>')
            else:
                render_html('<div class="answer-box soft">AI 상담사가 채팅에서 바로 답변한 문의예요. '
                            "왼쪽 채팅 내역에서 AI 답변을 확인할 수 있어요.</div>")
            return

        q = pages[idx]
        answer = _answer_of(inquiry, q["question_id"]) if q.get("status") == "ADMIN_ANSWERED" else None

        if answer is None:                      
            render_html(f'<p class="q-line"><b>Q.</b> {text(q["content"])}</p>')
            render_html('<p class="field-label">AI 답변 초안</p>')
            render_html(f'<div class="content-box">{text(_draft(q))}</div>')
            draft_key = f"draft_q_{q['question_id']}"
            st.session_state.setdefault(draft_key, _draft(q))
            st.text_area("최종 답변 (검토 후 수정)", key=draft_key, height=180)
            _label_inputs(q)
            st.button("승인하기", icon=":material/check_circle:", type="primary", width="stretch",
                      key=f"approve_{q['question_id']}", on_click=_send_answer,
                      args=(inquiry["id"], q["question_id"]))
            return

        edited = f" · 수정됨 {fmt_time(answer['edited_at'])}" if answer.get("edited_at") else ""
        render_html(f'<p class="q-line"><b>Q.</b> {text(q["content"])}</p>'
                    f'<div class="answer-box" style="margin-top:12px"><span class="answer-label">'
                    f'{escape(_author(inquiry, answer))} 답변 · {fmt_time(answer.get("created_at"))}{edited}</span>'
                    f'<div>{text(answer["content"])}</div></div>')

        edit_key = f"edit_{answer['id']}"
        if st.toggle("답변 수정하기", key=f"edit_toggle_{answer['id']}"):
            st.session_state.setdefault(edit_key, answer["content"])
            st.text_area("수정할 답변", key=edit_key, height=160)
            st.button("수정 저장", icon=":material/save:", type="primary", width="stretch",
                      key=f"save_edit_{answer['id']}", on_click=_save_edit,
                      args=(inquiry["id"], answer["question_id"], answer["id"]))


def _question_of(inquiry: dict, answer: dict) -> str:
    qid = answer.get("question_id")
    q = next((q for q in inquiry.get("questions") or [] if q.get("question_id") == qid), None)
    if q and q.get("content"):
        return q["content"]
    msg = next((m for m in inquiry.get("messages") or [] if m.get("role") == "CUSTOMER" and m.get("question_id") == qid), None)
    return (msg or {}).get("content", "")


def _page_index(key: str, total: int, default: int = 0) -> int:
    st.session_state[key] = min(max(st.session_state.get(key, default), 0), total - 1)
    return st.session_state[key]


def _move_page(key: str, step: int, total: int) -> None:
    st.session_state[key] = min(max(st.session_state.get(key, 0) + step, 0), total - 1)


def _labels_valid(q: dict, ci: dict[str, list[str]]) -> bool:
    a = q.get("analysis") or {}
    return a.get("category") in ci and a.get("intent") in ci.get(a.get("category"), [])


def _label_inputs(q: dict) -> None:
    """분류 수정 · 학습 데이터 · 메모 (선택). AI 분류가 없거나 잘못된 질문은 분류를 골라야 승인 가능."""
    ci = category_intents()
    if not ci:
        return
    qid = q["question_id"]
    a = q.get("analysis") or {}
    valid = _labels_valid(q, ci)
    cat_key, intent_key = f"cat_q_{qid}", f"intent_q_{qid}"
    st.session_state.setdefault(cat_key, a.get("category") if valid else None)

    with st.expander("분류 · 학습 데이터" + ("" if valid else " (분류 필요)"), expanded=not valid):
        if not valid:
            st.warning("AI 분류 결과가 없거나 잘못됐어요. 승인하려면 카테고리와 의도를 골라 주세요.",
                       icon=":material/warning:")
        st.selectbox("카테고리", list(ci), key=cat_key, placeholder="카테고리 선택")
        options = ci.get(st.session_state.get(cat_key)) or []
        if st.session_state.get(intent_key) not in options:      # 카테고리를 바꾸면 의도를 다시 고름
            st.session_state[intent_key] = a.get("intent") if a.get("intent") in options else None
        st.selectbox("의도", options, key=intent_key, placeholder="의도 선택")
        st.checkbox("학습 데이터로 사용", key=f"train_q_{qid}")
        st.text_input("관리자 메모 (선택)", key=f"remark_q_{qid}", max_chars=1000)


def _send_answer(inquiry_id: str, question_id: str) -> None:
    answer = st.session_state.get(f"draft_q_{question_id}", "").strip()
    if not answer:
        st.toast("답변 내용을 입력해 주세요.", icon=":material/error:")
        return
    cat = st.session_state.get(f"cat_q_{question_id}")
    intent = st.session_state.get(f"intent_q_{question_id}")
    if bool(cat) != bool(intent):
        st.toast("카테고리와 의도를 함께 골라 주세요.", icon=":material/error:")
        return
    ok, result = run_action(api.approve, inquiry_id, question_id, answer,
                            category=cat, intent=intent,
                            use_for_training=bool(st.session_state.get(f"train_q_{question_id}")),
                            remark=st.session_state.get(f"remark_q_{question_id}"),
                            messages={"NOT_REVIEW_PENDING": "이미 처리된 질문이에요.",
                                      "LABEL_REQUIRED": "AI 분류가 없는 질문이에요. 카테고리와 의도를 골라 주세요.",
                                      "VALIDATION_ERROR": "카테고리와 의도 조합을 확인해 주세요."})
    if not ok:
        return          # 실패하면 작성한 답변을 지우지 않음
    for k in ("draft_q_", "cat_q_", "intent_q_", "train_q_", "remark_q_"):
        st.session_state.pop(f"{k}{question_id}", None)
    remaining = len(pending_questions(result or {}))
    st.toast("모든 질문에 답변했어요. 답변완료로 변경돼요." if remaining == 0
             else f"답변을 보냈어요. 남은 질문 {remaining}건", icon=":material/check_circle:")


def _save_edit(inquiry_id: str, question_id: int, message_id: str) -> None:
    new_text = st.session_state.get(f"edit_{message_id}", "").strip()
    if not new_text:
        st.toast("답변 내용을 입력해 주세요.", icon=":material/error:")
        return
    ok, _ = run_action(api.edit_answer, inquiry_id, question_id, new_text)
    if not ok:
        return
    st.session_state.pop(f"edit_{message_id}", None)
    st.session_state[f"edit_toggle_{message_id}"] = False
    st.toast("답변을 수정했어요. 고객 화면에 '수정됨'으로 표시돼요.", icon=":material/edit:")


def _toggle_previous() -> None:
    st.session_state.prev_open = not st.session_state.get("prev_open", False)


def _render_previous(inquiry: dict) -> None:
    previous = inquiry.get("previous_inquiries") or []
    is_open = st.session_state.get("prev_open", False)
    with st.container(key="card_admin_previous"):
        head, action = st.columns([8, 1], vertical_alignment="center")
        with head:
            name = (inquiry.get("customer") or {}).get("name") or "고객"
            card_title("이전 문의 내역", "history", subtitle=f"{name} 고객의 다른 문의 {len(previous)}건")
        if not previous:
            return
        with action, st.container(key="prev_toggle_wrap", horizontal=True, horizontal_alignment="right"):
            st.button("", icon=":material/keyboard_arrow_up:" if is_open else ":material/keyboard_arrow_down:",
                      key="prev_toggle", type="tertiary", on_click=_toggle_previous)
        if not is_open:       
            return
        with st.container(key="admin_previous_list"):
            for prev in previous:
                prev_no = prev["inquiry_no"]
                label = (f"{fmt_time(prev['created_at'])} · {category(prev)} · {status_label(prev)}"
                         f" — {(prev.get('preview') or '')[:30]}")
                with st.expander(label, key=f"prev_exp_{prev_no}"):
                    with st.container(key=f"prev_scroll_{prev_no}", height=260):
                        transcript(_previous_messages(prev_no))


def _previous_messages(inquiry_no: str) -> list[dict]:
    try:
        return api.get_review(inquiry_no).get("messages") or []
    except api.ApiError:
        return []
