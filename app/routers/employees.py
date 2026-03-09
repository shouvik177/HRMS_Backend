from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import EmployeeCreate, EmployeeRead
from app.services.employee_service import create_employee, delete_employee_by_id, get_all_employees

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.post("", response_model=EmployeeRead, status_code=status.HTTP_201_CREATED)
def create_employee_endpoint(payload: EmployeeCreate, db: Session = Depends(get_db)) -> EmployeeRead:
    try:
        employee = create_employee(db=db, payload=payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create employee.",
        ) from exc
    return EmployeeRead.model_validate(employee)


@router.get("", response_model=list[EmployeeRead], status_code=status.HTTP_200_OK)
def get_employees_endpoint(db: Session = Depends(get_db)) -> list[EmployeeRead]:
    try:
        employees = get_all_employees(db=db)
        return [EmployeeRead.model_validate(item) for item in employees]
    except Exception as exc:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch employees.",
        ) from exc


@router.delete("/{employee_db_id}", status_code=status.HTTP_200_OK)
def delete_employee_endpoint(employee_db_id: int, db: Session = Depends(get_db)) -> dict:
    try:
        deleted = delete_employee_by_id(db=db, employee_db_id=employee_db_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found.")
        return {"message": "Employee deleted successfully."}
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete employee.",
        ) from exc
