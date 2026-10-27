import allure
import pytest
import requests

from ursl import URL, ORDER_ENDPOINT, USER_CREATE_ENDPOINT
from helpers.helper import generate_user_payload


@allure.feature("API получения списка заказов")
class TestGetUserData:

    @allure.title(
        "Проверяем, что авторизованный пользователь может получить список заказов конкретного пользователя: "
        "возвращается статус код 200, статус успешности запроса success = true, список заказов не пуст"
    )
    @pytest.mark.parametrize(
        "bun_name, bun_id, sauces_name, sauces_id, filling_name, filling_id",
        [
            (
                    "Флюоресцентная булка R2-D3", "6acef97852135b001b21a32c",
                    "Соус фирменный Space Sauce", "6acef97852135b001b21a332",
                    "Хрустящие минеральные кольца", "6acef97852135b001b21a335"
            ),
            (
                    "Краторная булка N-200i", "6acef97852135b001b21a32b",
                    "Соус с шипами Антарианского плоскоходца", "6acef97852135b001b21a334",
                    "Кристаллы марсианских альфа-сахаридов", "6acef97852135b001b21a337"
            ),
        ],
        ids=["mineral_fluorescent_space_burger", "cratered_alpha_saccharide_antarian_burger"]
    )
    def test_authorized_user_get_user_orders_request_return_status_code_200(
            self, delete_user,
            bun_name, bun_id, sauces_name, sauces_id, filling_name, filling_id
    ):
        payload = generate_user_payload()

        with allure.step("Создание нового пользователя"):
            creating_response = requests.post(
                f"{URL}{USER_CREATE_ENDPOINT}",
                json=payload
            )

        token = creating_response.json()["accessToken"]
        delete_user(payload["email"], payload["password"])

        ingredients = [bun_id, sauces_id, filling_id]

        with allure.step(
                "Отправляем POST на создание заказа c авторизацией (передаем accessToken в теле запроса)"
        ):
            requests.post(
                f"{URL}{ORDER_ENDPOINT}",
                headers={"Authorization": token},
                json={"ingredients": ingredients}
            )

        with allure.step(
                "Отправляем GET запрос на получение списка заказов конкретного пользователя"
        ):
            get_orders_response = requests.get(
                f"{URL}{ORDER_ENDPOINT}",
                headers={"Authorization": token}
            )

        with allure.step("Проверяем,что возвращается статус код 200"):
            assert get_orders_response.status_code == 200, (
                f"Ожидался статус код 200, но получен {get_orders_response.status_code}"
            )

        body = get_orders_response.json()

        with allure.step("Проверяем, что статус успешности запроса success = true"):
            assert body.get("success") is True, (
                "Статус success не равен true"
            )

        with allure.step("Проверяем, что orders — непустой список"):
            orders = body.get("orders", [])
            assert isinstance(orders, list), "orders не является списком"

        with allure.step("Проверяем, что каждый заказ содержит нужные поля"):
            for order in orders:
                assert "number" in order, f"В заказе нет number: {order}"
                assert "status" in order, f"В заказе нет status: {order}"
                assert "ingredients" in order, f"В заказе нет ingredients: {order}"
                assert order["number"] > 0, f"Некорректный number: {order['number']}"

    @allure.title(
        "Проверяем, что запрос на получение заказов конкретного пользователя, "
        "сделанный неавторизованным пользователем возврашает: "
        "статус код 401, статус успешности запроса success = false, сообщение об ошибке"
    )
    def test_unauthorized_user_get_user_orders_request_return_status_code_401(self):

        with allure.step(
                "Отправляем GET запрос на получение списка заказов конкретного пользователя без авторизации"
        ):
            get_orders_response = requests.get(
                f"{URL}{ORDER_ENDPOINT}"
            )

        with allure.step("Проверяем,что возвращается статус код 401"):
            assert get_orders_response.status_code == 401, (
                f"Ожидался статус код 401, но получен {get_orders_response.status_code}"
            )

        body = get_orders_response.json()

        with allure.step("Проверяем, что статус успешности запроса success = false"):
            assert body.get("success") is False, (
                "Статус success не равен false"
            )

        expected_message = "You should be authorised"
        message = body.get("message")

        with allure.step("Проверяем, что полученное сообщение соответствует ожидаемому"):
            assert message == expected_message, (
                f"Ожидлось получение сообщения {expected_message}, но получили {message}"
            )