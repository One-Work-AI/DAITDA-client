from collections import Counter
import altair as alt
import pandas as pd
import streamlit as st

from components.ui import card_title, icon, page_header, render_html
from data.dummy import HOURLY, INQUIRY_TYPES, PEAK_ALERT
from utils.inquiry import change_signature, now
from utils.live import live_watch
from utils.store import inquiries as all_inquiries

SHARE_COLORS = ["#D85F12", "#F37321", "#F89B5C", "#FBC49C", "#D9D9D9"]
INFLOW_COLOR, DONE_COLOR = "#F37321", "#FBC49C"


def render() -> None:
    page_header("운영 대시보드", "문의 현황을 한눈에 확인하세요.", right=f"{now():%Y.%m.%d %H:%M} 기준")
    inquiries = all_inquiries()
    live_watch("dashboard", lambda: tuple(change_signature(i) for i in all_inquiries()), interval=5)
    _render_kpis(inquiries)

    _render_type_share(inquiries)
    _render_hourly()


def _render_kpis(inquiries: list[dict]) -> None:
    total = len(inquiries)
    waiting = sum(i["status"] == "검토대기" for i in inquiries)
    done = total - waiting
    by_ai = sum(i.get("resolved_by") == "AI" for i in inquiries)
    by_admin = sum(i.get("resolved_by") == "관리자" for i in inquiries)
    ai_rate = round(by_ai / total * 100) if total else 0

    kpis = [
        ("전체 문의", "inbox", total, "건", '<span class="muted">채팅 종료 후 저장된 문의</span>'),
        ("검토대기", "clipboard-list", waiting, "건", '<span class="badge badge-warning">AI 미답변</span>'),
        ("답변완료", "circle-check", done, "건", f'<span class="muted">AI {by_ai}건 · 관리자 {by_admin}건</span>'),
        ("AI 자동 응답률", "sparkles", ai_rate, "%", '<span class="kpi-up">관리자 개입 없이 해결</span>'),
    ]
    cards = "".join(f"""
        <div class="kpi-card">
          <div class="kpi-head"><span>{label}</span><span class="kpi-icon">{icon(ic)}</span></div>
          <div class="kpi-value">{value}<small>{unit}</small></div>
          <div class="kpi-sub">{sub}</div>
        </div>""" for label, ic, value, unit, sub in kpis)
    render_html(f'<div class="kpi-grid">{cards}</div>')


def _render_type_share(inquiries: list[dict]) -> None:
    total = len(inquiries) or 1
    counts = Counter(i["type"] for i in inquiries)
    share = [(t, counts.get(t, 0), round(counts.get(t, 0) / total * 100)) for t in INQUIRY_TYPES]
    with st.container(key="card_type_share"):
        card_title("문의 유형별 비중", subtitle=f"총 {len(inquiries)}건 기준",
                   right='<span class="badge badge-brand">실시간</span>')
        bar = "".join(f'<span style="width:{r}%;background:{c}"></span>' for (_, _, r), c in zip(share, SHARE_COLORS))
        rows = "".join(f"""
            <li><span class="dot" style="background:{c}"></span><b>{t}</b><span class="share-desc"></span>
              <span class="share-count">{n}건</span><span class="share-ratio">{r}%</span></li>
        """ for (t, n, r), c in zip(share, SHARE_COLORS))
        render_html(f'<div class="stack-bar">{bar}</div><ul class="share-list">{rows}</ul>')


def _render_hourly() -> None:
    legend = (f'<span class="legend"><span class="dot" style="background:{INFLOW_COLOR}"></span>인입량'
              f'<span class="dot" style="background:{DONE_COLOR}"></span>처리완료</span>')
    with st.container(key="card_hourly"):
        card_title("시간대별 인입 및 처리 현황", subtitle="영업시간 (09:00 ~ 18:00) · 샘플 데이터", right=legend)
        st.altair_chart(_hourly_chart(), width="stretch")
        render_html(f'<div class="alert-box">{icon("info")}<span><b>피크 타임 알림:</b> {PEAK_ALERT}</span></div>')


def _hourly_chart() -> alt.LayerChart:
    df = pd.DataFrame(HOURLY).fillna({"peak": False})
    hours = df["hour"].tolist()
    long = df.melt(id_vars=["hour"], value_vars=["inflow", "done"], var_name="kind", value_name="count")
    long["kind"] = long["kind"].map({"inflow": "인입량", "done": "처리완료"})
    peak = df[df["peak"]].assign(top=df["inflow"].max() + 6,
                                 label=lambda d: d["inflow"].astype(str) + "/" + d["done"].astype(str))

    x = alt.X("hour:N", sort=hours, title=None, axis=alt.Axis(labelAngle=0, domain=False, ticks=False))
    band = alt.Chart(peak).mark_bar(color="#FFF4EC", cornerRadius=6, width=alt.RelativeBandSize(0.9)).encode(
        x=x, y=alt.Y("top:Q", axis=None))
    label = alt.Chart(peak).mark_text(dy=-6, fontWeight="bold", color="#D85F12", fontSize=11).encode(
        x=x, y="top:Q", text="label:N")
    bars = alt.Chart(long).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
        x=x,
        xOffset=alt.XOffset("kind:N", sort=["인입량", "처리완료"]),
        y=alt.Y("count:Q", axis=None),
        color=alt.Color("kind:N", scale=alt.Scale(domain=["인입량", "처리완료"], range=[INFLOW_COLOR, DONE_COLOR]),
                        legend=None),
        tooltip=[alt.Tooltip("hour", title="시간"), alt.Tooltip("kind", title="구분"),
                 alt.Tooltip("count", title="건수")],
    )
    return (alt.layer(band, bars, label).properties(height=230)
            .configure_view(strokeWidth=0).configure_axis(grid=False, labelColor="#6b7280"))