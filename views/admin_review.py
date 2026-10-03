import pandas as pd
import streamlit as st

from components.ui import icon, page_header, render_html
from data.dummy import INQUIRY_TYPES
from utils.inquiry import change_signature, latest_activity
from utils.live import live_watch
from utils.navigation import go
from utils.store import inquiries as all_inquiries


STATUS_TABS = ["검토대기", "전체", "답변완료"]

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

def render() -> None:
    page_header(
        "문의 검토",
        "AI가 답변하지 못한 문의를 확인하고 답변을 승인해 주세요.",
    )

    inquiries = all_inquiries()

    live_watch(
        "review",
        lambda: tuple(
            change_signature(i)
            for i in all_inquiries()
        ),
    )

    counts = {
        "검토대기": sum(
            i["status"] == "검토대기"
            for i in inquiries
        ),
        "전체": len(inquiries),
        "답변완료": sum(
            i["status"] == "답변완료"
            for i in inquiries
        ),
    }

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

    st.session_state.setdefault(
        "review_status",
        "검토대기",
    )

    st.session_state.setdefault(
        "review_type",
        "전체",
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
                )
                or "검토대기"
            )

            keyword = st.text_input(
                "검색",
                placeholder="고객명, 문의번호, 상품명 검색",
                icon=":material/search:",
                key="review_search",
            )

        with f2:
            inquiry_type = (
                st.pills(
                    "문의 유형",
                    ["전체", *INQUIRY_TYPES],
                    key="review_type",
                )
                or "전체"
            )


    if status == "전체":
        items = inquiries
    else:
        items = [
            i
            for i in inquiries
            if i["status"] == status
        ]

    if inquiry_type != "전체":
        items = [
            i
            for i in items
            if i["type"] == inquiry_type
        ]

    if keyword:
        items = [
            i
            for i in items
            if (
                keyword in i["customer"]
                or keyword in i["id"]
                or keyword in i["product"]
            )
        ]

    items = sorted(items, key=latest_activity, reverse=True) 

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
            st.info("조건에 맞는 문의가 없어요.")
            return

        df = pd.DataFrame(
            [
                {
                    "문의번호": i["id"],
                    "고객명": i["customer"],
                    "문의 유형": i["type"],
                    "상태": i["status"],

                    # 긴 값만 말줄임
                    "상품명": _ellipsis(
                        i["product"],
                        14,
                    ),
                    "이메일": _ellipsis(
                        i["email"],
                        18,
                    ),

                    "연락처": i["phone"],
                    "등록일자": i["created_at"],
                    "답변완료 시간": (
                        i["answered_at"]
                        or "-"
                    ),
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

        if event.selection.cells:
            row, _ = event.selection.cells[0]

            inquiry_id = df.iloc[row]["문의번호"]

            go(
                "admin_detail",
                id=inquiry_id,
            )