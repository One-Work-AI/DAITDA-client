# """더미 데이터. 추후 DB/API 연동 시 이 파일만 교체하면 됩니다."""
# from pathlib import Path

# SERVICE_NAME = "daitda"
# POLICY_DIR = Path(__file__).resolve().parent / "policies"

# CURRENT_CUSTOMER = {
#     "name": "김민지",
#     "email": "kimminji@email.com",
#     "phone": "010-1234-5678",
# }
# CURRENT_ADMIN = {"name": "관리자", "email": "admin@daitda.com", "phone": "-"}

# # 데모 계정 (실서비스에서는 해시된 비밀번호 + DB 사용)
# USERS = {
#     "customer@daitda.com": {"password": "1234", "role": "customer", **CURRENT_CUSTOMER},
#     "admin@daitda.com": {"password": "1234", "role": "admin", **CURRENT_ADMIN},
# }

# INQUIRY_TYPES = ["배송", "결제", "교환/환불", "주문", "기타"]
# STATUSES = ["검토대기", "답변완료"]   # 검토대기: AI가 답변하지 못해 관리자 확인 필요 / 답변완료

# # 고객의 최근 주문 (채팅에서 문의할 상품 선택용)
# ORDERS = [
#     {"order_no": "20241210-1234567", "product": "무선 블루투스 이어폰 Pro"},
#     {"order_no": "20241208-7654321", "product": "데일리 코튼 니트 (베이지, M)"},
#     {"order_no": "20241205-1122334", "product": "스테인리스 텀블러 500ml"},
# ]

# # ---------------- 정책 문서 (PDF) ----------------
# POLICIES = [
#     {"id": "POL-001", "title": "배송 정책 · 배송 기간 안내", "desc": "출고 기준일, 배송 소요 기간, 지연 안내 기준",
#      "file_name": "delivery_policy.pdf", "uploaded_at": "2024.12.02 10:20"},
#     {"id": "POL-002", "title": "교환 · 환불 정책", "desc": "신청 기한, 배송비 부담 기준, 환불 소요 기간",
#      "file_name": "refund_policy.pdf", "uploaded_at": "2024.12.05 09:41"},
#     {"id": "POL-003", "title": "결제 · 취소 정책", "desc": "결제 수단별 취소 시점과 중복 결제 처리 기준",
#      "file_name": "payment_policy.pdf", "uploaded_at": "2024.11.18 15:02"},
# ]


# # ---------------- 문의 (채팅 단위) ----------------
# def _m(role: str, at: str, content: str) -> dict:
#     return {"role": role, "at": at, "content": content}


# _KIM = {"customer": "김민지", "email": "kimminji@email.com", "phone": "010-1234-5678"}
# _HANDOFF = "확인이 필요한 내용이라 담당자에게 전달했어요. 검토 후 [문의 내역]에서 답변을 확인하실 수 있어요."

