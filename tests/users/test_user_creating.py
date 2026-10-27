import allure
import pytest
import requests

from ursl import URL, USER_CREATE_ENDPOINT
from helpers.helper import generate_user_payload

@allure.feature("API создания пользователя")
class TestUserCreation:

    @allure.title(
        "Проверяем, что новый пользователь успешно создается: "
        "запрос возвращает код 200 и success: true в теле ответа"
    )
    def test_user_is_successfully_created(self, delete_user):
        payload = generate_user_payload()

        with allure.step("Создаем нового пользователя"):
            response = requests.post(f"{URL}{USER_CREATE_ENDPOINT}", json=payload)

        delete_user(payload["email"], payload["password"])

        with allure.step(
                "Поверяем, что при успешной попытке создать нового пользователя возвращается статус код - 200"
        ):
            assert response.status_code == 200, (
                f"Ожидался статус код 200, но получен {response.status_code}. Ответ: {response.text}"
            )

        body = response.json()

        with allure.step(
                "Поверяем, что при успешной попытке создать нового пользователя поле success теле ответа равно true"
        ):
            assert body.get("success") is True, (
                "В ответе success != true"
            )

        with allure.step(
                "Проверяем, что в теле запроса возвращается тот же email, что был передан в запросе"
        ):
            assert body["user"]["email"] == payload["email"], (
                "Email в ответе не совпадает с отправленным"
            )
        with allure.step(
                "Проверяем, что в теле запроса возвращается то же имя, что было передано в запросе"
        ):
            assert body["user"]["name"] == payload["name"], (
                "Имя в ответе не совпадает с отправленным"
            )
        with allure.step("Проверяем, наличие поля accessToken в ответе"):
            assert body.get("accessToken") is not None, (
                "В ответе отсутствует accessToken"
            )

    @allure.title(
        "Проверяем, что создать уже зарегистрированного пользователя невозможно: "
        "запрос возвращает код 403 и success = false в теле ответа"
        )
    def test_duplicate_user_registration_is_rejected(self, delete_user):
        payload = generate_user_payload()

        with allure.step("Создаём нового пользователя"):
            requests.post(f"{URL}{USER_CREATE_ENDPOINT}", json=payload)

        delete_user(payload["email"], payload["password"])

        with allure.step("Пытаемся создать второго пользователя с теми же кредами"):
            duplicate_response = requests.post(f"{URL}{USER_CREATE_ENDPOINT}", json=payload)

        with allure.step(
                "Проверяем, что при попытке повторно создать пользователя с теми же данными возвращается статус код 403"
        ):
            assert duplicate_response.status_code == 403, (
                f"Ожидался статус код 403, но получен {duplicate_response.status_code}"
            )

        body = duplicate_response.json()

        with allure.step(
                "Проверяем, что при попытке повторно создать пользователя с теми же данными поле success равно false"
        ):
            assert body.get("success") is False, (
                "В ответе success != false"
            )

        with allure.step(
                "Проверяем, что при попытке повторно создать пользователя с теми же данными возвращается "
                "сообщение об ошибке - 'User already exists'"
        ):
            assert body.get("message") == "User already exists", (
                "В ответе нет сообщения 'User already exists'"
            )

    @allure.title(
        "Проверяем, что невозможно создать пользователя без заполнения одного из обязательных полей: "
        "Запрос возвращает 403 статус и сообщение об ошибке "
    )
    @pytest.mark.parametrize(
        "missing_field",
        ["email", "password", "name"],
        ids=["без емейла", "без ппароля", "без имени"]
    )
    def test_missing_required_field_causes_error(self, missing_field, delete_user):
        payload = generate_user_payload()

        bad_payload = {k: v for k, v in payload.items() if k != missing_field}

        with allure.step(f"Создаем пользователя, не передав обязательное {missing_field}"):
            response = requests.post(f"{URL}{USER_CREATE_ENDPOINT}", json=bad_payload)

        # Страховка. Еесли вдруг пользовтель создастстя, то он гарантировано будет удален.
        # Когда я писал тест я опечатася в генераторе словаря -
        # поставил if v != missing_field и пользователь успешно создавался
        delete_user(payload["email"], payload["password"])

        with allure.step(
                "Проверяем, что без заполнения одного из обязательных полей запрос возвращает статус код 403"
        ):
            assert response.status_code == 403, (
                f"Ожидался 403 при отсутствии поля '{missing_field}', "
                f"но получен {response.status_code}. Ответ: {response.text}"
            )

        body = response.json()
        success = body.get("success")

        with allure.step("Проверяем. что поле success в теле ответа равно false"):
            assert success is False, (
                "В теле ответа значение 'success' не false"
            )

        message = body.get("message", "")

        with allure.step(
                "Проверяем, что при отправке запроса с незаполненным полем возвращается сообщение об ошибке "
                "'Email, password and name are required fields'"
        ):
            assert "Email, password and name are required fields" in message, (
                f"Ожидалось сообщение 'Недостаточно данных', получено: {message}"
            )
