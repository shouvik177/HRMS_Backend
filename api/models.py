"""
Employee and Attendance models. Employee has unique employee_id.
"""
from django.db import models


class Employee(models.Model):
    """Employee record. employee_id is unique (e.g. EMP001)."""
    employee_id = models.CharField(max_length=50, unique=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    department = models.CharField(max_length=100)

    class Meta:
        ordering = ['employee_id']

    def __str__(self):
        return f"{self.employee_id} - {self.full_name}"


class Attendance(models.Model):
    """Daily attendance: one record per employee per date with status Present/Absent."""
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    class Meta:
        ordering = ['-date', 'employee']
        constraints = [
            models.UniqueConstraint(fields=['employee', 'date'], name='unique_employee_date'),
        ]

    def __str__(self):
        return f"{self.employee.employee_id} - {self.date} - {self.status}"
