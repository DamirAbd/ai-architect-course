from state import TravelState


POLICY_TEXT = """
Политика командировок:
1. Для поездок по России допускается только эконом-класс.
2. Лимит на отель: 7000 руб. за ночь.
3. Если общая стоимость поездки превышает 50000 руб., требуется согласование руководителя.
4. Предпочтительно выбирать варианты в рамках лимитов компании.
5. Для оформления нужны: город, даты поездки, цель поездки.
""".strip()


def fake_rag_retrieve(user_request: str) -> dict:
    """
    Упрощенный RAG.
    В реальной реализации:
    chunking -> embeddings -> vector search -> rerank -> context assembly
    """
    return {
        "trip_type": "Россия",
        "allowed_flight_class": "economy",
        "hotel_limit_per_night": 7000,
        "approval_if_total_gt": 50000,
        "required_fields": ["город", "даты", "цель поездки"],
        "policy_excerpt": POLICY_TEXT,
    }


def policy_rag_agent(state: TravelState) -> TravelState:
    state["policy_constraints"] = fake_rag_retrieve(state["user_request"])
    state["status"] = "policy_loaded"
    return state