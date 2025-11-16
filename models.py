from datetime import datetime
from enum import Enum

class UserRole(Enum):
    STUDENT = "student"
    HEADMAN = "headman"

class Subject(Enum):
    MATH = "Математика"
    PHYSICS = "Физика"
    PROGRAMMING = "Программирование"
    ENGLISH = "Английский язык"
    HISTORY = "История"