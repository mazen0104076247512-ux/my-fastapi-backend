from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uuid, time
from app import models, schemas, database

# إنشاء جداول قاعدة البيانات إذا لم تكن موجودة
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# --- إعدادات CORS ---
# نفس الإعدادات الموجودة في ملف db_connect.php
origins = [
    "https://ahmed-hussein-bs.netlify.app",
    "https://your-frontend-app.com", # أضف رابط الواجهة الأمامية بعد النشر
    "http://localhost",
    "http://127.0.0.1",
    "http://127.0.0.1:5500", # For local development with VS Code Live Server
    "http://localhost:5500", # Also allow localhost:5500
    "null", # Allow requests from local file:// URLs
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# دالة للحصول على جلسة قاعدة البيانات
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- نقاط النهاية (Endpoints) ---

@app.post("/api/login", response_model=schemas.LoginResponse)
def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    يحل محل ملف login.php
    """
    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()
    
    if not user or not models.verify_password(user_credentials.password, user.password):
        raise HTTPException(
            status_code=401, # Unauthorized
            detail={"status": "error", "message": "خطأ في البريد الإلكتروني أو كلمة السر."},
        )
    
    # ملاحظة: هذا الكود يفترض أن كلمات المرور في قاعدة البيانات مشفرة بـ bcrypt
    # إذا كانت كلمات المرور كنص عادي، يجب تغيير الشرط أعلاه
    
    return {"status": "success", "user": user}

@app.post("/api/register", response_model=schemas.RegisterResponse)
def register(student_data: schemas.StudentRegister, db: Session = Depends(get_db)):
    """
    يحل محل ملف register.php
    """
    existing_user = db.query(models.User).filter(models.User.email == student_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail={"status": "error", "message": "هذا البريد الإلكتروني مسجل بالفعل."})

    new_user = models.User(
        id=str(uuid.uuid4()),
        name=student_data.name,
        email=student_data.email,
                password=models.hash_password(student_data.password),
        class_=student_data.class_,
        role='student'
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Convert to Pydantic model to ensure proper serialization.
    user_response = schemas.User.model_validate(new_user)
    return {"status": "success", "message": "تم إنشاء حسابك بنجاح! يمكنك الآن تسجيل الدخول.", "user": user_response}

@app.get("/api/load_data")
def load_data(db: Session = Depends(get_db)):
    """
    يحل محل ملف load_data.php (نسخة مبسطة)
    """
    try:
        # تحويل جداول الطلاب إلى قاموس منظم
        student_schedules_query = db.query(models.StudentSchedule).all()
        student_schedules_dict = {}
        for ss in student_schedules_query:
            if ss.studentId not in student_schedules_dict:
                student_schedules_dict[ss.studentId] = {}
            if ss.day not in student_schedules_dict[ss.studentId]:
                student_schedules_dict[ss.studentId][ss.day] = []
            student_schedules_dict[ss.studentId][ss.day].append(schemas.StudentScheduleEntry.from_orm(ss).dict())

        data = {
            'users': db.query(models.User).all(),
            'lessons': db.query(models.Lesson).all(),
            'modules': db.query(models.Module).all(),
            'exams': db.query(models.Exam).all(),
            'results': db.query(models.Result).all(),
            'schedules': {}, # سيتم التعامل معها لاحقاً
            'studentSchedules': student_schedules_dict, # جلب جداول الطلاب الخاصة
            'groups': [], # سيتم التعامل معها لاحقاً
            'notifications': [], # سيتم التعامل معها لاحقاً
            'favorites': {}, # سيتم التعامل معها لاحقاً
            'settings': {}, # سيتم التعامل معها لاحقاً
            'activityLog': {}, # سيتم التعامل معها لاحقاً
        }
        return data
    except Exception as e:
        # في حالة حدوث أي خطأ أثناء الاتصال أو الاستعلام، أرجع رسالة خطأ واضحة
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")

@app.post("/api/save_lesson")
def save_lesson(lesson_data: schemas.LessonSave, db: Session = Depends(get_db)):
    """
    يحل محل ملف save_lesson.php
    """
    try:
        if lesson_data.id:
            # --- تحديث درس موجود ---
            db_lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_data.id).first()
            if not db_lesson:
                raise HTTPException(status_code=404, detail="Lesson not found")

            db_lesson.title = lesson_data.title
            db_lesson.description = lesson_data.description
            db_lesson.class_ = lesson_data.class_
            db_lesson.moduleId = lesson_data.moduleId
            db_lesson.slides = lesson_data.slides
            message = "تم تحديث الدرس بنجاح"
        else:
            # --- إنشاء درس جديد ---
            new_lesson = models.Lesson(
                id=str(uuid.uuid4()),
                title=lesson_data.title,
                description=lesson_data.description,
                class_=lesson_data.class_,
                moduleId=lesson_data.moduleId,
                slides=lesson_data.slides,
                createdAt=int(time.time() * 1000) # Timestamp in milliseconds
            )
            db.add(new_lesson)
            message = "تم حفظ الدرس بنجاح"

        db.commit()
        return {"status": "success", "message": message}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Could not save lesson: {str(e)}")

@app.post("/api/delete_lesson")
def delete_lesson(item: schemas.DeleteItem, db: Session = Depends(get_db)):
    """
    يحل محل ملف delete_lesson.php
    """
    try:
        db_lesson = db.query(models.Lesson).filter(models.Lesson.id == item.id).first()
        if not db_lesson:
            raise HTTPException(status_code=404, detail="Lesson not found")
        db.delete(db_lesson)
        db.commit()
        return {"status": "success", "message": "تم حذف الدرس بنجاح"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Could not delete lesson: {str(e)}")

@app.post("/api/save_module")
def save_module(module_data: schemas.ModuleSave, db: Session = Depends(get_db)):
    try:
        if module_data.id:
            db_module = db.query(models.Module).filter(models.Module.id == module_data.id).first()
            if not db_module: raise HTTPException(status_code=404, detail="Module not found")
            db_module.name = module_data.name
            db_module.description = module_data.description
            db_module.class_ = module_data.class_
            message = "تم تحديث الوحدة بنجاح"
        else:
            new_module = models.Module(
                id=str(uuid.uuid4()),
                name=module_data.name,
                description=module_data.description,
                class_=module_data.class_
            )
            db.add(new_module)
            message = "تم حفظ الوحدة بنجاح"
        db.commit()
        return {"status": "success", "message": message}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Could not save module: {str(e)}")

@app.post("/api/delete_module")
def delete_module(item: schemas.DeleteItem, db: Session = Depends(get_db)):
    try:
        db.query(models.Lesson).filter(models.Lesson.moduleId == item.id).update({"moduleId": None})
        db_module = db.query(models.Module).filter(models.Module.id == item.id).first()
        if not db_module: raise HTTPException(status_code=404, detail="Module not found")
        db.delete(db_module)
        db.commit()
        return {"status": "success", "message": "تم حذف الوحدة بنجاح"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Could not delete module: {str(e)}")

@app.post("/api/save_exam")
def save_exam(exam_data: schemas.ExamSave, db: Session = Depends(get_db)):
    try:
        if exam_data.id:
            db_exam = db.query(models.Exam).filter(models.Exam.id == exam_data.id).first()
            if not db_exam: raise HTTPException(status_code=404, detail="Exam not found")
            
            db_exam.title = exam_data.title
            db_exam.class_ = exam_data.class_
            db_exam.duration = exam_data.duration
            db_exam.questions = [q.dict() for q in exam_data.questions]
            db_exam.confirmOnSubmit = exam_data.confirmOnSubmit
            
            message = "تم تحديث الامتحان بنجاح"
        else:
            new_exam = models.Exam(
                id=str(uuid.uuid4()),
                title=exam_data.title,
                class_=exam_data.class_,
                duration=exam_data.duration,
                questions=[q.dict() for q in exam_data.questions],
                confirmOnSubmit=exam_data.confirmOnSubmit
            )
            db.add(new_exam)
            message = "تم حفظ الامتحان بنجاح"
        db.commit()
        return {"status": "success", "message": message}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Could not save exam: {str(e)}")

@app.post("/api/delete_exam")
def delete_exam(item: schemas.DeleteItem, db: Session = Depends(get_db)):
    try:
        db.query(models.Result).filter(models.Result.examId == item.id).delete()
        db_exam = db.query(models.Exam).filter(models.Exam.id == item.id).first()
        if not db_exam: raise HTTPException(status_code=404, detail="Exam not found")
        db.delete(db_exam)
        db.commit()
        return {"status": "success", "message": "تم حذف الامتحان ونتائجه بنجاح"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Could not delete exam: {str(e)}")

@app.post("/api/save_student")
def save_student(student_data: schemas.StudentSave, db: Session = Depends(get_db)):
    try:
        if student_data.id:
            db_student = db.query(models.User).filter(models.User.id == student_data.id).first()
            if not db_student: raise HTTPException(status_code=404, detail="Student not found")
            db_student.name = student_data.name
            db_student.email = student_data.email
            db_student.class_ = student_data.class_
            if student_data.password: # كلمة المرور اختيارية عند التعديل
                db_student.password = models.hash_password(student_data.password)
            message = "تم تحديث بيانات الطالب"
        else:
            new_student = models.User(
                id=str(uuid.uuid4()),
                name=student_data.name,
                email=student_data.email,
                password=models.User.hash_password(student_data.password),
                class_=student_data.class_,
                role='student'
            )
            db.add(new_student)
            message = "تم إضافة الطالب بنجاح"
        db.commit()
        return {"status": "success", "message": message}
    except Exception as e:
        db.rollback()
        # Check for duplicate email
        if "Duplicate entry" in str(e):
            raise HTTPException(status_code=400, detail="هذا البريد الإلكتروني مسجل بالفعل.")
        raise HTTPException(status_code=500, detail=f"Could not save student: {str(e)}")

@app.post("/api/delete_student")
def delete_student(item: schemas.DeleteItem, db: Session = Depends(get_db)):
    try:
        db.query(models.Result).filter(models.Result.userId == item.id).delete()
        db_student = db.query(models.User).filter(models.User.id == item.id).first()
        if not db_student: raise HTTPException(status_code=404, detail="Student not found")
        db.delete(db_student)
        db.commit()
        return {"status": "success", "message": "تم حذف الطالب ونتائجه بنجاح"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Could not delete student: {str(e)}")

@app.post("/api/submit_exam")
def submit_exam(result_data: schemas.ExamSubmit, db: Session = Depends(get_db)):
    try:
        exam = db.query(models.Exam).filter(models.Exam.id == result_data.examId).first()
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found")

        score = 0
        for i, question in enumerate(exam.questions):
            if question['answer'] == result_data.studentAnswers[i]:
                score += 1
        
        total = len(exam.questions)

        new_result = models.Result(
            id=str(uuid.uuid4()),
            userId=result_data.userId,
            examId=result_data.examId,
            score=score,
            total=total,
            at=result_data.at,
            studentAnswers=result_data.studentAnswers
        )
        db.add(new_result)
        db.commit()

        return {"status": "success", "message": "تم تسليم الامتحان بنجاح.", "score": score, "total": total}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Could not submit exam: {str(e)}")

@app.get("/api/get_lesson_slides")
def get_lesson_slides(id: str, db: Session = Depends(get_db)):
    lesson = db.query(models.Lesson.slides).filter(models.Lesson.id == id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson.slides

@app.post("/api/save_student_schedule")
def save_student_schedule(entry_data: schemas.StudentScheduleSave, db: Session = Depends(get_db)):
    try:
        # Check if an entry for this student, day, and time already exists
        db_entry = db.query(models.StudentSchedule).filter(
            models.StudentSchedule.studentId == entry_data.studentId,
            models.StudentSchedule.day == entry_data.day,
            models.StudentSchedule.time == entry_data.time
        ).first()

        if db_entry:
            # Update existing entry
            db_entry.subject = entry_data.subject
            db_entry.teacher = entry_data.teacher
            message = "تم تحديث الحصة بنجاح"
        else:
            # Create new entry
            new_entry = models.StudentSchedule(**entry_data.dict())
            db.add(new_entry)
            message = "تم حفظ الحصة بنجاح"
        
        db.commit()
        return {"status": "success", "message": message}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Could not save schedule entry: {str(e)}")

@app.post("/api/delete_student_schedule")
def delete_student_schedule(item: schemas.StudentScheduleSave, db: Session = Depends(get_db)):
    try:
        db_entry = db.query(models.StudentSchedule).filter_by(studentId=item.studentId, day=item.day, time=item.time).first()
        if not db_entry: raise HTTPException(status_code=404, detail="Schedule entry not found")
        db.delete(db_entry)
        db.commit()
        return {"status": "success", "message": "تم حذف الحصة بنجاح"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Could not delete schedule entry: {str(e)}")

@app.post("/api/update_password")
def update_password(update_data: schemas.PasswordUpdate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == update_data.userId).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        user.password = models.User.hash_password(update_data.newPassword)
        db.commit()
        return {"status": "success", "message": "تم تحديث كلمة المرور بنجاح."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Could not update password: {str(e)}")
