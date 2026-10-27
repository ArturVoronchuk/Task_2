import random
import string

class Helper:
    @staticmethod
    def random_string(length=10):
        return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))

def generate_user_payload():
    email = f"test_{Helper.random_string()}@gmail.ru"
    password = Helper.random_string()
    name = Helper.random_string()
    return {
        "email": email,
        "password": password,
        "name": name,
    }