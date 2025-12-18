from pydantic import BaseModel
from typing import List, Optional

# Schema للرد بمعلومات المستخدم (بدون كلمة المرور)
class User(BaseModel):
    id: str
    name: str
    email: str
    role: str
    class_: Optional[str] = None
    isActive: bool

    class Config:
        from_attributes = True

# Schema لطلب تسجيل الدخول
class UserLogin(BaseModel):
    email: str
    password: str

# Schema للرد بعد تسجيل الدخول الناجح
class LoginResponse(BaseModel):
    status: str
    user: User

# Schema لبيانات الدرس عند الحفظ
class LessonSave(BaseModel):
    id: Optional[str] = None
    title: str
    description: Optional[str] = None
    class_: str
    moduleId: Optional[str] = None
    slides: List[str]

# Schema عام لعمليات الحذف
class DeleteItem(BaseModel):
    id: str

# Schema لحفظ وتعديل الوحدة
class ModuleSave(BaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    class_: str

# Schema لحفظ وتعديل الامتحان
class ExamQuestion(BaseModel):
    q: str
    choices: List[str]
    answer: int
    type: str
    topic: str

class ExamSave(BaseModel):
    id: Optional[str] = None
    title: str
    class_: str
    duration: int
    questions: List[ExamQuestion]
    confirmOnSubmit: bool

# Schema لحفظ وتعديل الطالب
class StudentSave(BaseModel):
    id: Optional[str] = None
    name: str
    email: str
    password: Optional[str] = None # كلمة المرور اختيارية عند التعديل
    class_: str

# Schema لطلب تسجيل طالب جديد
class StudentRegister(BaseModel):
    name: str
    email: str
    password: str
    class_: str

# Schema لبيانات تسليم الامتحان
class ExamSubmit(BaseModel):
    userId: str
    examId: str
    at: int
    studentAnswers: List[Optional[int]]

# Schema للرد بعد التسجيل الناجح
class RegisterResponse(BaseModel):
    status: str
    message: str
    user: User

# Schema لتحديث كلمة المرور
class PasswordUpdate(BaseModel):
    userId: str
    newPassword: str

# Schema لإدخال جدول الطالب
class StudentScheduleEntry(BaseModel):
    day: str
    time: str
    subject: str
    teacher: str

    class Config:
        from_attributes = True

# Schema for saving a student schedule entry
class StudentScheduleSave(BaseModel):
    studentId: str
    day: str
    time: str
    subject: str
    teacher: Optional[str] = None
