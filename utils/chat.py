"""고객 채팅: 더미 AI 응답 + 자동 종료 계산. 실제 AI 연동 시 ai_reply()만 AI팀 API 호출로 교체."""
import os

from utils.inquiry import now

AUTO_CLOSE_SECONDS = int(os.environ.get("DAITDA_AUTO_CLOSE", 5 * 60))
WELCOME = "안녕하세요, daitda 고객센터 AI 상담사예요. 주문·배송·교환/환불 등 궁금한 점을 편하게 물어봐 주세요."
FAQ = [
    (["배송", "언제", "도착", "출고", "택배"],
     "주문하신 상품은 결제 완료 후 영업일 기준 1~2일 내 출고되고, 출고 후 1~2일 내에 도착해요. "
     "실시간 위치는 [주문 내역 > 배송 조회]에서 확인할 수 있어요."),
    (["교환", "반품", "사이즈"],
     "상품 수령 후 7일 이내라면 [주문 내역 > 교환/반품 신청]에서 바로 접수할 수 있어요. "
     "단순 변심은 왕복 배송비가 부과돼요."),
    (["환불"], "환불은 상품 회수가 완료된 뒤 영업일 기준 3~5일 내에 결제 수단으로 돌아가요."),
    (["결제 취소", "주문 취소", "취소"],
     "출고 전 주문은 [주문 내역 > 주문 취소]에서 바로 취소할 수 있어요. 카드 결제는 즉시 승인 취소돼요."),
    (["배송지", "옵션", "변경"], "출고 전이라면 [주문 내역]에서 배송지와 옵션을 직접 변경할 수 있어요."),
    (["쿠폰", "적립", "포인트"],
     "보유 쿠폰과 적립금은 [마이 > 쿠폰/적립금]에서 확인할 수 있어요. 결제 단계에서 적용 버튼을 눌러 주세요."),
    (["감사", "고마"], "도움이 되어 다행이에요. 더 궁금한 점이 있으면 언제든 물어봐 주세요."),
]
REVIEW_RULES = [
    (["파손", "불량", "오배송", "누락", "분실"], "상품 하자·배송 사고 – 사진/택배사 확인 필요"),
    (["두 번", "중복"], "중복 결제 – 결제 내역 확인 필요"),
    (["상담원", "사람", "직원"], "고객이 상담원 연결 요청"),
    (["보상"], "보상 요청 – 관리자 판단 필요"),
    (["이미 출고"], "출고 후 취소 – 정책 예외 판단 필요"),
    (["안 들어", "안들어"], "환불·입금 지연 – 처리 내역 확인 필요"),
]
NO_ANSWER_REASON = "AI가 답변할 수 있는 정책 정보 없음"

QUICK_PROMPTS = ["주문한 상품 언제 도착하나요?", "교환/반품은 어떻게 하나요?", "결제 취소하고 싶어요"]


def ai_reply(message: str) -> tuple[str, bool, str | None]:
    for words, reason in REVIEW_RULES:
        if any(word in message for word in words):
            return "", True, reason
    for words, answer in FAQ:
        if any(word in message for word in words):
            return answer, False, None
    return "", True, NO_ANSWER_REASON

HEARTBEAT_GAP_SECONDS = 12


def _timer_paused(inquiry: dict | None) -> bool:
    return (inquiry is None
            or inquiry.get("chat_state") == "ended"
            or inquiry["status"] == "검토대기"             
            or inquiry.get("awaiting_customer_view", False))  


def seconds_left(inquiry: dict | None) -> int | None:
    if _timer_paused(inquiry):
        return None
    return max(0, int(inquiry.get("timer_left", AUTO_CLOSE_SECONDS)))


def tick_timer(inquiry: dict | None) -> int | None:
    from utils.store import lock
    if inquiry is None:
        return None
    with lock():
        current = now()
        if _timer_paused(inquiry):
            inquiry["timer_heartbeat"] = None
            return None
        inquiry.setdefault("timer_left", AUTO_CLOSE_SECONDS)
        last = inquiry.get("timer_heartbeat")
        if last is not None:
            gap = (current - last).total_seconds()
            if gap <= HEARTBEAT_GAP_SECONDS:           
                inquiry["timer_left"] = max(0.0, inquiry["timer_left"] - gap)
        inquiry["timer_heartbeat"] = current
        return int(inquiry["timer_left"])


def pause_timer(inquiry: dict | None) -> None:
    from utils.store import lock
    if inquiry is not None:
        with lock():
            inquiry["timer_heartbeat"] = None


def reset_timer(inquiry: dict) -> None:
    inquiry["timer_left"] = float(AUTO_CLOSE_SECONDS)
    inquiry["timer_heartbeat"] = now()
