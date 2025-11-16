from auth import AuthSystem
from student_interface import StudentInterface
from headman_interface import HeadmanInterface


def main():
    auth_system = AuthSystem()

    while True:
        print("\n=== СИСТЕМА АКАДЕМИЧЕСКОГО МОНИТОРИНГА ===")
        print("1. Вход в систему")
        print("2. Выход")

        choice = input("Выберите действие: ")

        if choice == '1':
            if auth_system.login():
                user = auth_system.get_current_user()

                if user['role'] == 'student':
                    student_interface = StudentInterface(user['id'], user['group_name'])
                    student_interface.show_menu()
                elif user['role'] == 'headman':
                    headman_interface = HeadmanInterface(user['id'], user['group_name'])
                    headman_interface.show_menu()

                auth_system.logout()

        elif choice == '2':
            print("До свидания!")
            break
        else:
            print("Неверный выбор!")


if __name__ == "__main__":
    main()