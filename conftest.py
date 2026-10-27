import pytest
import requests
from ursl import URL, USER_LOGIN_ENDPOINT, USER_DATA_ENDPOINT

@pytest.fixture
def delete_user():
    credentials = []

    def _register_for_deletion(email, password):
        credentials.append({"email": email, "password": password})

    yield _register_for_deletion
    #Перед удалением пользователя дергает ручку /api/auth/login, для обновления accessToken,
    #т.е. в документации API непонятно ,
    # как обновлять токен запросом https://qa-stellarburgers.education-services.ru/api/auth/token
    for cred in credentials:
        login_resp = requests.post(
            f"{URL}{USER_LOGIN_ENDPOINT}",json={"email": cred["email"], "password": cred["password"]}
        )
        if login_resp.status_code == 200:
            token = login_resp.json()["accessToken"]
            requests.delete(f"{URL}{USER_DATA_ENDPOINT}", headers={"Authorization": token})