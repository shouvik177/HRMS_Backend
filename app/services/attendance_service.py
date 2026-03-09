from datetime import date

from sqlalchemy import and_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Attendance, Employee
from app.schemas import AttendanceCreate


def create_attendance(db: Session, payload: AttendanceCreate) -> Attendance:
    employee = db.get(Employee, payload.employee_id)
    if not employee:
        raise LookupError("Employee not found.")

    attendance = Attendance(
        employee_id=payload.employee_id,
        date=payload.date,
        status=payload.status,
    )
    db.add(attendance)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("Attendance already marked for this employee on the selected date.") from exc

    db.refresh(attendance)
    return attendance


def get_attendance(
    db: Session,
    attendance_date: date | None = None,
    employee_id: int | None = None,
) -> list[Attendance]:
    filters = []
    if attendance_date:
        filters.append(Attendance.date == attendance_date)
    if employee_id:
        filters.append(Attendance.employee_id == employee_id)

    query = select(Attendance).order_by(Attendance.date.desc(), Attendance.created_at.desc())
    if filters:
        query = query.where(and_(*filters))

    return list(db.scalars(query).all())


def get_attendance_for_employee(db: Session, employee_id: int) -> list[Attendance]:
    employee = db.get(Employee, employee_id)
    if not employee:
        raise LookupError("Employee not found.")
    return get_attendance(db=db, employee_id=employee_id)
