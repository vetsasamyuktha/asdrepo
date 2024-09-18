from pydantic import BaseModel
from typing import Optional
from datetime import date

class InstituteCreate(BaseModel):
    institute_name: str

class CourseCreate(BaseModel):
    institute_id: int
    course_name: str

class StudentCreate(BaseModel):
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
        from_attributes = True  # Updated from orm_mode to from_attributes
