import pandas as pd
import streamlit as st

from components.ui import icon, page_header, pagination, render_html
from utils import api
from utils.api import fmt_time
from utils.inquiry import categories, category, items_of, list_signature, status_label, total_pages
from utils.live import live_watch
from utils.navigation import go
from utils.session import load


STATUS_TABS = ["전체", "검토대기", "답변완료"]
TAB_CODE = {"검토대기": "pending", "전체": "all", "답변완료": "done"}   
PAGE_SIZE = 100   

COLUMNS = [
    "문의번호",
    "고객명",
    "문의 유형",
    "상태",
    "상품명",
    "이메일",
    "연락처",
    "등록일자",
    "답변완료 시간",
]

def _status_style(value: str) -> str:
    if value == "검토대기":
        return "color:#D85F12;font-weight:700"

    return "color:#15924a;font-weight:600"


def _ellipsis(value: str, max_length: int) -> str:
    value = str(value or "-")

    if len(value) <= max_length:
        return value

    return value[: max_length - 1] + "…"

def _set_page(n: int) -> None:
    st.session_state.review_page = n


def _reset_page() -> None:
    st.session_state.review_page = 1


def render() -> None:
    page_header(
        "문의 검토",
        "AI가 답변하지 못한 문의를 확인하고 답변을 승인해 주세요.",
    )

    st.session_state.setdefault("review_status", "검토대기")
    st.session_state.setdefault("review_type", "전체")
    st.session_state.setdefault("review_page", 1)

    tab = TAB_CODE.get(st.session_state.review_status or "검토대기", "pending")
    cat = None if st.session_state.review_type in (None, "전체") else st.session_state.review_type
    q = (st.session_state.get("review_search") or "").strip() or None
    page = st.session_state.review_page

    res = load(api.list_reviews, tab, q, cat, page, PAGE_SIZE)
    live_watch("review", lambda: list_signature(api.list_reviews(tab, q, cat, page, PAGE_SIZE)),
               initial=list_signature(res))

    raw_counts = res.get("counts") or {}
    counts = {label: raw_counts.get(code, 0) for label, code in TAB_CODE.items()}

    if counts["검토대기"]:
        render_html(
            f"""
            <div class="alert-box">
                {icon("bell-ring")}
                <span>
                    AI가 답변하지 못한 문의
                    <b>{counts["검토대기"]}건</b>이
                    검토를 기다리고 있어요.
                </span>
            </div>
            """
        )

    with st.container(key="card_review_filters"):
        f1, f2 = st.columns(
            [1, 1.3],
            vertical_alignment="bottom",
        )

        with f1:
            status = (
                st.segmented_control(
                    "문의 상태",
                    STATUS_TABS,
                    key="review_status",
                    format_func=lambda s: f"{s} {counts[s]}",
                    on_change=_reset_page,
                )
                or "검토대기"
            )

            keyword = st.text_input(
                "검색",
                placeholder="고객명, 문의번호, 상품명 검색",
                icon=":material/search:",
                key="review_search",
                on_change=_reset_page,
            )

        with f2:
            inquiry_type = (
                st.pills(
                    "문의 유형",
                    ["전체", *categories()],
                    key="review_type",
                    on_change=_reset_page,
                )
                or "전체"
            )


    items = items_of(res)
    total = total_pages(res, PAGE_SIZE)

    with st.container(key="card_review_table"):
        render_html(
            f"""
            <p class="table-caption">
                <b>{len(items)}건</b>
                · 행의 아무 칸이나 클릭하면 상세 화면으로 이동해요.
            </p>
            """
        )

        if not items:
         
            return

        df = pd.DataFrame(
            [
                {
                    "문의번호": i["inquiry_no"],
                    "고객명": i.get("customer_name") or "-",
                    "문의 유형": category(i),
                    "상태": status_label(i),

                    # 긴 값만 말줄임
                    "상품명": _ellipsis(
                        i.get("product_name"),
                        14,
                    ),
                    "이메일": _ellipsis(
                        i.get("customer_email"),
                        18,
                    ),

                    "연락처": i.get("customer_phone") or "-",
                    "등록일자": fmt_time(i.get("created_at")),
                    "답변완료 시간": ("-" if i.get("status_code") == "REVIEWING"
                                      else fmt_time(i.get("answered_at"))),
                }
                for i in items
            ],
            columns=COLUMNS,
        )

        event = st.dataframe(
            df.style.map(
                _status_style,
                subset=["상태"],
            ),

            key="review_table",
            hide_index=True,

            width="stretch",
            
            column_config={
                "문의번호": st.column_config.TextColumn(
                    "문의번호",
                    width=125,
                ),

                "고객명": st.column_config.TextColumn(
                    "고객명",
                    width=70,
                ),

                "문의 유형": st.column_config.TextColumn(
                    "문의 유형",
                    width=85,
                ),

                "상태": st.column_config.TextColumn(
                    "상태",
                    width=75,
                ),

                "상품명": st.column_config.TextColumn(
                    "상품명",
                    width=145,
                ),

                "이메일": st.column_config.TextColumn(
                    "이메일",
                    width=155,
                ),

                "연락처": st.column_config.TextColumn(
                    "연락처",
                    width=120,
                ),

                "등록일자": st.column_config.TextColumn(
                    "등록일자",
                    width=135,
                ),

                "답변완료 시간": st.column_config.TextColumn(
                    "답변완료 시간",
                    width=140,
                ),
            },

            on_select="rerun",
            selection_mode="single-cell",

           height="stretch", 
        )
        pagination(page, total, _set_page)

        if event.selection.cells:
            row, _ = event.selection.cells[0]

            inquiry_id = df.iloc[row]["문의번호"]

            go(
                "admin_detail",
                id=inquiry_id,
            )