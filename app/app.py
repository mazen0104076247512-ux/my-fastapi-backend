import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Dict, Any, Optional
import os

# --- App Initialization ---
app = FastAPI()

# --- CORS Middleware ---
# للسماح للواجهة الأمامية (Frontend) بالتواصل مع هذا الخادم
origins = [
    "http://localhost",
    "http://127.0.0.1",
    "http://127.0.0.1:5500", # قد تحتاج هذا المنفذ إذا كنت تستخدم Live Server في VSCode
    # أضف هنا رابط الواجهة الأمامية عند رفعها على الإنترنت
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models (Data Validation) ---
# هذه النماذج تتأكد من أن البيانات القادمة من الواجهة الأمامية بالصيغة الصحيحة

class LoginData(BaseModel):
    email: str
    password: str

class StudentRegisterData(BaseModel):
    name: str
    email: EmailStr
    password: str
    class_: str

class LessonData(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    class_: str
    moduleId: str
    slides: List[str] # قائمة من الصور بصيغة Base64

class ExamData(BaseModel):
    id: Optional[str] = None
    title: str
    class_: str
    duration: int
    questions: List[Dict[str, Any]]
    confirmOnSubmit: bool

class StudentData(BaseModel):
    id: Optional[str] = None
    name: str
    email: EmailStr
    password: Optional[str] = None
    class_: str

class NoteData(BaseModel):
    userId: str
    lessonId: str
    slideIndex: int
    noteText: str

class ExamSubmission(BaseModel):
    userId: str
    examId: str
    at: int
    studentAnswers: List[Any]

class BroadcastData(BaseModel):
    message: str
    target: str # 'all', '1', '2', '3', or 'group-...'

# --- Database Configuration ---
# يقرأ رابط قاعدة البيانات من متغيرات البيئة (Environment Variables)
# هذا ضروري للأمان والمرونة عند النشر على الإنترنت
DATABASE_URL = os.getenv("DATABASE_URL")

# TODO: قم بإعداد اتصال قاعدة البيانات الحقيقي هنا باستخدام SQLAlchemy
# if DATABASE_URL:
#     # Production setup (e.g., PostgreSQL on Koyeb/Render)
#     from sqlalchemy import create_engine
#     from sqlalchemy.orm import sessionmaker
#     engine = create_engine(DATABASE_URL)
#     SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# else:
# Fallback to a dummy dictionary if DATABASE_URL is not set (for local development)
print("WARNING: DATABASE_URL environment variable not found. Using a temporary in-memory database.")
DUMMY_DB = {
    "users": [
        {"id": "admin1", "name": "Admin", "email": "admin@example.com", "password_hash": "hashed_password", "role": "admin", "class_": None},
        {"id": "student1", "name": "طالب مثال", "email": "student@example.com", "password_hash": "hashed_password", "role": "student", "class_": "3"}
    ], "lessons": [], "exams": [], "results": [], "schedules": {}, "studentSchedules": {},
    "notifications": [], "settings": {}, "activityLog": {}, "favorites": {}, "modules": [], "groups": []
}

# --- API Endpoints ---

@app.get("/api/load_data")
async def load_data():
    """
    يقوم هذا الـ endpoint بتحميل جميع البيانات الأولية التي يحتاجها التطبيق عند البدء.
    """
    # TODO: استبدل هذا بمنطق حقيقي لجلب البيانات من قاعدة البيانات الفعلية
    # if DATABASE_URL:
    #     db = SessionLocal()
    #     # ... fetch data from db ...
    return DUMMY_DB

@app.post("/api/login")
async def login(data: LoginData):
    """
    يتحقق من بيانات تسجيل الدخول ويعيد معلومات المستخدم إذا كانت صحيحة.
    """
    # TODO: تحقق من المستخدم وكلمة المرور في قاعدة البيانات
    # استخدم passlib.hash.bcrypt.verify() لمقارنة كلمة المرور
    user = next((u for u in DUMMY_DB["users"] if u["email"] == data.email), None)
    if user:
        # في التطبيق الحقيقي، قارن الـ hash وليس كلمة المرور مباشرة
        return {"status": "success", "user": user}
    return {"status": "error", "message": "بيانات الدخول غير صحيحة"}

@app.post("/api/register")
async def register(data: StudentRegisterData):
    """
    يسجل طالباً جديداً في النظام.
    """
    # TODO: أضف المستخدم الجديد إلى قاعدة البيانات
    # استخدم passlib.hash.bcrypt.hash() لتشفير كلمة المرور قبل حفظها
    print(f"Registering new student: {data.name}")
    return {"status": "success", "message": "تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول."}


@app.post("/api/save_lesson")
async def save_lesson(data: LessonData):
    """
    يحفظ درساً جديداً أو يقوم بتحديث درس موجود.
    """
    # TODO: منطق حفظ أو تحديث الدرس في قاعدة البيانات
    if data.id:
        print(f"Updating lesson: {data.title}")
        return {"status": "success", "message": "تم تحديث الدرس بنجاح."}
    else:
        print(f"Saving new lesson: {data.title}")
        return {"status": "success", "message": "تم حفظ الدرس بنجاح."}

@app.post("/api/delete_lesson")
async def delete_lesson(data: dict):
    """
    يحذف درساً من النظام.
    """
    lesson_id = data.get("id")
    # TODO: منطق حذف الدرس من قاعدة البيانات
    print(f"Deleting lesson with ID: {lesson_id}")
    return {"status": "success", "message": "تم حذف الدرس."}


@app.get("/api/get_lesson_slides")
async def get_lesson_slides(id: str):
    """
    يجلب شرائح الدرس عند الحاجة إليها لتقليل حجم التحميل الأولي.
    """
    # TODO: ابحث عن الدرس في قاعدة البيانات وأعد قائمة الشرائح الخاصة به
    # هذه بيانات وهمية للتجربة
    dummy_slides = [
        "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=", # 1x1 black pixel
        "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    ]
    return dummy_slides


@app.post("/api/submit_exam")
async def submit_exam(submission: ExamSubmission):
    """
    يستقبل إجابات الطالب، يقوم بتصحيحها، ويحفظ النتيجة.
    """
    # TODO:
    # 1. جلب الامتحان الصحيح من قاعدة البيانات.
    # 2. مقارنة إجابات الطالب بالإجابات الصحيحة لحساب الدرجة.
    # 3. حفظ النتيجة (score, total, studentAnswers, etc.) في جدول النتائج.
    score = 5 # درجة وهمية
    total = 10 # إجمالي وهمي
    print(f"Submitting exam {submission.examId} for user {submission.userId}")
    return {"status": "success", "score": score, "total": total}


# --- باقي الـ Endpoints ---
# يجب إضافة باقي نقاط الاتصال هنا بنفس الطريقة
# مثل: save_exam, delete_exam, save_student, toggle_favorite, etc.

@app.get("/")
async def root():
    """
    نقطة اتصال جذرية للتحقق من أن الخادم يعمل.
    """
    return {"message": "مرحباً بك في الواجهة الخلفية للمشروع. الخادم يعمل بنجاح!"}


# --- Uvicorn Runner ---
# هذا الجزء هو المسؤول عن تشغيل الخادم عند تنفيذ الملف مباشرة
# وهو ضروري للعمل على منصات مثل Koyeb أو Hugging Face
if __name__ == "__main__":
    # يستخدم المنفذ 7860 بشكل افتراضي في Hugging Face Spaces
    # منصات أخرى مثل Koyeb قد توفر المنفذ عبر متغيرات البيئة (Environment Variables)
    # الكود التالي يمكنه التعامل مع كلتا الحالتين
    import os
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)