# INQUIRIES = [
#     # ---- 김민지 ----
#     {"id": "Q20241210-001", "cs_no": "CS2412100001", **_KIM, "product": "무선 블루투스 이어폰 Pro",
#      "order_no": "20241210-1234567", "type": "배송", "status": "답변완료", "resolved_by": "AI",
#      "created_at": "2024.12.10 14:30", "answered_at": "2024.12.10 14:30", "ended_at": "2024.12.10 14:36",
#      "end_reason": "고객 종료",
#      "messages": [
#          _m("customer", "2024.12.10 14:30", "주문한 이어폰 언제 배송되나요? 주문번호 20241210-1234567이에요."),
#          _m("ai", "2024.12.10 14:30", "주문하신 상품은 현재 배송 준비 중이며 내일(12/11) 택배사로 인계될 예정이에요. "
#                                       "인계 후 보통 1~2일 내에 받아보실 수 있어요."),
#          _m("customer", "2024.12.10 14:35", "네 감사합니다!"),
#          _m("ai", "2024.12.10 14:35", "도움이 되어 다행이에요. 더 궁금한 점이 있으면 언제든 물어봐 주세요."),
#      ]},
#     {"id": "Q20241208-002", "cs_no": "CS2412080002", **_KIM, "product": "데일리 코튼 니트 (베이지, M)",
#      "order_no": "20241208-7654321", "type": "결제", "status": "검토대기", "resolved_by": None,
#      "created_at": "2024.12.08 10:15", "answered_at": None, "ended_at": "2024.12.08 10:21", "end_reason": "자동 종료",
#      "messages": [
#          _m("customer", "2024.12.08 10:15", "이미 출고됐다고 나오는데 결제 취소가 가능한가요? 다른 상품으로 다시 주문하고 싶어요."),
#          _m("ai", "2024.12.08 10:15", _HANDOFF),
#      ]},
#     {"id": "Q20241205-003", "cs_no": "CS2412050003", **_KIM, "product": "스테인리스 텀블러 500ml",
#      "order_no": "20241205-1122334", "type": "교환/환불", "status": "답변완료", "resolved_by": "관리자",
#      "created_at": "2024.12.05 09:20", "answered_at": "2024.12.05 13:02", "ended_at": "2024.12.05 09:27",
#      "end_reason": "고객 종료",
#      "messages": [
#          _m("customer", "2024.12.05 09:20", "텀블러 뚜껑이 처음부터 금이 가 있어요. 교환 가능할까요?"),
#          _m("ai", "2024.12.05 09:20", _HANDOFF),
#          _m("admin", "2024.12.05 13:02", "불편을 드려 죄송합니다. 불량 상품으로 확인되어 무상 교환으로 접수해 드렸어요. "
#                                          "내일 회수 기사님이 방문 예정이며 회수 배송비는 부담하지 않으셔도 됩니다."),
#      ]},
#     {"id": "Q20241201-004", "cs_no": "CS2412010004", **_KIM, "product": "-", "order_no": None,
#      "type": "주문", "status": "답변완료", "resolved_by": "AI",
#      "created_at": "2024.12.01 16:45", "answered_at": "2024.12.01 16:45", "ended_at": "2024.12.01 16:52",
#      "end_reason": "자동 종료",
#      "messages": [
#          _m("customer", "2024.12.01 16:45", "배송지를 회사 주소로 바꾸고 싶어요."),
#          _m("ai", "2024.12.01 16:45", "출고 전 주문은 [주문 내역 > 배송지 변경]에서 직접 바꾸실 수 있어요. "
#                                       "이미 출고된 경우에는 택배사 고객센터를 통해 변경해야 해요."),
#      ]},
#     # ---- 다른 고객 ----
#     {"id": "Q20241210-005", "cs_no": "CS2412100005", "customer": "박서연", "email": "seoyeon.park@email.com",
#      "phone": "010-2345-6789", "product": "에어프라이어 5.5L", "order_no": "20241209-5551234", "type": "결제",
#      "status": "검토대기", "resolved_by": None, "created_at": "2024.12.10 15:40", "answered_at": None,
#      "ended_at": "2024.12.10 15:46", "end_reason": "고객 종료",
#      "messages": [
#          _m("customer", "2024.12.10 15:40", "같은 주문이 카드로 두 번 결제됐어요. 확인 부탁드려요."),
#          _m("ai", "2024.12.10 15:40", _HANDOFF),
#      ]},
#     {"id": "Q20241210-006", "cs_no": "CS2412100006", "customer": "김하늘", "email": "haneul@email.com",
#      "phone": "010-3456-7890", "product": "세라믹 머그컵 2P 세트", "order_no": "20241207-3332211",
#      "type": "교환/환불", "status": "검토대기", "resolved_by": None, "created_at": "2024.12.10 13:05",
#      "answered_at": None, "ended_at": "2024.12.10 13:12", "end_reason": "자동 종료",
#      "messages": [
#          _m("customer", "2024.12.10 13:05", "받은 머그컵 하나가 파손되어 왔어요."),
#          _m("ai", "2024.12.10 13:05", _HANDOFF),
#          _m("customer", "2024.12.10 13:07", "사진도 보낼 수 있나요?"),
#          _m("ai", "2024.12.10 13:07", "담당자가 확인 후 사진 접수 방법을 함께 안내해 드릴게요."),
#      ]},
#     {"id": "Q20241210-007", "cs_no": "CS2412100007", "customer": "이준호", "email": "junho.lee@email.com",
#      "phone": "010-4567-8901", "product": "러닝화 에어 270 (260)", "order_no": "20241130-9988776",
#      "type": "교환/환불", "status": "답변완료", "resolved_by": "관리자", "created_at": "2024.12.10 11:20",
#      "answered_at": "2024.12.10 12:05", "ended_at": "2024.12.10 11:24", "end_reason": "고객 종료",
#      "messages": [
#          _m("customer", "2024.12.10 11:20", "반품 접수한 지 일주일이 지났는데 환불이 안 들어왔어요."),
#          _m("ai", "2024.12.10 11:20", _HANDOFF),
#          _m("admin", "2024.12.10 12:05", "확인 결과 회수가 어제 완료되어 오늘 환불 처리되었습니다. 카드사에 따라 3~5일 내 반영돼요."),
#      ]},
#     {"id": "Q20241209-008", "cs_no": "CS2412090008", "customer": "최지훈", "email": "jihoon@email.com",
#      "phone": "010-5678-9012", "product": "기계식 키보드 텐키리스", "order_no": "20241209-4445556",
#      "type": "주문", "status": "답변완료", "resolved_by": "AI", "created_at": "2024.12.09 16:40",
#      "answered_at": "2024.12.09 16:40", "ended_at": "2024.12.09 16:47", "end_reason": "자동 종료",
#      "messages": [
#          _m("customer", "2024.12.09 16:40", "주문한 키보드 색상을 화이트로 바꿀 수 있나요?"),
#          _m("ai", "2024.12.09 16:40", "출고 전이라 옵션 변경이 가능해요. [주문 내역 > 옵션 변경]에서 화이트로 바꿔 주세요."),
#      ]},
#     {"id": "Q20241209-009", "cs_no": "CS2412090009", "customer": "정다은", "email": "daeun@email.com",
#      "phone": "010-6789-0123", "product": "-", "order_no": None, "type": "기타", "status": "검토대기",
#      "resolved_by": None, "created_at": "2024.12.09 13:20", "answered_at": None,
#      "ended_at": "2024.12.09 13:26", "end_reason": "고객 종료",
#      "messages": [
#          _m("customer", "2024.12.09 13:20", "신규 가입 쿠폰이 결제 페이지에서 안 보여요. 상담원 연결해 주세요."),
#          _m("ai", "2024.12.09 13:20", _HANDOFF),
#      ]},
# ]

