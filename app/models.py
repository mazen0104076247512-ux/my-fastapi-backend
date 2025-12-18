from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, JSON, BigInteger
from .database import Base, engine
from passlib.context import CryptContext

# لإدارة كلمات المرور
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password.encode('utf-8')[:72])

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password.encode('utf-8')[:72], hashed_password)

class User(Base):
    __tablename__ = "users"
    id = Column(String(255), primary_key=True, index=True)
    name = Column(String(255))
    email = Column(String(255), unique=True, index=True)
    password = Column(String(255))
    role = Column(String(50), default='student')
    class_ = Column('class', String(50)) # 'class' is a reserved keyword
    isActive = Column(Boolean, default=True)

class Lesson(Base):
    __tablename__ = "lessons"
    id = Column(String(255), primary_key=True, index=True)
    title = Column(String(255))
    description = Column(Text)
    class_ = Column('class', String(50))
    moduleId = Column(String(255), ForeignKey("modules.id"), nullable=True)
    order = Column(Integer, default=0)
    isVisible = Column(Boolean, default=True)
    slides = Column(JSON) # Storing slides as JSON
    # TODO: Add this column manually to your 'lessons' table in phpMyAdmin.
    # The SQL command is: ALTER TABLE lessons ADD COLUMN viewedBy JSON;
    # viewedBy = Column(JSON) # Storing viewedBy as JSON
    createdAt = Column(BigInteger)

class Module(Base):
    __tablename__ = "modules"
    id = Column(String(255), primary_key=True, index=True)
    name = Column(String(255))
    description = Column(Text, nullable=True)
    class_ = Column('class', String(50))
    order = Column(Integer, default=0)
    isVisible = Column(Boolean, default=True)

class Exam(Base):
    __tablename__ = "exams"
    id = Column(String(255), primary_key=True, index=True)
    title = Column(String(255))
    class_ = Column('class', String(50))
    duration = Column(Integer)
    questions = Column(JSON)
    confirmOnSubmit = Column(Boolean, default=True)

class Result(Base):
    __tablename__ = "results"
    id = Column(String(255), primary_key=True, index=True)
    userId = Column(String(255), ForeignKey("users.id"))
    examId = Column(String(255), ForeignKey("exams.id"))
    score = Column(Integer)
    total = Column(Integer)
    at = Column(BigInteger)
    studentAnswers = Column(JSON)

class StudentSchedule(Base):
    __tablename__ = "student_schedules"
    id = Column(Integer, primary_key=True, index=True)
    studentId = Column(String(255), ForeignKey("users.id"))
    day = Column(String(50))
    time = Column(String(50))
    subject = Column(String(255))
    teacher = Column(String(255), nullable=True)

# This line ensures that if the tables don't exist, they are created.
# If they exist but columns are missing, you might need to manually alter the table in the database.
Base.metadata.create_all(bind=engine)
