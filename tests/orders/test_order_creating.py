import allure
import pytest
import requests

from ursl import USER_CREATE_ENDPOINT, URL, ORDER_ENDPOINT
from helpers.helper import generate_user_payload

@allure.feature("API создания заказов")
class TestOrderCreate:

    @allure.title(
        "Проверяем, что авторизованный пользователь может создать заказ: "
        "запрос возвращает статус код 200, список ingredients, id ингредиента, "
        "запрос возвращает имя польователя, сделавшего заказ, статус заказа"
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
        ids = ["mineral_fluorescent_space_burger", "cratered_alpha_saccharide_antarian_burger"]
    )
    def test_authorized_user_successfully_create_an_order(
            self, delete_user,
            bun_name, bun_id, sauces_name, sauces_id, filling_name, filling_id
    ):
        payload = generate_user_payload()

        with allure.step("Создание нового пользователя"):
            creating_response = requests.post(f"{URL}{USER_CREATE_ENDPOINT}", json=payload)

        token = creating_response.json()["accessToken"]
        delete_user(payload["email"], payload["password"])

        ingredients = [bun_id, sauces_id, filling_id]

        with allure.step(
                "Отправляем POST на создание заказа c авторизацией (передаем accessToken в теле запроса)"
        ):
            order_response = requests.post(
                f"{URL}{ORDER_ENDPOINT}",
                headers={"Authorization": token},
                json={"ingredients": ingredients}
            )

        with allure.step("Проверяем, что возвращается статус код 200"):
            assert order_response.status_code == 200, (
                f"Ожидался статус код 200, но получен {order_response.status_code}"
            )

        body = order_response.json()

        with allure.step(
                "Проверяем, что в ответе авторизованному пользователю вернулся список из трех ингредиеентов: "
                "булка, соус, начинка"
        ):
            order_ingredients = body["order"]["ingredients"]
            assert len(order_ingredients) == 3, (
                f"В заказе ожидалось 3 игредиента, получили - {len(order_ingredients)} ингредиентов"
            )

        with allure.step("Проверяем, что ID ингредиентов совпадают с отправленными"):
            actual_ids = [ing["_id"] for ing in order_ingredients]
            assert actual_ids == ingredients, (
                f"ID ингредиентов не совпадают: ожидалось {ingredients}, получено {actual_ids}"
            )

        with allure.step("Проверяем, что в заказе указано имя пользователя"):
            owner_name = body["order"]["owner"]["name"]
            assert owner_name == payload["name"], (
                f"Имя пользователя не совпадает: ожидалось '{payload['name']}', получено '{owner_name}'"
            )

        with allure.step("Проверяем, что у заказа есть статус"):
            status = body["order"]["status"]
            assert status in ("done", "pending", "created"), (
                f"Неожиданный статус заказа: {status}"
            )

    @allure.title(
        "Проверяем, что неавторизованный пользователь не может создать заказ - "
        "в теле ответа отсутствуют: список ингредиентов, имя пользователя, статус заказа"
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
    def test_unauthorized_user_cant_create_an_order(
            self,
            bun_name, bun_id, sauces_name, sauces_id, filling_name, filling_id
    ):

        ingredients = [bun_id, sauces_id, filling_id]

        with allure.step(
                "Отправляем POST на создание заказа без авторизации (без передачи accessToken в теле запроса)"
        ):
            order_response = requests.post(
                f"{URL}{ORDER_ENDPOINT}",
                json={"ingredients": ingredients}
            )

        body = order_response.json()
        order = body.get("order", {})

        with allure.step("Проверяем, что запрос был обработан - вернулся статус код 200"):
            assert order_response.status_code == 200, (
                f"Ожидался статус код 200, но получен {order_response.status_code}"
            )

        with allure.step("Проверяем, что в ответе в поле 'order' нет списка ингредиентов"):
            assert "ingredients" not in order, (
                f"В ответе есть ingredients — заказ создан для неавторизованного: {order}"
            )

        with allure.step("Проверяем, что в ответе в поле 'order' нет имени пользователя "):
            assert "owner" not in order, (
                f"В ответе есть owner — заказ создан для неавторизованного: {order}"
            )

        with allure.step("Проверяем, что в ответе в поле 'order' нет статуса заказа"):
            assert "status" not in order, (
                f"В ответе есть status — заказ создан для неавторизованного: {order}"
            )

    @allure.title(
        "Проверяем, что при отсутствии ингредиентов в запросе возвращается "
        "статус код 400, статус успености запроса success = fals и текст ошибки"
    )
    def test_request_without_ingredients_returns_status_code_400(self):

        with allure.step(
                "Отправляем POST на создание заказа без ингредиентов"
        ):
            order_response = requests.post(
                f"{URL}{ORDER_ENDPOINT}"
            )

        with allure.step("Проверяем, что в ответе на запрос вернлся статус код 400"):
            assert order_response.status_code == 400, (
                f"В ответе ожидался статус код 400, но был получен статус код: {order_response.status_code}"
            )

        body = order_response.json()

        with allure.step("Проверяем, что статус запроса success = false"):
            assert body.get("success") is False, (
                "Статус success не равен false"
            )

        expected_message = "Ingredient ids must be provided"
        message = body.get("message")

        with allure.step(
                f"Проверяем, что сообщение в ответе соответствует {expected_message}"
        ):
            assert message == expected_message, (
                f"Ожидался текст сообщения {expected_message}. "
                f"Вместо этого получили сообщение {message}"
            )

    @allure.title(
        "Проверяем, что при передаче некорректного хэша ингредиента запрос возвращает:"
        "статус код 400, статус успешности запроса success = false "
        "и собщение об ошибке 'One or more ids provided are incorrect'"
    )
    def test_invalid_ingredients_hash_returns_status_code_400(self):

        invalid_ingredient_hash = "6acef97852135b001b21a31b"

        with allure.step(
                "Отправляем POST на создание заказа без ингредиентов"
        ):
            order_response = requests.post(
                f"{URL}{ORDER_ENDPOINT}",
                json={"ingredients": invalid_ingredient_hash}
            )

        with allure.step("Проверяем, что в ответе на запрос вернлся статус код 400"):
            assert order_response.status_code == 400, (
                f"В ответе ожидался статус код 400, но был получен статус код: {order_response.status_code}"
            )

        body = order_response.json()

        with allure.step("Проверяем, что статус успешности запроса success = false"):
            assert body.get("success") is False, (
                "Статус успешности запроса не false"
            )

        expected_message = "One or more ids provided are incorrect"
        message = body.get("message")

        with allure.step(f"Проверяем, что сообщение об ошибке соответстует {expected_message}"):
            assert message == expected_message, (
                f"Ожидалось получить в сообщении {expected_message}, но получили {message}"
            )