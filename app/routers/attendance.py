from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import AttendanceCreate, AttendanceRead
from app.services.attendance_service import create_attendance, get_attendance, get_attendance_for_employee

router = APIRouter(prefix="/attendance", tags=["Attendance"])


def _to_read_model(attendance_item) -> AttendanceRead:
    return AttendanceRead(
        id=attendance_item.id,
        employee_id=attendance_item.employee_id,
        date=attendance_item.date,
        status=attendance_item.status,
        created_at=attendance_item.created_at,
        employee_name=attendance_item.employee.full_name,
        employee_code=attendance_item.employee.employee_id,
    )


@router.post("", response_model=AttendanceRead, status_code=status.HTTP_201_CREATED)
def create_attendance_endpoint(payload: AttendanceCreate, db: Session = Depends(get_db)) -> AttendanceRead:
    try:
        attendance = create_attendance(db=db, payload=payload)
        db.refresh(attendance, attribute_names=["employee"])
        return _to_read_model(attendance)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark attendance.",
        ) from exc


@router.get("", response_model=list[AttendanceRead], status_code=status.HTTP_200_OK)
def get_attendance_endpoint(
    date_filter: date | None = Query(default=None, alias="date"),
    employee_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[AttendanceRead]:
    try:
        rows = get_attendance(db=db, attendance_date=date_filter, employee_id=employee_id)
        return [_to_read_model(item) for item in rows]
    except Exception as exc:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch attendance records.",
        ) from exc


@router.get("/{employee_id}", response_model=list[AttendanceRead], status_code=status.HTTP_200_OK)
def get_employee_attendance_endpoint(employee_id: int, db: Session = Depends(get_db)) -> list[AttendanceRead]:
    try:
        rows = get_attendance_for_employee(db=db, employee_id=employee_id)
        return [_to_read_model(item) for item in rows]
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch employee attendance history.",
        ) from exc