# # ---------------- 대시보드 (시간대별은 샘플) ----------------
# HOURLY = [
#     {"hour": "09시", "inflow": 14, "done": 12},
#     {"hour": "10시", "inflow": 21, "done": 19},
#     {"hour": "11시", "inflow": 25, "done": 23},
#     {"hour": "12시", "inflow": 17, "done": 18},
#     {"hour": "13시", "inflow": 28, "done": 22, "peak": True},
#     {"hour": "14시", "inflow": 31, "done": 25, "peak": True},
#     {"hour": "15시", "inflow": 12, "done": 11},
#     {"hour": "16시", "inflow": 6, "done": 6},
#     {"hour": "17시", "inflow": 3, "done": 3},
# ]
# PEAK_ALERT = "오늘 13:00 ~ 15:00 구간 배송 문의 집중. 현재 인입 속도 안정화 단계 진입."



# """더미 데이터. 추후 DB/API 연동 시 이 파일만 교체하면 됩니다."""
# from pathlib import Path

# SERVICE_NAME = "daitda"
# POLICY_DIR = Path(__file__).resolve().parent / "policies"

# CURRENT_CUSTOMER = {
#     "name": "김민지",
#     "email": "kimminji@email.com",
#     "phone": "010-1234-5678",
# }
# CURRENT_ADMIN = {"name": "관리자", "email": "admin@daitda.com", "phone": "-"}

# # 데모 계정 (실서비스에서는 해시된 비밀번호 + DB 사용)
# USERS = {
#     "customer@daitda.com": {"password": "1234", "role": "customer", **CURRENT_CUSTOMER},
#     "admin@daitda.com": {"password": "1234", "role": "admin", **CURRENT_ADMIN},
# }

# INQUIRY_TYPES = ["배송", "결제", "교환/환불", "주문", "기타"]
# # 관리자 상태: 검토대기(AI가 답변하지 못해 관리자 확인 필요) / 답변완료
# STATUSES = ["검토대기", "답변완료"]
# # 고객 화면 상태: 상담 중(채팅 진행) / 검토 중(담당자 답변 대기, 입력 잠금) / 상담 종료
# CUSTOMER_STATUSES = ["상담 중", "검토 중", "상담 종료"]

# # 고객의 최근 주문 (채팅에서 문의할 상품 선택용)
# ORDERS = [
#     {"order_no": "20241210-1234567", "product": "무선 블루투스 이어폰 Pro"},
#     {"order_no": "20241208-7654321", "product": "데일리 코튼 니트 (베이지, M)"},
#     {"order_no": "20241205-1122334", "product": "스테인리스 텀블러 500ml"},
# ]

