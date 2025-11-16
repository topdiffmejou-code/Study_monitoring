from database import Database
import json
from datetime import datetime


class HeadmanInterface:
    def __init__(self, user_id, group_name):
        self.db = Database()
        self.user_id = user_id
        self.group_name = group_name

    def show_menu(self):
        while True:
            print("\n=== ПАНЕЛЬ СТАРОСТЫ ===")
            print("1. Просмотр успеваемости группы")
            print("2. Добавить оценку")
            print("3. Отметить посещаемость")
            print("4. Статистика группы")
            print("5. Сформировать отчет группы в JSON")
            print("6. Выход")

            choice = input("Выберите действие: ")

            if choice == '1':
                self.show_group_grades()
            elif choice == '2':
                self.add_grade()
            elif choice == '3':
                self.mark_attendance()
            elif choice == '4':
                self.show_group_statistics()
            elif choice == '5':
                self.generate_group_json_report()
            elif choice == '6':
                break
            else:
                print("Неверный выбор!")

    def show_group_grades(self):
        print(f"\n=== УСПЕВАЕМОСТЬ ГРУППЫ {self.group_name} ===")
        grades = self.db.get_group_grades(self.group_name)

        if not grades:
            print("Оценок пока нет.")
            return

        current_student = ""
        for student, subject, grade, date, teacher in grades:
            if student != current_student:
                current_student = student
                print(f"\n{student}:")
            print(f"  {subject}: {grade} ({date})")

    def add_grade(self):
        print("\n=== ДОБАВЛЕНИЕ ОЦЕНКИ ===")

        students = self.db.get_group_students(self.group_name)
        if not students:
            print("В группе нет студентов.")
            return

        print("\nСписок студентов:")
        for i, (student_id, full_name, username) in enumerate(students, 1):
            print(f"{i}. {full_name}")

        try:
            student_choice = int(input("\nВыберите студента: ")) - 1
            if student_choice < 0 or student_choice >= len(students):
                print("Неверный выбор студента!")
                return

            student_id = students[student_choice][0]

            subjects = [
                'Математика', 'Физика', 'Программирование',
                'Английский язык', 'История'
            ]

            print("\nДоступные предметы:")
            for i, subject in enumerate(subjects, 1):
                print(f"{i}. {subject}")

            subject_choice = int(input("Выберите предмет: ")) - 1
            if subject_choice < 0 or subject_choice >= len(subjects):
                print("Неверный выбор предмета!")
                return

            subject_name = subjects[subject_choice]

            grade = int(input("Оценка (2-5): "))
            if grade < 2 or grade > 5:
                print("Оценка должна быть от 2 до 5!")
                return

            teacher_name = input("ФИО преподавателя: ")

            if self.db.add_grade(student_id, subject_name, grade, teacher_name):
                print("Оценка успешно добавлена!")
            else:
                print("Ошибка при добавлении оценки!")

        except ValueError:
            print("Ошибка ввода!")

    def mark_attendance(self):
        print("\n=== ОТМЕТКА ПОСЕЩАЕМОСТИ ===")

        students = self.db.get_group_students(self.group_name)
        if not students:
            print("В группе нет студентов.")
            return

        subjects = [
            'Математика', 'Физика', 'Программирование',
            'Английский язык', 'История'
        ]

        print("\nДоступные предметы:")
        for i, subject in enumerate(subjects, 1):
            print(f"{i}. {subject}")

        try:
            subject_choice = int(input("Выберите предмет: ")) - 1
            if subject_choice < 0 or subject_choice >= len(subjects):
                print("Неверный выбор предмета!")
                return

            subject_name = subjects[subject_choice]

            print(f"\nОтметка посещаемости для {subject_name}:")
            for student_id, full_name, username in students:
                present = input(f"{full_name} присутствует? (y/n): ").lower() == 'y'
                self.db.add_attendance(student_id, subject_name, present)

            print("Посещаемость отмечена для всех студентов!")

        except ValueError:
            print("Ошибка ввода!")

    def show_group_statistics(self):
        print(f"\n=== СТАТИСТИКА ГРУППЫ {self.group_name} ===")

        grades = self.db.get_group_grades(self.group_name)
        students = self.db.get_group_students(self.group_name)

        if not grades:
            print("Нет данных для статистики.")
            return

        # Статистика по средним баллам
        student_grades = {}
        subject_grades = {}

        for student, subject, grade, date, teacher in grades:
            if student not in student_grades:
                student_grades[student] = []
            student_grades[student].append(grade)

            if subject not in subject_grades:
                subject_grades[subject] = []
            subject_grades[subject].append(grade)

        print("\nСредние баллы студентов:")
        for student, grades_list in student_grades.items():
            average = sum(grades_list) / len(grades_list)
            print(f"  {student}: {average:.2f}")

        print("\nСредние баллы по предметам:")
        for subject, grades_list in subject_grades.items():
            average = sum(grades_list) / len(grades_list)
            print(f"  {subject}: {average:.2f}")

        # Общая статистика
        all_grades = [grade for _, _, grade, _, _ in grades]
        overall_average = sum(all_grades) / len(all_grades)
        excellent_count = len([g for g in all_grades if g == 5])
        good_count = len([g for g in all_grades if g == 4])
        satisfactory_count = len([g for g in all_grades if g == 3])
        unsatisfactory_count = len([g for g in all_grades if g == 2])

        print(f"\nОбщая статистика группы:")
        print(f"  Средний балл: {overall_average:.2f}")
        print(f"  Отличных оценок: {excellent_count}")
        print(f"  Хороших оценок: {good_count}")
        print(f"  Удовлетворительных: {satisfactory_count}")
        print(f"  Неудовлетворительных: {unsatisfactory_count}")

    def generate_group_json_report(self):
        """Формирование отчета группы в JSON формате"""
        print("\n=== ФОРМИРОВАНИЕ ОТЧЕТА ГРУППЫ В JSON ===")

        group_data = self.db.get_group_detailed_info(self.group_name)

        if not group_data or not group_data['students']:
            print("Нет данных для формирования отчета группы.")
            return

        # Создаем имя файла
        filename = f"group_report_{self.group_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(group_data, f, ensure_ascii=False, indent=2)

            print(f"Отчет группы успешно сохранен в файл: {filename}")
            print(f"Содержимое отчета:")
            print(f"- Информация о группе: {group_data['group_name']}")
            print(f"- Количество студентов: {len(group_data['students'])}")
            print(f"- Средний балл группы: {group_data['group_statistics'].get('average_group_grade', 0):.2f}")
            print(f"- Средняя посещаемость: {group_data['group_statistics'].get('average_group_attendance', 0):.1f}%")
            print(f"- Детальная информация по каждому студенту")

        except Exception as e:
            print(f"Ошибка при сохранении отчета: {e}")