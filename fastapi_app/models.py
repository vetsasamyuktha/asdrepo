from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "mysql://root:root@localhost/sd"  # Update with your credentials

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Institute(Base):
    __tablename__ = "institute"
    institute_id = Column(Integer, primary_key=True, index=True)
    institute_name = Column(String(100), unique=True, nullable=False)

class Course(Base):
    __tablename__ = "course"
    course_id = Column(Integer, primary_key=True, index=True)
    institute_id = Column(Integer, ForeignKey('institute.institute_id'), nullable=False)
    course_name = Column(String(100), nullable=False)

class Student(Base):
    __tablename__ = "student"
    student_id = Column(Integer, primary_key=True, index=True)
    institute_id = Column(Integer, ForeignKey('institute.institute_id'), nullable=False)
    course_id = Column(Integer, ForeignKey('course.course_id'), nullable=False)
    student_name = Column(String(100), nullable=False)
    joining_date = Column(Date, nullable=False)
Base.metadata.create_all(bind=engine)
