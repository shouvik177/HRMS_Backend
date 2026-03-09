from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models import AttendanceStatus


class EmployeeBase(BaseModel):
    employee_id: str = Field(min_length=2, max_length=40)
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    department: str = Field(min_length=2, max_length=100)


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeRead(EmployeeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class AttendanceBase(BaseModel):
    employee_id: int
    date: date
    status: AttendanceStatus


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceRead(AttendanceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    employee_name: str
    employee_code: str


class UserSignup(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: EmailStr
    created_at: datetime


class AuthResponse(BaseModel):
    message: str
    user: UserRead
