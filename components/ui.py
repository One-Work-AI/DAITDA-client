from html import escape

import streamlit as st

LUCIDE_URL = "https://cdn.jsdelivr.net/npm/lucide-static@0.469.0/icons/{name}.svg"

BADGE_TONE = {
    "검토대기": "warning", "답변완료": "success", "AI 답변": "brand", "관리자 답변": "dark",
    "상담 중": "success", "검토 중": "warning", "상담 종료": "neutral",
}


def icon(name: str, size: int | str = "1.15em", color: str = "currentColor") -> str:
    """SVG를 mask로 씌워서 글자색(currentColor)을 따라가게 함. 기본 크기는 글자 크기 기준(em)."""
    url = LUCIDE_URL.format(name=name)
    size = f"{size}px" if isinstance(size, int) else size
    return (
        f'<span class="icon" style="width:{size};height:{size};background-color:{color};'
        f'-webkit-mask-image:url({url});mask-image:url({url});"></span>'
    )


def render_html(markup: str) -> None:
    lines = (line.strip() for line in markup.strip().splitlines())
    st.markdown(" ".join(line for line in lines if line), unsafe_allow_html=True)


def text(value: str) -> str:
    return escape(value or "").replace("\n", "<br>")


def badge(label: str, tone: str | None = None) -> str:
    tone = tone or BADGE_TONE.get(label, "neutral")
    return f'<span class="badge badge-{tone}">{escape(label)}</span>'


def resolved_badge(inquiry: dict) -> str:
    by = inquiry.get("resolved_by")
    return badge("AI 답변" if by == "AI" else "관리자 답변") if by else ""


def type_pill(label: str) -> str:
    return f'<span class="type-pill">{escape(label)}</span>'


def brand() -> str:
    return f'<div class="brand"><span class="brand-mark">{icon("shopping-bag", 15)}</span><span>daitda</span></div>'


def page_header(title: str, subtitle: str = "", right: str = "") -> None:
    render_html(f"""
        <div class="page-header">
          <div><h1>{escape(title)}</h1><p>{escape(subtitle)}</p></div>
          <span class="page-header-right">{escape(right)}</span>
        </div>
    """)


def card_title(title: str, icon_name: str | None = None, subtitle: str = "", right: str = "") -> None:
    ic = f'<span class="card-title-icon">{icon(icon_name)}</span>' if icon_name else ""
    sub = f'<p class="card-subtitle">{escape(subtitle)}</p>' if subtitle else ""
    render_html(f"""
        <div class="card-head">
          <div class="card-head-left">{ic}<div><h3 class="card-title">{escape(title)}</h3>{sub}</div></div>
          <div class="card-head-right">{right}</div>
        </div>
    """)


def kv_table(rows: list[tuple[str, str]]) -> None:
    """rows: (label, html_value)"""
    body = "".join(f"<tr><th>{escape(k)}</th><td>{v}</td></tr>" for k, v in rows)
    render_html(f'<table class="kv-table">{body}</table>')


def info_grid(items: list[tuple[str, str]]) -> None:
    """요약 정보 그리드 (모바일에서는 2열). items: (label, html_value)"""
    cells = "".join(f'<div class="info-cell"><span>{escape(k)}</span><b>{v}</b></div>' for k, v in items)
    render_html(f'<div class="info-grid">{cells}</div>')

ROLE_META = {
    "ai": ("AI 상담사", "sparkles"),
    "admin": ("담당자 답변", "headset"),
}


def bubble_html(msg: dict) -> str:
    role = msg["role"]
    time = escape(msg.get("at", "")[-5:])
    if role == "customer":
        return (f'<div class="msg-row customer"><span class="msg-time">{time}</span>'
                f'<div class="bubble">{text(msg["content"])}</div></div>')
    if role == "system":
        return f'<div class="msg-row system"><div class="bubble">{text(msg["content"])}</div></div>'
    name, ic = ROLE_META.get(role, ROLE_META["ai"])
    edited = (f'<span class="msg-edited">수정됨 · {escape(msg["edited_at"][-5:])}</span>'
              if msg.get("edited_at") else "")
    return (f'<div class="msg-row {role}"><span class="msg-avatar">{icon(ic)}</span>'
            f'<div class="msg-body"><span class="msg-name">{name}</span>'
            f'<div class="msg-line"><div class="bubble">{text(msg["content"])}</div>'
            f'<span class="msg-time">{edited}{time}</span></div></div></div>')


def typing_bubble_html() -> str:
    return (f'<div class="msg-row ai"><span class="msg-avatar">{icon("sparkles")}</span>'
            f'<div class="msg-body"><span class="msg-name">AI 상담사</span>'
            f'<div class="bubble typing"><span></span><span></span><span></span>'
            f'<em>답변을 준비하고 있어요</em></div></div></div>')


def transcript(messages: list[dict]) -> None:
    render_html(f'<div class="transcript">{"".join(bubble_html(m) for m in messages)}</div>')