from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.responses import FileResponse
from typing import List
from sqlalchemy.orm import Session
from models import Institute, Course, Student
from schemas import InstituteCreate, CourseCreate, StudentCreate, StudentOut, CourseUpdate, StudentUpdate, InstituteUpdate
from database import get_db
import shutil
import os
from fpdf import FPDF
from datetime import date

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


@app.put("/api/institutes/{institute_id}", response_model=InstituteUpdate)
def update_institute(institute_id: int, institute: InstituteUpdate, db: Session = Depends(get_db)):
    db_institute = db.query(Institute).filter(Institute.institute_id == institute_id).first()
    if not db_institute:
        raise HTTPException(status_code=404, detail="Institute not found")

    for key, value in institute.dict(exclude_unset=True).items():
        setattr(db_institute, key, value)

    db.commit()
    db.refresh(db_institute)
    return db_institute


@app.delete("/api/institutes/{institute_id}", response_model=dict)
def delete_institute(institute_id: int, db: Session = Depends(get_db)):
    db_institute = db.query(Institute).filter(Institute.institute_id == institute_id).first()
    if not db_institute:
        raise HTTPException(status_code=404, detail="Institute not found")

    db.delete(db_institute)
    db.commit()
    return {"detail": "Institute deleted successfully"}


@app.get("/api/institutes/", response_model=List[InstituteCreate])
def read_institutes(db: Session = Depends(get_db)):
    return db.query(Institute).all()

# CRUD for Course
@app.post("/api/courses/", response_model=CourseCreate)
def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    # Check if the institute exists
    db_institute = db.query(Institute).filter(Institute.institute_id == course.institute_id).first()
    if not db_institute:
        raise HTTPException(status_code=400, detail="Institute ID does not exist.")

    try:
        db_course = Course(**course.dict())
        db.add(db_course)
        db.commit()
        db.refresh(db_course)
        return db_course
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/api/courses/", response_model=List[CourseCreate])
def read_courses(db: Session = Depends(get_db)):
    return db.query(Course).all()


@app.put("/api/courses/{course_id}", response_model=CourseUpdate)
def update_course(course_id: int, course: CourseUpdate, db: Session = Depends(get_db)):
    db_course = db.query(Course).filter(Course.course_id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")

    for key, value in course.dict(exclude_unset=True).items():
        setattr(db_course, key, value)

    db.commit()
    db.refresh(db_course)
    return db_course


@app.delete("/api/courses/{course_id}", response_model=dict)
def delete_course(course_id: int, db: Session = Depends(get_db)):
    db_course = db.query(Course).filter(Course.course_id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")

    db.delete(db_course)
    db.commit()
    return {"detail": "Course deleted successfully"}

# CRUD for Student
@app.post("/api/students/", response_model=StudentOut)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    db_student = Student(**student.dict())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


@app.put("/api/students/{student_id}", response_model=StudentOut)
def update_student(student_id: int, student_update: StudentUpdate, db: Session = Depends(get_db)):
    db_student = db.query(Student).filter(Student.student_id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")

    for key, value in student_update.dict(exclude_unset=True).items():
        setattr(db_student, key, value)

    db.commit()
    db.refresh(db_student)
    return db_student


@app.delete("/api/students/{student_id}", response_model=dict)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    db_student = db.query(Student).filter(Student.student_id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")

    db.delete(db_student)
    db.commit()
    return {"detail": "Student deleted successfully"}


@app.get("/api/students/", response_model=List[StudentOut])
def read_students(db: Session = Depends(get_db)):
    return db.query(Student).all()

@app.get("/api/search/")
def search(query: str, db: Session = Depends(get_db)):
    # Ensure the query is not empty
    if not query:
        raise HTTPException(status_code=400, detail="Query parameter cannot be empty.")

    results = db.query(
        Institute.institute_name,
        Course.course_name,
        Student.student_name,
        Student.joining_date
    ) \
    .join(Course, Student.course_id == Course.course_id) \
    .join(Institute, Student.institute_id == Institute.institute_id) \
    .filter(
        Institute.institute_name.ilike(f"%{query}%") |
        Course.course_name.ilike(f"%{query}%") |
        Student.student_name.ilike(f"%{query}%")
    ).all()

    # Return structured results
    return [{
        "institute_name": r[0],
        "course_name": r[1],
        "student_name": r[2],
        "joining_date": r[3]
    } for r in results]


ALLOWED_EXTENSIONS = {".jpg", ".png", ".pdf"}
@app.post("/api/students/{student_id}/upload-photo/")
async def upload_photo(student_id: int, file: UploadFile = File(...)):
    # Validate the file extension
    file_extension = file.filename.split(".")[-1].lower()

    if not f".{file_extension}" in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid file format. Only .jpg, .png, and .pdf are allowed.")

    try:
        # Save the file
        file_location = f"photos/{student_id}_{file.filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {"info": f"File saved at {file_location}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")


# Generate Student ID Card
@app.get("/api/students/{student_id}/id-card/")
def generate_id_card(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    institute = db.query(Institute).filter(Institute.institute_id == student.institute_id).first()
    course = db.query(Course).filter(Course.course_id == student.course_id).first()

    os.makedirs('id_cards', exist_ok=True)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Student Name: {student.student_name}", ln=True)
    pdf.cell(200, 10, txt=f"Course Name: {course.course_name}", ln=True)
    pdf.cell(200, 10, txt=f"Institution Name: {institute.institute_name}", ln=True)
    pdf.cell(200, 10, txt=f"Joining Date: {student.joining_date}", ln=True)
    pdf_file = f"id_cards/id_card_{student_id}.pdf"
    pdf.output(pdf_file)
    return FileResponse(pdf_file, media_type='application/pdf', filename=f"id_card_{student_id}.pdf")