# # ---------------- 정책 문서 (PDF) ----------------
# POLICIES = [
#     {"id": "POL-001", "title": "배송 정책 · 배송 기간 안내", "desc": "출고 기준일, 배송 소요 기간, 지연 안내 기준",
#      "file_name": "delivery_policy.pdf", "uploaded_at": "2024.12.02 10:20"},
#     {"id": "POL-002", "title": "교환 · 환불 정책", "desc": "신청 기한, 배송비 부담 기준, 환불 소요 기간",
#      "file_name": "refund_policy.pdf", "uploaded_at": "2024.12.05 09:41"},
#     {"id": "POL-003", "title": "결제 · 취소 정책", "desc": "결제 수단별 취소 시점과 중복 결제 처리 기준",
#      "file_name": "payment_policy.pdf", "uploaded_at": "2024.11.18 15:02"},
# ]


# # ---------------- 문의 (채팅 단위) ----------------
# def _m(role: str, at: str, content: str) -> dict:
#     return {"role": role, "at": at, "content": content}


# _KIM = {"customer": "김민지", "email": "kimminji@email.com", "phone": "010-1234-5678"}
# _HANDOFF = "담당자가 확인 후 답변드립니다. 답변이 등록되면 이 채팅창에서 이어서 상담할 수 있어요."

