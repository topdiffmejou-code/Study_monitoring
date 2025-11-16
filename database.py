import sqlite3
from datetime import datetime
import json


class Database:
    def __init__(self, db_name="academic_system.db"):
        self.db_name = db_name
        self.init_database()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL,
                group_name TEXT NOT NULL
            )
        ''')

        # Таблица предметов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')

        # Таблица оценок
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS grades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                subject_id INTEGER NOT NULL,
                grade INTEGER NOT NULL,
                date TEXT NOT NULL,
                teacher_name TEXT NOT NULL,
                FOREIGN KEY (student_id) REFERENCES users (id),
                FOREIGN KEY (subject_id) REFERENCES subjects (id)
            )
        ''')

        # Таблица посещаемости
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                subject_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                present BOOLEAN NOT NULL,
                FOREIGN KEY (student_id) REFERENCES users (id),
                FOREIGN KEY (subject_id) REFERENCES subjects (id)
            )
        ''')

        # Добавляем основные предметы
        subjects = [
            'Математика', 'Физика', 'Программирование',
            'Английский язык', 'История'
        ]

        for subject in subjects:
            cursor.execute(
                "INSERT OR IGNORE INTO subjects (name) VALUES (?)",
                (subject,)
            )

        # Добавляем тестовых пользователей
        test_users = [
            ('student1', '123456', 'Иванов Иван Иванович', 'student', 'Группа 101'),
            ('student2', '123456', 'Петров Петр Петрович', 'student', 'Группа 101'),
            ('headman1', '123456', 'Сидоров Алексей', 'headman', 'Группа 101')
        ]

        for user in test_users:
            cursor.execute(
                '''INSERT OR IGNORE INTO users 
                (username, password, full_name, role, group_name) 
                VALUES (?, ?, ?, ?, ?)''',
                user
            )

        conn.commit()
        conn.close()

    def authenticate_user(self, username, password):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password)
        )

        user = cursor.fetchone()
        conn.close()

        if user:
            return {
                'id': user[0],
                'username': user[1],
                'full_name': user[3],
                'role': user[4],
                'group_name': user[5]
            }
        return None

    def get_student_grades(self, student_id):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT s.name, g.grade, g.date, g.teacher_name 
            FROM grades g
            JOIN subjects s ON g.subject_id = s.id
            WHERE g.student_id = ?
            ORDER BY s.name, g.date
        ''', (student_id,))

        grades = cursor.fetchall()
        conn.close()
        return grades

    def get_student_attendance(self, student_id):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT s.name, a.date, a.present 
            FROM attendance a
            JOIN subjects s ON a.subject_id = s.id
            WHERE a.student_id = ?
            ORDER BY a.date DESC
        ''', (student_id,))

        attendance = cursor.fetchall()
        conn.close()
        return attendance

    def get_group_students(self, group_name):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, full_name, username 
            FROM users 
            WHERE group_name = ? AND role = 'student'
            ORDER BY full_name
        ''', (group_name,))

        students = cursor.fetchall()
        conn.close()
        return students

    def get_group_grades(self, group_name):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT u.full_name, s.name, g.grade, g.date, g.teacher_name
            FROM grades g
            JOIN users u ON g.student_id = u.id
            JOIN subjects s ON g.subject_id = s.id
            WHERE u.group_name = ?
            ORDER BY u.full_name, s.name
        ''', (group_name,))

        grades = cursor.fetchall()
        conn.close()
        return grades

    def add_grade(self, student_id, subject_name, grade, teacher_name):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Получаем ID предмета
        cursor.execute("SELECT id FROM subjects WHERE name = ?", (subject_name,))
        subject = cursor.fetchone()

        if subject:
            cursor.execute('''
                INSERT INTO grades (student_id, subject_id, grade, date, teacher_name)
                VALUES (?, ?, ?, ?, ?)
            ''', (student_id, subject[0], grade, datetime.now().strftime("%Y-%m-%d"), teacher_name))

            conn.commit()
            conn.close()
            return True

        conn.close()
        return False

    def add_attendance(self, student_id, subject_name, present):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Получаем ID предмета
        cursor.execute("SELECT id FROM subjects WHERE name = ?", (subject_name,))
        subject = cursor.fetchone()

        if subject:
            cursor.execute('''
                INSERT INTO attendance (student_id, subject_id, date, present)
                VALUES (?, ?, ?, ?)
            ''', (student_id, subject[0], datetime.now().strftime("%Y-%m-%d"), present))

            conn.commit()
            conn.close()
            return True

        conn.close()
        return False

    def get_student_detailed_info(self, student_id):
        """Получить детальную информацию о студенте для отчета"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Основная информация о студенте
        cursor.execute('''
            SELECT full_name, group_name FROM users WHERE id = ?
        ''', (student_id,))
        student_info = cursor.fetchone()

        if not student_info:
            return None

        # Оценки
        grades = self.get_student_grades(student_id)

        # Посещаемость
        attendance = self.get_student_attendance(student_id)

        # Расчет статистики
        subject_stats = {}
        for subject, grade, date, teacher in grades:
            if subject not in subject_stats:
                subject_stats[subject] = {'grades': [], 'teacher': teacher}
            subject_stats[subject]['grades'].append(grade)

        # Добавляем средние баллы
        for subject, stats in subject_stats.items():
            stats['average'] = sum(stats['grades']) / len(stats['grades'])

        # Статистика посещаемости
        attendance_stats = {}
        total_present = 0
        total_classes = 0

        for subject, date, present in attendance:
            if subject not in attendance_stats:
                attendance_stats[subject] = {'present': 0, 'total': 0}
            attendance_stats[subject]['total'] += 1
            if present:
                attendance_stats[subject]['present'] += 1
                total_present += 1
            total_classes += 1

        # Добавляем проценты посещаемости
        for subject, stats in attendance_stats.items():
            stats['attendance_rate'] = (stats['present'] / stats['total']) * 100 if stats['total'] > 0 else 0

        overall_attendance = (total_present / total_classes) * 100 if total_classes > 0 else 0

        conn.close()

        return {
            'student_info': {
                'full_name': student_info[0],
                'group': student_info[1],
                'student_id': student_id
            },
            'subjects': subject_stats,
            'attendance': attendance_stats,
            'overall_statistics': {
                'average_grade': sum(grade for subject in subject_stats.values() for grade in subject['grades']) / sum(
                    len(subject['grades']) for subject in subject_stats.values()) if subject_stats else 0,
                'overall_attendance': overall_attendance,
                'total_grades': sum(len(subject['grades']) for subject in subject_stats.values()),
                'total_classes': total_classes
            }
        }

    def get_group_detailed_info(self, group_name):
        """Получить детальную информацию о группе для отчета"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Получаем всех студентов группы
        students = self.get_group_students(group_name)

        group_data = {
            'group_name': group_name,
            'report_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'students': [],
            'group_statistics': {}
        }

        # Собираем данные по каждому студенту
        student_stats = []
        for student_id, full_name, username in students:
            student_info = self.get_student_detailed_info(student_id)
            if student_info:
                group_data['students'].append(student_info)
                student_stats.append(student_info['overall_statistics'])

        # Расчет общей статистики группы
        if student_stats:
            group_data['group_statistics'] = {
                'total_students': len(student_stats),
                'average_group_grade': sum(stat['average_grade'] for stat in student_stats) / len(student_stats),
                'average_group_attendance': sum(stat['overall_attendance'] for stat in student_stats) / len(
                    student_stats),
                'total_grades': sum(stat['total_grades'] for stat in student_stats),
                'total_classes': sum(stat['total_classes'] for stat in student_stats)
            }

        conn.close()
        return group_data