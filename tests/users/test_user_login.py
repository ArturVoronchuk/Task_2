import allure
import requests

from ursl import URL, USER_LOGIN_ENDPOINT, USER_CREATE_ENDPOINT
from helpers.helper import generate_user_payload

@allure.feature("API авторизации")
class TestUserLogin:

    @allure.title(
        "Успешная авторизация зарегистрированного пользователя:"
        "Возвращатся статус код 200"
        "В ответе присутствует accessToken"
        "email и имя в ответе соответствует переданным в запрос"
    )

    def test_successful_authorization_of_the_registered_user(self, delete_user):
        payload = generate_user_payload()

        with allure.step("Создание нового пользователя"):
            requests.post(f"{URL}{USER_CREATE_ENDPOINT}", json=payload)

        delete_user(payload["email"], payload["password"])

        with allure.step("Авторизация зарегистрированного пользователя:"):
            response = requests.post(f"{URL}{USER_LOGIN_ENDPOINT}", json=payload)

        with allure.step("Проверяем, что статус код - 200"):
            assert response.status_code == 200, (
                f"Ожидался статус код 200, но получен {response.status_code}"
            )

        body = response.json()

        with allure.step("Проверяем, что поле success равно true"):
            assert body.get("success") is True, (
                "Success не равен true"
            )

        user_data = body.get("user")

        with allure.step(
                "Проверяем, что в теле ответа тот же email, что был передан в запросе на вторизацию"
        ):
            assert user_data["email"] == payload["email"], (
                f"ожидался email {payload['email']}, но получен {user_data['email']}"
            )

        with allure.step(
                "Проверяем, что в теле ответа то же имя пользователя, что было передано в запросе на вторизацию"
        ):
            assert user_data["name"] == payload["name"], (
                f"ожидалось имя пользователя - {payload['name']}, но получен {user_data['name']}"
            )

        with allure.step("Проверяем, наличие поля accessToken в ответе"):
            assert body.get("accessToken") is not None, (
                f"accessToken отсутствует в ответе"
            )

    @allure.title(
        "Авторизация с неверным пользователем или паролем завершается ошибкой: "
        "Запрос возвращает статус код 401 и сообщение об ошибке"
    )
    def test_login_with_invalid_credentials_returns_401(self, delete_user):

        wrong_payload = {
            "email": "wrong_user_email@gmail.ru",
            "password": "WrongUserPassword!",
        }

        with allure.step("Передача неверного логина и пароля в запросе авторизации"):
            response = requests.post(f"{URL}{USER_LOGIN_ENDPOINT}", json=wrong_payload)

        with allure.step("Проверяем,что возвращаемый статус код - 401"):
            assert response.status_code == 401, (
                f"Ожидался статус код 401, но получен {response.status_code}"
            )

        body = response.json()
        with allure.step("Проверяем, что success равен false"):
            assert body.get("success") is False, (
                f"Поле success не равен false"
            )
        with allure.step("Проверяем, что теле ответа есть сообщение об ошибке некорректных email или password"):
            assert body.get("message") == "email or password are incorrect", (
                f"Нет ожидаемого сообщения об ошибке"
            )