import pandas as pd

from graph import build_graph


def print_shortlist(result: dict) -> None:
    rows = []
    for idx, option in enumerate(result["shortlist"], start=1):
        rows.append(
            {
                "№": idx,
                "Билет": option["flight"]["name"],
                "Цена билета": option["flight"]["price"],
                "Отель": option["hotel"]["name"],
                "Цена отеля / ночь": option["hotel"]["price_per_night"],
                "Отель в лимите": "Да" if option["hotel_within_limit"] else "Нет",
                "Итого": option["total_cost"],
            }
        )

    df = pd.DataFrame(rows)
    print("\nДоступные варианты:\n")
    print(df.to_string(index=False))


def main():
    app = build_graph()

    state = {
        "user_request": "Хочу оформить командировку в Казань 15-17 апреля, нужен вариант подешевле",
        "destination": None,
        "dates": None,
        "preference": None,
        "policy_constraints": {},
        "flight_options": [],
        "hotel_options": [],
        "shortlist": [],
        "selected_option_index": None,
        "approval_required": False,
        "approval_attached": False,
        "booking_result": None,
        "status": "",
        "final_answer": None,
    }

    # Первая итерация: получить shortlist
    result = app.invoke(state)

    print("Статус после первой итерации:", result["status"])
    print_shortlist(result)

    selected = int(input("\nВыберите вариант (1-3): "))
    result["selected_option_index"] = selected

    # Вторая итерация: проверить, нужно ли согласование
    result = app.invoke(result)

    print("\nСтатус после выбора варианта:", result["status"])

    if result["status"] == "waiting_for_approval":
        user_input = input("Для выбранного варианта нужно согласование. Приложить согласование? (y/n): ").strip().lower()
        if user_input == "y":
            result["approval_attached"] = True
            result = app.invoke(result)
        else:
            print("\nПроцесс остановлен: ожидается согласование.")
            return

    print("\nФинальный результат:\n")
    print(result["final_answer"])


if __name__ == "__main__":
    main()