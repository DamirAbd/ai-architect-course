from typing import TypedDict, Optional, List, Dict, Any


class TravelState(TypedDict):
    # вход
    user_request: str

    # извлеченные параметры
    destination: Optional[str]
    dates: Optional[str]
    preference: Optional[str]

    # данные политики
    policy_constraints: Dict[str, Any]

    # найденные варианты
    flight_options: List[Dict[str, Any]]
    hotel_options: List[Dict[str, Any]]
    shortlist: List[Dict[str, Any]]

    # выбор пользователя
    selected_option_index: Optional[int]

    # согласование
    approval_required: bool
    approval_attached: bool

    # результат бронирования
    booking_result: Optional[Dict[str, Any]]

    # служебное
    status: str
    final_answer: Optional[str]