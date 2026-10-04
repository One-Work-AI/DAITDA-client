from datetime import datetime, timedelta, timezone
from html import escape

import altair as alt
import pandas as pd
import streamlit as st

from components.ui import card_title, icon, page_header, render_html
from utils import api
from utils.inquiry import categories
from utils.live import live_watch
from utils.session import load

BUSINESS_HOURS = range(9, 18)  


def now() -> datetime:
    return datetime.now(timezone(timedelta(hours=9)))


def _signature(d: dict) -> tuple:
    a = d.get("answered") or {}
    return (d.get("total_inquiries"), d.get("pending_review"), a.get("ai"), a.get("admin"),
            tuple((c.get("name"), c.get("count")) for c in d.get("by_category") or []))

SHARE_COLORS = ["#D85F12", "#F37321", "#F89B5C", "#FBC49C", "#D9D9D9"]
INFLOW_COLOR, DONE_COLOR = "#F37321", "#FBC49C"


def render() -> None:
    page_header("운영 대시보드", "문의 현황을 한눈에 확인하세요.", right=f"{now():%Y.%m.%d %H:%M} 기준")
    data = load(api.dashboard)
    live_watch("dashboard", lambda: _signature(api.dashboard()), interval=5, initial=_signature(data))
    _render_kpis(data)

    _render_type_share(data)
    _render_hourly(data)


def _render_kpis(data: dict) -> None:
    answered = data.get("answered") or {}
    total = data.get("total_inquiries", 0)
    waiting = data.get("pending_review", 0)
    done = answered.get("total", 0)
    by_ai = answered.get("ai", 0)
    by_admin = answered.get("admin", 0)
    rate = data.get("ai_auto_rate") or 0
    ai_rate = round(rate * 100) if rate <= 1 else round(rate)

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


def _render_type_share(data: dict) -> None:
    rows = {c.get("name"): c for c in data.get("by_category") or []}
    total_count = sum(c.get("count", 0) for c in rows.values())
    names = [*categories(), *[n for n in rows if n and n not in categories()]]
    share = []
    for t in names:
        n = (rows.get(t) or {}).get("count", 0)
        ratio = (rows.get(t) or {}).get("ratio")
        r = round(ratio * 100) if ratio is not None and ratio <= 1 else round(ratio or (n / total_count * 100 if total_count else 0))
        share.append((t, n, r))
    with st.container(key="card_type_share"):
        card_title("문의 유형별 비중", subtitle=f"총 {total_count}건 기준",
                   right='<span class="badge badge-brand">실시간</span>')
        bar = "".join(f'<span style="width:{r}%;background:{c}"></span>' for (_, _, r), c in zip(share, SHARE_COLORS))
        rows = "".join(f"""
            <li><span class="dot" style="background:{c}"></span><b>{t}</b><span class="share-desc"></span>
              <span class="share-count">{n}건</span><span class="share-ratio">{r}%</span></li>
        """ for (t, n, r), c in zip(share, SHARE_COLORS))
        render_html(f'<div class="stack-bar">{bar}</div><ul class="share-list">{rows}</ul>')


def _render_hourly(data: dict) -> None:
    legend = (f'<span class="legend"><span class="dot" style="background:{INFLOW_COLOR}"></span>인입량'
              f'<span class="dot" style="background:{DONE_COLOR}"></span>처리완료</span>')
    with st.container(key="card_hourly"):
        card_title("시간대별 인입 및 처리 현황", subtitle="영업시간 (09:00 ~ 18:00)", right=legend)
        st.altair_chart(_hourly_chart(data), width="stretch")
        peak = _peak_alert(data)
        if peak:
            render_html(f'<div class="alert-box">{icon("info")}<span><b>피크 타임 알림:</b> {peak}</span></div>')


def _hourly_rows(data: dict) -> list[dict]:
    """API hourly(0~23시, received/answered) → 화면용 (09~17시, inflow/done, peak)."""
    by_hour = {int(h.get("hour", -1)): h for h in data.get("hourly") or []}
    peak = data.get("peak_window") or {}
    start, end = peak.get("start_hour"), peak.get("end_hour")
    return [{"hour": f"{h:02d}시", "inflow": by_hour.get(h, {}).get("received", 0),
             "done": by_hour.get(h, {}).get("answered", 0),
             "peak": start is not None and end is not None and start <= h < end} for h in BUSINESS_HOURS]


def _peak_alert(data: dict) -> str | None:
    peak = data.get("peak_window") or {}
    if peak.get("start_hour") is None or peak.get("end_hour") is None:
        return None
    top = peak.get("top_category")
    return (f'{peak["start_hour"]:02d}:00 ~ {peak["end_hour"]:02d}:00 구간 '
            f'{escape(top) + " " if top else ""}문의 집중')


def _hourly_chart(data: dict) -> alt.LayerChart:
    df = pd.DataFrame(_hourly_rows(data)).fillna({"peak": False})
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