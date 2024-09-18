from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from models import Institute, Course, Student
from schemas import InstituteCreate, CourseCreate, StudentCreate, StudentOut
from database import get_db
import shutil
from fpdf import FPDF

app = FastAPI()
# CRUD for Institute
@app.post("/api/institutes/", response_model=InstituteCreate)
def create_institute(institute: InstituteCreate, db: Session = Depends(get_db)):
    try:
        db_institute = Institute(**institute.dict())
        db.add(db_institute)
        db.commit()
        db.refresh(db_institute)
        return db_institute
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sri/", response_model=list[InstituteCreate])
def read_institutes(db: Session = Depends(get_db)):
    return db.query(Institute).all()


# CRUD for Course
@app.post("/api/courses/", response_model=CourseCreate)
def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    try:
        db_course = Course(**course.dict())
        db.add(db_course)
        db.commit()
        db.refresh(db_course)
        return db_course
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# CRUD for Student
@app.post("/api/students/", response_model=StudentOut)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    db_student = Student(**student.dict())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


@app.get("/api/students/", response_model=list[StudentOut])
def read_students(db: Session = Depends(get_db)):
    return db.query(Student).all()


# Search API
@app.get("/api/search/")
def search(query: str, db: Session = Depends(get_db)):
    results = db.query(Institute.institute_name, Course.course_name, Student.student_name, Student.joining_date) \
        .join(Course, Student.course_id == Course.course_id) \
        .join(Institute, Student.institute_id == Institute.institute_id) \
        .filter(Institute.institute_name.ilike(f"%{query}%") |
                Course.course_name.ilike(f"%{query}%") |
                Student.student_name.ilike(f"%{query}%")).all()

    return [{"institute_name": r[0], "course_name": r[1], "student_name": r[2], "joining_date": r[3]} for r in results]


# Upload Student Photo
@app.post("/api/students/{student_id}/upload-photo/")
async def upload_photo(student_id: int, file: UploadFile = File(...)):
    file_location = f"photos/{student_id}_{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"info": f"File saved at {file_location}"}


# Generate Student ID Card
@app.get("/api/students/{student_id}/id-card/")
def generate_id_card(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    institute = db.query(Institute).filter(Institute.institute_id == student.institute_id).first()
    course = db.query(Course).filter(Course.course_id == student.course_id).first()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Student Name: {student.student_name}", ln=True)
    pdf.cell(200, 10, txt=f"Course Name: {course.course_name}", ln=True)
    pdf.cell(200, 10, txt=f"Institution Name: {institute.institute_name}", ln=True)
    pdf.cell(200, 10, txt=f"Joining Date: {student.joining_date}", ln=True)

    pdf_file = f"id_card_{student_id}.pdf"
    pdf.output(pdf_file)
    return FileResponse(pdf_file, media_type='application/pdf', filename=pdf_file)
