from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Employee
from app.schemas import EmployeeCreate


def create_employee(db: Session, payload: EmployeeCreate) -> Employee:
    employee = Employee(
        employee_id=payload.employee_id.strip(),
        full_name=payload.full_name.strip(),
        email=str(payload.email).lower().strip(),
        department=payload.department.strip(),
    )
    db.add(employee)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("Employee ID or email already exists.") from exc

    db.refresh(employee)
    return employee


def get_all_employees(db: Session) -> list[Employee]:
    query = select(Employee).order_by(Employee.created_at.desc())
    return list(db.scalars(query).all())


def delete_employee_by_id(db: Session, employee_db_id: int) -> bool:
    employee = db.get(Employee, employee_db_id)
    if not employee:
        return False

    db.delete(employee)
    db.commit()
    return True
