import streamlit as st

from components.ui import brand, icon, render_html
from utils.navigation import HOME_PAGE, go
from utils.session import current_user, login


FEATURES = [
    (
        "package-check",
        "주문 · 배송",
        "주문 상태와 배송 정보를 빠르게 확인해요.",
    ),
    (
        "refresh-ccw",
        "교환 · 환불",
        "신청 방법부터 진행 과정까지 안내해요.",
    ),
    (
        "messages-square",
        "AI 고객 상담",
        "문의 내용을 분석해 필요한 답변을 안내해요.",
    ),
]


DEMO_ACCOUNTS = [
    ("고객으로 체험", "customer@daitda.com", ":material/person:"),
    ("관리자로 체험", "admin@daitda.com", ":material/admin_panel_settings:"),
]


def _go_home() -> None:
    go(HOME_PAGE[current_user()["role"]])


def render() -> None:
    with st.container(key="login_layout"):
        intro_col, form_col = st.columns([1, 1.35], gap="large")

        with intro_col, st.container(key="login_intro"):
            features = "".join(
                f"""
                <li>
                    <span class="feature-icon">
                        {icon(ic)}
                    </span>

                    <div class="feature-content">
                        <b>{title}</b>
                        <p>{description}</p>
                    </div>
                </li>
                """
                for ic, title, description in FEATURES
            )

            render_html(brand())

            render_html(
                f"""
                <div class="login-intro-body">

                    <div class="login-eyebrow">
                        {icon("sparkles")}
                        <span>AI CUSTOMER SERVICE</span>
                    </div>

                    <h1 class="login-headline">
                        궁금한 쇼핑 문의,<br>
                        <span>DAITDA</span>에게 물어보세요
                    </h1>

                    <p class="login-lead">
                        주문부터 배송, 결제, 교환·환불까지<br>
                        필요한 답변을 빠르게 확인해보세요.
                    </p>

                    <ul class="login-features">
                        {features}
                    </ul>

                </div>
                """
            )

            render_html('<p class="login-copy">© 2026 DAITDA</p>')

        with form_col, st.container(key="login_panel"):
            with st.container(key="login_box"):
                render_html(
                    """
                    <h2 class="login-title">로그인</h2>
                    """
                )

                with st.form("login_form", border=False):
                    email = st.text_input(
                        "이메일",
                        placeholder="name@example.com",
                    )

                    password = st.text_input(
                        "비밀번호",
                        type="password",
                        placeholder="비밀번호 입력",
                    )

                    submitted = st.form_submit_button(
                        "로그인",
                        type="primary",
                        width="stretch",
                    )

                if submitted:
                    if not email or not password:
                        render_html(
                            f'<p class="field-error">'
                            f'{icon("circle-alert")}'
                            "<span>이메일과 비밀번호를 모두 입력해주세요.</span>"
                            "</p>"
                        )

                    elif login(email, password):
                        _go_home()

                    else:
                        render_html(
                            f'<p class="field-error">'
                            f'{icon("circle-alert")}'
                            "<span>이메일 또는 비밀번호가 올바르지 않습니다.</span>"
                            "</p>"
                        )

                render_html(
                    '<div class="login-divider">'
                    "<span>데모 계정으로 바로 체험</span>"
                    "</div>"
                )

                c1, c2 = st.columns(2)

                for col, (label, email_, ic) in zip(
                    (c1, c2),
                    DEMO_ACCOUNTS,
                ):
                    if col.button(
                        label,
                        icon=ic,
                        key=f"demo_{email_}",
                        width="stretch",
                    ):
                        login(email_, "1234")
                        _go_home()

                render_html(
                    f'<p class="login-hint">'
                    f'{icon("key-round")}'
                    "<span>데모 계정 비밀번호는 1234입니다</span>"
                    "</p>"
                )