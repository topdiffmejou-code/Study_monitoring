from database import Database


class AuthSystem:
    def __init__(self):
        self.db = Database()
        self.current_user = None

    def login(self):
        print("\n=== Вход в систему ===")
        username = input("Логин: ")
        password = input("Пароль: ")

        user = self.db.authenticate_user(username, password)

        if user:
            self.current_user = user
            print(f"\nДобро пожаловать, {user['full_name']}!")
            print(f"Роль: {user['role']}")
            print(f"Группа: {user['group_name']}")
            return True
        else:
            print("Неверный логин или пароль!")
            return False

    def logout(self):
        self.current_user = None
        print("Выход из системы выполнен.")

    def get_current_user(self):
        return self.current_user