# INQUIRIES = [
#     # ---- 김민지 ----
#     {"id": "Q20241210-001", "cs_no": "CS2412100001", **_KIM, "product": "무선 블루투스 이어폰 Pro",
#      "order_no": "20241210-1234567", "type": "배송", "status": "답변완료", "resolved_by": "AI",
#      "created_at": "2024.12.10 14:30", "answered_at": "2024.12.10 14:30", "ended_at": "2024.12.10 14:36",
#      "end_reason": "고객 종료",
#      "messages": [
#          _m("customer", "2024.12.10 14:30", "주문한 이어폰 언제 배송되나요? 주문번호 20241210-1234567이에요."),
#          _m("ai", "2024.12.10 14:30", "주문하신 상품은 현재 배송 준비 중이며 내일(12/11) 택배사로 인계될 예정이에요. "
#                                       "인계 후 보통 1~2일 내에 받아보실 수 있어요."),
#          _m("customer", "2024.12.10 14:35", "네 감사합니다!"),
#          _m("ai", "2024.12.10 14:35", "도움이 되어 다행이에요. 더 궁금한 점이 있으면 언제든 물어봐 주세요."),
#      ]},
#     {"id": "Q20241208-002", "cs_no": "CS2412080002", **_KIM, "product": "데일리 코튼 니트 (베이지, M)",
#      "order_no": "20241208-7654321", "type": "결제", "status": "검토대기", "resolved_by": None, "chat_state": "active",
#      "review_reasons": ["출고 후 결제 취소 – 정책 예외 판단 필요"], "review_wait_min": 12,
#      "created_at": "2024.12.08 10:15", "answered_at": None, "ended_at": None, "end_reason": None,
#      "messages": [
#          _m("customer", "2024.12.08 10:15", "이미 출고됐다고 나오는데 결제 취소가 가능한가요? 다른 상품으로 다시 주문하고 싶어요."),
#          _m("ai", "2024.12.08 10:15", _HANDOFF),
#      ]},
#     {"id": "Q20241205-003", "cs_no": "CS2412050003", **_KIM, "product": "스테인리스 텀블러 500ml",
#      "order_no": "20241205-1122334", "type": "교환/환불", "status": "답변완료", "resolved_by": "관리자",
#      "created_at": "2024.12.05 09:20", "answered_at": "2024.12.05 13:02", "ended_at": "2024.12.05 09:27",
#      "end_reason": "고객 종료",
#      "messages": [
#          _m("customer", "2024.12.05 09:20", "텀블러 뚜껑이 처음부터 금이 가 있어요. 교환 가능할까요?"),
#          _m("ai", "2024.12.05 09:20", _HANDOFF),
#          _m("admin", "2024.12.05 13:02", "불편을 드려 죄송합니다. 불량 상품으로 확인되어 무상 교환으로 접수해 드렸어요. "
#                                          "내일 회수 기사님이 방문 예정이며 회수 배송비는 부담하지 않으셔도 됩니다."),
#      ]},
#     {"id": "Q20241201-004", "cs_no": "CS2412010004", **_KIM, "product": "-", "order_no": None,
#      "type": "주문", "status": "답변완료", "resolved_by": "AI",
#      "created_at": "2024.12.01 16:45", "answered_at": "2024.12.01 16:45", "ended_at": "2024.12.01 16:52",
#      "end_reason": "자동 종료",
#      "messages": [
#          _m("customer", "2024.12.01 16:45", "배송지를 회사 주소로 바꾸고 싶어요."),
#          _m("ai", "2024.12.01 16:45", "출고 전 주문은 [주문 내역 > 배송지 변경]에서 직접 바꾸실 수 있어요. "
#                                       "이미 출고된 경우에는 택배사 고객센터를 통해 변경해야 해요."),
#      ]},
#     # ---- 다른 고객 ----
#     {"id": "Q20241210-005", "cs_no": "CS2412100005", "customer": "박서연", "email": "seoyeon.park@email.com",
#      "phone": "010-2345-6789", "product": "에어프라이어 5.5L", "order_no": "20241209-5551234", "type": "결제",
#      "status": "검토대기", "resolved_by": None, "created_at": "2024.12.10 15:40", "answered_at": None,
#      "review_reasons": ["중복 결제 – 결제 내역 확인 필요"], "review_wait_min": 34,
#      "ended_at": "2024.12.10 15:46", "end_reason": "고객 종료",
#      "messages": [
#          _m("customer", "2024.12.10 15:40", "같은 주문이 카드로 두 번 결제됐어요. 확인 부탁드려요."),
#          _m("ai", "2024.12.10 15:40", _HANDOFF),
#      ]},
#     {"id": "Q20241210-006", "cs_no": "CS2412100006", "customer": "김하늘", "email": "haneul@email.com",
#      "phone": "010-3456-7890", "product": "세라믹 머그컵 2P 세트", "order_no": "20241207-3332211",
#      "type": "교환/환불", "status": "검토대기", "resolved_by": None, "created_at": "2024.12.10 13:05",
#      "review_reasons": ["상품 하자·배송 사고 – 사진/택배사 확인 필요"], "review_wait_min": 28,
#      "answered_at": None, "ended_at": "2024.12.10 13:12", "end_reason": "자동 종료",
#      "messages": [
#          _m("customer", "2024.12.10 13:05", "받은 머그컵 하나가 파손되어 왔어요."),
#          _m("ai", "2024.12.10 13:05", _HANDOFF),
#          _m("customer", "2024.12.10 13:07", "사진도 보낼 수 있나요?"),
#          _m("ai", "2024.12.10 13:07", "담당자가 확인 후 사진 접수 방법을 함께 안내해 드릴게요."),
#      ]},
#     {"id": "Q20241210-007", "cs_no": "CS2412100007", "customer": "이준호", "email": "junho.lee@email.com",
#      "phone": "010-4567-8901", "product": "러닝화 에어 270 (260)", "order_no": "20241130-9988776",
#      "type": "교환/환불", "status": "답변완료", "resolved_by": "관리자", "created_at": "2024.12.10 11:20",
#      "answered_at": "2024.12.10 12:05", "ended_at": "2024.12.10 11:24", "end_reason": "고객 종료",
#      "messages": [
#          _m("customer", "2024.12.10 11:20", "반품 접수한 지 일주일이 지났는데 환불이 안 들어왔어요."),
#          _m("ai", "2024.12.10 11:20", _HANDOFF),
#          _m("admin", "2024.12.10 12:05", "확인 결과 회수가 어제 완료되어 오늘 환불 처리되었습니다. 카드사에 따라 3~5일 내 반영돼요."),
#      ]},
#     {"id": "Q20241209-008", "cs_no": "CS2412090008", "customer": "최지훈", "email": "jihoon@email.com",
#      "phone": "010-5678-9012", "product": "기계식 키보드 텐키리스", "order_no": "20241209-4445556",
#      "type": "주문", "status": "답변완료", "resolved_by": "AI", "created_at": "2024.12.09 16:40",
#      "answered_at": "2024.12.09 16:40", "ended_at": "2024.12.09 16:47", "end_reason": "자동 종료",
#      "messages": [
#          _m("customer", "2024.12.09 16:40", "주문한 키보드 색상을 화이트로 바꿀 수 있나요?"),
#          _m("ai", "2024.12.09 16:40", "출고 전이라 옵션 변경이 가능해요. [주문 내역 > 옵션 변경]에서 화이트로 바꿔 주세요."),
#      ]},
#     {"id": "Q20241209-009", "cs_no": "CS2412090009", "customer": "정다은", "email": "daeun@email.com",
#      "phone": "010-6789-0123", "product": "-", "order_no": None, "type": "기타", "status": "검토대기",
#      "review_reasons": ["고객이 상담원 연결 요청"], "review_wait_min": 19,
#      "resolved_by": None, "created_at": "2024.12.09 13:20", "answered_at": None,
#      "ended_at": "2024.12.09 13:26", "end_reason": "고객 종료",
#      "messages": [
#          _m("customer", "2024.12.09 13:20", "신규 가입 쿠폰이 결제 페이지에서 안 보여요. 상담원 연결해 주세요."),
#          _m("ai", "2024.12.09 13:20", _HANDOFF),
#      ]},
# ]

