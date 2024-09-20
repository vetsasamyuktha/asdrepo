from pydantic import BaseModel
from typing import Optional
from datetime import date

class InstituteCreate(BaseModel):
    institute_name: str

class InstituteUpdate(BaseModel):
    institute_name: str

    class Config:
        from_attributes = True  # Updated to 'from_attributes'

class CourseCreate(BaseModel):
    institute_id: int
    course_name: str

class CourseUpdate(BaseModel):
    course_name: str
    institute_id: int

class StudentCreate(BaseModel):
    institute_id: int
    course_id: int
    student_name: str
    joining_date: date

class StudentUpdate(BaseModel):
    institute_id: int
    course_id: int
    student_name: str
    joining_date: date

class StudentOut(BaseModel):
    student_id: int
    institute_id: int
    course_id: int
    student_name: str
    joining_date: date

    class Config:
        from_attributes = True  # Correct usage
