from database import Database
import json
from datetime import datetime


class StudentInterface:
    def __init__(self, user_id, group_name):
        self.db = Database()
        self.user_id = user_id
        self.group_name = group_name

    def show_menu(self):
        while True:
            print("\n=== ПАНЕЛЬ СТУДЕНТА ===")
            print("1. Просмотр оценок")
            print("2. Просмотр посещаемости")
            print("3. Средний балл по предметам")
            print("4. Сформировать отчет в JSON")
            print("5. Выход")

            choice = input("Выберите действие: ")

            if choice == '1':
                self.show_grades()
            elif choice == '2':
                self.show_attendance()
            elif choice == '3':
                self.show_average_grades()
            elif choice == '4':
                self.generate_json_report()
            elif choice == '5':
                break
            else:
                print("Неверный выбор!")

    def show_grades(self):
        print("\n=== ВАШИ ОЦЕНКИ ===")
        grades = self.db.get_student_grades(self.user_id)

        if not grades:
            print("Оценок пока нет.")
            return

        current_subject = ""
        for subject, grade, date, teacher in grades:
            if subject != current_subject:
                current_subject = subject
                print(f"\n{subject}:")
            print(f"  {date}: {grade} (преп. {teacher})")

    def show_attendance(self):
        print("\n=== ВАША ПОСЕЩАЕМОСТЬ ===")
        attendance = self.db.get_student_attendance(self.user_id)

        if not attendance:
            print("Данные о посещаемости отсутствуют.")
            return

        present_count = 0
        total_count = 0

        print("\nПоследние занятия:")
        for subject, date, present in attendance[:10]:  # Показываем последние 10 записей
            status = "Присутствовал" if present else "Отсутствовал"
            print(f"  {date} - {subject}: {status}")

            total_count += 1
            if present:
                present_count += 1

        if total_count > 0:
            attendance_rate = (present_count / total_count) * 100
            print(f"\nОбщая посещаемость: {attendance_rate:.1f}%")

    def show_average_grades(self):
        print("\n=== СРЕДНИЙ БАЛЛ ПО ПРЕДМЕТАМ ===")
        grades = self.db.get_student_grades(self.user_id)

        if not grades:
            print("Оценок пока нет для расчета среднего балла.")
            return

        subject_grades = {}

        for subject, grade, date, teacher in grades:
            if subject not in subject_grades:
                subject_grades[subject] = []
            subject_grades[subject].append(grade)

        for subject, grades_list in subject_grades.items():
            average = sum(grades_list) / len(grades_list)
            print(f"{subject}: {average:.2f} ({len(grades_list)} оценок)")

    def generate_json_report(self):
        """Формирование отчета в JSON формате"""
        print("\n=== ФОРМИРОВАНИЕ ОТЧЕТА В JSON ===")

        student_data = self.db.get_student_detailed_info(self.user_id)

        if not student_data:
            print("Нет данных для формирования отчета.")
            return

        # Создаем имя файла
        filename = f"student_report_{self.user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(student_data, f, ensure_ascii=False, indent=2)

            print(f"Отчет успешно сохранен в файл: {filename}")
            print(f"Содержимое отчета:")
            print(f"- Личная информация")
            print(f"- Оценки по всем предметам")
            print(f"- Статистика посещаемости")
            print(f"- Средние баллы")
            print(f"- Общая статистика")

        except Exception as e:
            print(f"Ошибка при сохранении отчета: {e}")