# # ---------------- 대시보드 (시간대별은 샘플) ----------------
# HOURLY = [
#     {"hour": "09시", "inflow": 14, "done": 12},
#     {"hour": "10시", "inflow": 21, "done": 19},
#     {"hour": "11시", "inflow": 25, "done": 23},
#     {"hour": "12시", "inflow": 17, "done": 18},
#     {"hour": "13시", "inflow": 28, "done": 22, "peak": True},
#     {"hour": "14시", "inflow": 31, "done": 25, "peak": True},
#     {"hour": "15시", "inflow": 12, "done": 11},
#     {"hour": "16시", "inflow": 6, "done": 6},
#     {"hour": "17시", "inflow": 3, "done": 3},
# ]
# PEAK_ALERT = "오늘 13:00 ~ 15:00 구간 배송 문의 집중. 현재 인입 속도 안정화 단계 진입."



"""더미 데이터. 추후 DB/API 연동 시 이 파일만 교체하면 됩니다."""
from pathlib import Path

SERVICE_NAME = "daitda"
POLICY_DIR = Path(__file__).resolve().parent / "policies"

CURRENT_CUSTOMER = {
    "name": "김민지",
    "email": "kimminji@email.com",
    "phone": "010-1234-5678",
}
CURRENT_ADMIN = {"name": "관리자", "email": "admin@daitda.com", "phone": "-"}

# 데모 계정 (실서비스에서는 해시된 비밀번호 + DB 사용)
USERS = {
    "customer@daitda.com": {"password": "1234", "role": "customer", **CURRENT_CUSTOMER},
    "admin@daitda.com": {"password": "1234", "role": "admin", **CURRENT_ADMIN},
}

INQUIRY_TYPES = ["배송", "결제", "교환/환불", "주문", "기타"]
# 관리자 상태: 검토대기(AI가 답변하지 못해 관리자 확인 필요) / 답변완료
STATUSES = ["검토대기", "답변완료"]
# 고객 화면 상태: 상담 중(채팅 진행) / 상담 종료  (종료되면 관리자 화면에서도 답변완료로 이동)
CUSTOMER_STATUSES = ["상담 중", "상담 종료"]

# 고객의 최근 주문 (채팅에서 문의할 상품 선택용)
ORDERS = [
    {"order_no": "20241210-1234567", "product": "무선 블루투스 이어폰 Pro"},
    {"order_no": "20241208-7654321", "product": "데일리 코튼 니트 (베이지, M)"},
    {"order_no": "20241205-1122334", "product": "스테인리스 텀블러 500ml"},
]

# ---------------- 정책 문서 (PDF) ----------------
POLICIES = [
    {"id": "POL-001", "title": "배송 정책 · 배송 기간 안내", "desc": "출고 기준일, 배송 소요 기간, 지연 안내 기준",
     "file_name": "delivery_policy.pdf", "uploaded_at": "2024.12.02 10:20"},
    {"id": "POL-002", "title": "교환 · 환불 정책", "desc": "신청 기한, 배송비 부담 기준, 환불 소요 기간",
     "file_name": "refund_policy.pdf", "uploaded_at": "2024.12.05 09:41"},
    {"id": "POL-003", "title": "결제 · 취소 정책", "desc": "결제 수단별 취소 시점과 중복 결제 처리 기준",
     "file_name": "payment_policy.pdf", "uploaded_at": "2024.11.18 15:02"},
]


# ---------------- 문의 (채팅 단위) ----------------
def _m(role: str, at: str, content: str) -> dict:
    return {"role": role, "at": at, "content": content}


_KIM = {"customer": "김민지", "email": "kimminji@email.com", "phone": "010-1234-5678"}
_HANDOFF = "담당자가 확인 후 답변드릴게요. 기다리시는 동안 다른 궁금한 점도 편하게 물어보세요."

