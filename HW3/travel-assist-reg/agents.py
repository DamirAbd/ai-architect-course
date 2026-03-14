from typing import Literal
from state import TravelState


def manager_extract_request(state: TravelState) -> TravelState:
    text = state["user_request"].lower()

    destination = "Не указано"
    if "казань" in text:
        destination = "Казань"
    elif "москва" in text:
        destination = "Москва"
    elif "санкт-петербург" in text or "петербург" in text or "спб" in text:
        destination = "Санкт-Петербург"

    dates = "15-17 апреля"
    if "15-17" in text or "15–17" in text:
        dates = "15-17 апреля"

    preference = "дешевле"
    if "удоб" in text:
        preference = "удобнее"
    elif "дешев" in text:
        preference = "дешевле"

    state["destination"] = destination
    state["dates"] = dates
    state["preference"] = preference
    state["status"] = "request_parsed"
    return state


def travel_search_agent(state: TravelState) -> TravelState:
    constraints = state["policy_constraints"]
    allowed_class = constraints["allowed_flight_class"]

    flights = [
        {"id": "F1", "name": "Рейс SU-101", "price": 12000, "time": "08:10", "class": "economy"},
        {"id": "F2", "name": "Рейс S7-214", "price": 14500, "time": "12:40", "class": "economy"},
        {"id": "F3", "name": "Рейс UT-330", "price": 22000, "time": "19:20", "class": "economy"},
    ]

    hotels = [
        {"id": "H1", "name": "Отель Волга", "price_per_night": 6500, "rating": 4.3, "distance_km": 1.2},
        {"id": "H2", "name": "Отель Центр", "price_per_night": 7200, "rating": 4.6, "distance_km": 0.5},
        {"id": "H3", "name": "Отель Бизнес", "price_per_night": 5900, "rating": 4.0, "distance_km": 2.1},
    ]

    state["flight_options"] = [f for f in flights if f["class"] == allowed_class]
    state["hotel_options"] = hotels
    state["status"] = "travel_options_found"
    return state


def manager_build_shortlist(state: TravelState) -> TravelState:
    hotel_limit = state["policy_constraints"]["hotel_limit_per_night"]

    flights = state["flight_options"]
    hotels = state["hotel_options"]

    nights = 2
    options = []

    for flight in flights:
        for hotel in hotels:
            total_cost = flight["price"] + hotel["price_per_night"] * nights
            hotel_within_limit = hotel["price_per_night"] <= hotel_limit

            score = (
                flight["price"] * 0.45
                + hotel["price_per_night"] * 0.35
                + hotel["distance_km"] * 1000 * 0.20
            )

            if not hotel_within_limit:
                score += 5000

            options.append(
                {
                    "flight": flight,
                    "hotel": hotel,
                    "total_cost": total_cost,
                    "hotel_within_limit": hotel_within_limit,
                    "score": score,
                }
            )

    options = sorted(options, key=lambda x: x["score"])[:3]
    state["shortlist"] = options
    state["status"] = "shortlist_ready"
    return state


def manager_wait_for_selection(state: TravelState) -> TravelState:
    state["status"] = "waiting_for_user_selection"
    return state


def route_after_selection(state: TravelState) -> Literal["wait", "selected"]:
    if state.get("selected_option_index") is None:
        return "wait"
    return "selected"


def manager_check_approval(state: TravelState) -> TravelState:
    idx = state["selected_option_index"]
    if idx is None:
        raise ValueError("Не выбран вариант")

    selected = state["shortlist"][idx - 1]
    approval_limit = state["policy_constraints"]["approval_if_total_gt"]

    state["approval_required"] = selected["total_cost"] > approval_limit
    state["status"] = "approval_checked"
    return state


def route_after_approval_check(
    state: TravelState,
) -> Literal["approval_needed", "booking"]:
    if state["approval_required"]:
        return "approval_needed"
    return "booking"


def manager_wait_for_approval(state: TravelState) -> TravelState:
    state["status"] = "waiting_for_approval"
    return state


def route_after_approval_wait(
    state: TravelState,
) -> Literal["wait", "booking"]:
    if state.get("approval_attached"):
        return "booking"
    return "wait"


def booking_agent(state: TravelState) -> TravelState:
    selected = state["shortlist"][state["selected_option_index"] - 1]

    state["booking_result"] = {
        "status": "booked",
        "message": "Бронирование успешно выполнено.",
        "booking_id": "TRIP-2026-001",
        "flight": selected["flight"]["name"],
        "hotel": selected["hotel"]["name"],
    }
    state["status"] = "booked"
    return state


def manager_build_final_answer(state: TravelState) -> TravelState:
    selected = state["shortlist"][state["selected_option_index"] - 1]
    booking_result = state["booking_result"]

    approval_required_text = "Да" if state["approval_required"] else "Нет"
    hotel_limit_text = "Да" if selected["hotel_within_limit"] else "Нет"

    final_answer = f"""
Итог по командировке

Направление: {state['destination']}
Даты: {state['dates']}
Предпочтение пользователя: {state['preference']}

Выбранный вариант:
- Билет: {selected['flight']['name']} ({selected['flight']['price']} руб.)
- Отель: {selected['hotel']['name']} ({selected['hotel']['price_per_night']} руб./ночь)
- Общая стоимость: {selected['total_cost']} руб.

Проверка ограничений:
- Допустимый класс перелета: {state['policy_constraints']['allowed_flight_class']}
- Отель в лимите: {hotel_limit_text}
- Требуется согласование: {approval_required_text}

Результат:
- Статус: {booking_result['status']}
- Сообщение: {booking_result['message']}
""".strip()

    booking_id = booking_result.get("booking_id")
    if booking_id:
        final_answer += f"\n- Идентификатор бронирования: {booking_id}"

    state["final_answer"] = final_answer
    state["status"] = "finished"
    return state