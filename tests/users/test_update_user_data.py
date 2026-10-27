import allure
import pytest
import requests

from ursl import USER_CREATE_ENDPOINT, URL, USER_DATA_ENDPOINT
from helpers.helper import generate_user_payload

@allure.feature("API обновления данных")
class TestUpdateUserData:

    @allure.title(
        "Проверяем, что авторизизованный пользователь может успешно обновлять свои данные: "
        "успешная попытка изменения данных возвращает статус код 200 поле success = true "
    )
    def test_authorized_user_can_update_any_field(self, delete_user):
        payload = generate_user_payload()
        new_payload = generate_user_payload()

        with allure.step("Создание нового пользователя"):
            creating_response = requests.post(f"{URL}{USER_CREATE_ENDPOINT}", json=payload)

        token = creating_response.json()["accessToken"]
        delete_user(payload["email"], payload["password"])

        with allure.step(f"Модификация данных пользователя"):
            response = requests.patch(
                f"{URL}{USER_DATA_ENDPOINT}",
                headers={"Authorization": token},
                json=new_payload
            )

        with allure.step(
                "Проверяем, что на успешный запрос изменения данных "
                "авторизованного пользователя возвращается статус код 200"
        ):
            assert response.status_code == 200, (
                f"Ожидался статус код 200, но получен {response.status_code}"
            )

        body = response.json()

        with allure.step(
                "Проверяем, что в ответе на успешный запрос изменения данных "
                "авторизованного пользователя поле success в теле письма равно true"
        ):
            assert body.get("success") is True, (
                f"Поле success не равно true"
            )

        with allure.step("Проверяем, что данные пользователя обновились"):
            user_response = requests.get(
                f"{URL}{USER_DATA_ENDPOINT}",
                headers={"Authorization": token}
            )
            user_data = user_response.json()["user"]
            assert user_data["email"] == new_payload["email"], (
                f"Email не изменился: ожидалось '{new_payload['email']}', "
                f"получено '{user_data['email']}'"
            )
            assert user_data["name"] == new_payload["name"], (
                f"Имя не изменилось: ожидалось '{new_payload['name']}', "
                f"получено '{user_data['name']}'"
            )

    @allure.title("Проверяем, что неавторизованный пользователь не может изменить свои данные: "
                  "неуспешная попытка возвращает статус код 401 и поле success = false")
    @pytest.mark.parametrize(
        "field, new_value",
        [
            ("email", "new_email@test.com"),
            ("name", "Ivanov Ivan"),
            ("password", "NewStrongPass123!"),
        ],
        ids=["update_email", "update_name", "update_password"]
    )
    def test_changing_field_by_unauthorized_user_returns_error(self, delete_user, field, new_value):
        payload = generate_user_payload()

        with allure.step("Создаем нового пользователя"):
            requests.post(f"{URL}{USER_CREATE_ENDPOINT}", json=payload)

        delete_user(payload["email"], payload["password"])
        update_user_data = {field: new_value}

        with allure.step(f"Отправляем PATCH на изменение поля '{field}' без accessToken"):
            response = requests.patch(
                f"{URL}{USER_DATA_ENDPOINT}",
                json=update_user_data
            )

        with allure.step(
                "Проверяем, что при неуспешной попытке изменить данные неавторизованным пользователем "
                "возвращается статус код 401"
        ):
            assert response.status_code == 401, (
                f"Ожидался статус код 401, но пполучен {response.status_code}"
            )

        body = response.json()

        with allure.step(
                "Проверяем, что в ответе на неуспешный запрос изменения данных "
                "неавторизованного пользователя поле success в теле письма равно false"
        ):
            assert body.get("success") is False, (
                f"Поле success не равно false"
            )