INQUIRIES = [
    # ---- 김민지 ----
    {"id": "Q20241210-001", "cs_no": "CS2412100001", **_KIM, "product": "무선 블루투스 이어폰 Pro",
     "order_no": "20241210-1234567", "type": "배송", "status": "답변완료", "resolved_by": "AI",
     "created_at": "2024.12.10 14:30", "answered_at": "2024.12.10 14:30", "ended_at": "2024.12.10 14:36",
     "end_reason": "고객 종료",
     "messages": [
         _m("customer", "2024.12.10 14:30", "주문한 이어폰 언제 배송되나요? 주문번호 20241210-1234567이에요."),
         _m("ai", "2024.12.10 14:30", "주문하신 상품은 현재 배송 준비 중이며 내일(12/11) 택배사로 인계될 예정이에요. "
                                      "인계 후 보통 1~2일 내에 받아보실 수 있어요."),
         _m("customer", "2024.12.10 14:35", "네 감사합니다!"),
         _m("ai", "2024.12.10 14:35", "도움이 되어 다행이에요. 더 궁금한 점이 있으면 언제든 물어봐 주세요."),
     ]},
    {"id": "Q20241208-002", "cs_no": "CS2412080002", **_KIM, "product": "데일리 코튼 니트 (베이지, M)",
     "order_no": "20241208-7654321", "type": "결제", "status": "검토대기", "resolved_by": None, "chat_state": "active",
     "review_reasons": ["출고 후 결제 취소 – 정책 예외 판단 필요"], "review_wait_min": 12,
     "created_at": "2024.12.08 10:15", "answered_at": None, "ended_at": None, "end_reason": None,
     "messages": [
         _m("customer", "2024.12.08 10:15", "이미 출고됐다고 나오는데 결제 취소가 가능한가요? 다른 상품으로 다시 주문하고 싶어요."),
         _m("ai", "2024.12.08 10:15", _HANDOFF),
     ]},
    {"id": "Q20241205-003", "cs_no": "CS2412050003", **_KIM, "product": "스테인리스 텀블러 500ml",
     "order_no": "20241205-1122334", "type": "교환/환불", "status": "답변완료", "resolved_by": "관리자",
     "created_at": "2024.12.05 09:20", "answered_at": "2024.12.05 13:02", "ended_at": "2024.12.05 09:27",
     "end_reason": "고객 종료",
     "messages": [
         _m("customer", "2024.12.05 09:20", "텀블러 뚜껑이 처음부터 금이 가 있어요. 교환 가능할까요?"),
         _m("ai", "2024.12.05 09:20", _HANDOFF),
         _m("admin", "2024.12.05 13:02", "불편을 드려 죄송합니다. 불량 상품으로 확인되어 무상 교환으로 접수해 드렸어요. "
                                         "내일 회수 기사님이 방문 예정이며 회수 배송비는 부담하지 않으셔도 됩니다."),
     ]},
    {"id": "Q20241201-004", "cs_no": "CS2412010004", **_KIM, "product": "-", "order_no": None,
     "type": "주문", "status": "답변완료", "resolved_by": "AI",
     "created_at": "2024.12.01 16:45", "answered_at": "2024.12.01 16:45", "ended_at": "2024.12.01 16:52",
     "end_reason": "자동 종료",
     "messages": [
         _m("customer", "2024.12.01 16:45", "배송지를 회사 주소로 바꾸고 싶어요."),
         _m("ai", "2024.12.01 16:45", "출고 전 주문은 [주문 내역 > 배송지 변경]에서 직접 바꾸실 수 있어요. "
                                      "이미 출고된 경우에는 택배사 고객센터를 통해 변경해야 해요."),
     ]},
    # ---- 다른 고객 ----
    {"id": "Q20241210-005", "cs_no": "CS2412100005", "customer": "박서연", "email": "seoyeon.park@email.com",
     "phone": "010-2345-6789", "product": "에어프라이어 5.5L", "order_no": "20241209-5551234", "type": "결제",
     "status": "검토대기", "resolved_by": None, "created_at": "2024.12.10 15:40", "answered_at": None,
     "review_reasons": ["중복 결제 – 결제 내역 확인 필요"], "review_wait_min": 34, "chat_state": "active",
     "ended_at": None, "end_reason": None,
     "messages": [
         _m("customer", "2024.12.10 15:40", "같은 주문이 카드로 두 번 결제됐어요. 확인 부탁드려요."),
         _m("ai", "2024.12.10 15:40", _HANDOFF),
     ]},
    {"id": "Q20241210-006", "cs_no": "CS2412100006", "customer": "김하늘", "email": "haneul@email.com",
     "phone": "010-3456-7890", "product": "세라믹 머그컵 2P 세트", "order_no": "20241207-3332211",
     "type": "교환/환불", "status": "검토대기", "resolved_by": None, "created_at": "2024.12.10 13:05",
     "review_reasons": ["상품 하자·배송 사고 – 사진/택배사 확인 필요"], "review_wait_min": 28, "chat_state": "active",
     "answered_at": None, "ended_at": None, "end_reason": None,
     "messages": [
         _m("customer", "2024.12.10 13:05", "받은 머그컵 하나가 파손되어 왔어요."),
         _m("ai", "2024.12.10 13:05", _HANDOFF),
         _m("customer", "2024.12.10 13:07", "사진도 보낼 수 있나요?"),
         _m("ai", "2024.12.10 13:07", "담당자가 확인 후 사진 접수 방법을 함께 안내해 드릴게요."),
     ]},
    {"id": "Q20241210-007", "cs_no": "CS2412100007", "customer": "이준호", "email": "junho.lee@email.com",
     "phone": "010-4567-8901", "product": "러닝화 에어 270 (260)", "order_no": "20241130-9988776",
     "type": "교환/환불", "status": "답변완료", "resolved_by": "관리자", "created_at": "2024.12.10 11:20",
     "answered_at": "2024.12.10 12:05", "ended_at": "2024.12.10 11:24", "end_reason": "고객 종료",
     "messages": [
         _m("customer", "2024.12.10 11:20", "반품 접수한 지 일주일이 지났는데 환불이 안 들어왔어요."),
         _m("ai", "2024.12.10 11:20", _HANDOFF),
         _m("admin", "2024.12.10 12:05", "확인 결과 회수가 어제 완료되어 오늘 환불 처리되었습니다. 카드사에 따라 3~5일 내 반영돼요."),
     ]},
    {"id": "Q20241209-008", "cs_no": "CS2412090008", "customer": "최지훈", "email": "jihoon@email.com",
     "phone": "010-5678-9012", "product": "기계식 키보드 텐키리스", "order_no": "20241209-4445556",
     "type": "주문", "status": "답변완료", "resolved_by": "AI", "created_at": "2024.12.09 16:40",
     "answered_at": "2024.12.09 16:40", "ended_at": "2024.12.09 16:47", "end_reason": "자동 종료",
     "messages": [
         _m("customer", "2024.12.09 16:40", "주문한 키보드 색상을 화이트로 바꿀 수 있나요?"),
         _m("ai", "2024.12.09 16:40", "출고 전이라 옵션 변경이 가능해요. [주문 내역 > 옵션 변경]에서 화이트로 바꿔 주세요."),
     ]},
    {"id": "Q20241209-009", "cs_no": "CS2412090009", "customer": "정다은", "email": "daeun@email.com",
     "phone": "010-6789-0123", "product": "-", "order_no": None, "type": "기타", "status": "검토대기",
     "review_reasons": ["고객이 상담원 연결 요청"], "review_wait_min": 19, "chat_state": "active",
     "resolved_by": None, "created_at": "2024.12.09 13:20", "answered_at": None,
     "ended_at": None, "end_reason": None,
     "messages": [
         _m("customer", "2024.12.09 13:20", "신규 가입 쿠폰이 결제 페이지에서 안 보여요. 상담원 연결해 주세요."),
         _m("ai", "2024.12.09 13:20", _HANDOFF),
     ]},
]

# ---------------- 대시보드 (시간대별은 샘플) ----------------
HOURLY = [
    {"hour": "09시", "inflow": 14, "done": 12},
    {"hour": "10시", "inflow": 21, "done": 19},
    {"hour": "11시", "inflow": 25, "done": 23},
    {"hour": "12시", "inflow": 17, "done": 18},
    {"hour": "13시", "inflow": 28, "done": 22, "peak": True},
    {"hour": "14시", "inflow": 31, "done": 25, "peak": True},
    {"hour": "15시", "inflow": 12, "done": 11},
    {"hour": "16시", "inflow": 6, "done": 6},
    {"hour": "17시", "inflow": 3, "done": 3},
]
PEAK_ALERT = "오늘 13:00 ~ 15:00 구간 배송 문의 집중. 현재 인입 속도 안정화 단계 진입."