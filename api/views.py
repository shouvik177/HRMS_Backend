"""REST API: employees and attendance."""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Employee, Attendance
from .serializers import EmployeeSerializer, AttendanceSerializer, AttendanceListSerializer

# Swagger: request body schemas
_employee_post_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['employee_id', 'full_name', 'email', 'department'],
    properties={
        'employee_id': openapi.Schema(type=openapi.TYPE_STRING, description='Unique ID (e.g. EMP001)'),
        'full_name': openapi.Schema(type=openapi.TYPE_STRING),
        'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
        'department': openapi.Schema(type=openapi.TYPE_STRING),
    },
    example={'employee_id': 'EMP001', 'full_name': 'John Doe', 'email': 'john@example.com', 'department': 'Engineering'},
)
_attendance_post_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['employee_id', 'date', 'status'],
    properties={
        'employee_id': openapi.Schema(type=openapi.TYPE_STRING, description='Employee ID (e.g. EMP001)'),
        'date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE, description='YYYY-MM-DD'),
        'status': openapi.Schema(type=openapi.TYPE_STRING, enum=['Present', 'Absent']),
    },
    example={'employee_id': 'EMP001', 'date': '2025-02-19', 'status': 'Present'},
)


@swagger_auto_schema(
    method='post',
    operation_summary='Add employee',
    request_body=_employee_post_schema,
    responses={201: 'Created', 400: 'Bad Request'},
)
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def employee_list_create(request):
    if request.method == 'GET':
        serializer = EmployeeSerializer(Employee.objects.all(), many=True)
        return Response(serializer.data)
    serializer = EmployeeSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@swagger_auto_schema(
    method='put',
    operation_summary='Update employee',
    request_body=_employee_post_schema,
    responses={200: 'OK', 400: 'Bad Request', 404: 'Not Found'},
)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([AllowAny])
def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'GET':
        return Response(EmployeeSerializer(employee).data)
    if request.method in ('PUT', 'PATCH'):
        serializer = EmployeeSerializer(employee, data=request.data, partial=(request.method == 'PATCH'))
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)
    employee.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(
    method='post',
    operation_summary='Mark attendance',
    operation_description='Create an attendance record. Requires employee_id, date (YYYY-MM-DD), and status (Present or Absent).',
    request_body=_attendance_post_schema,
    responses={201: 'Created', 400: 'Bad Request'},
)
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def attendance_list_create(request):
    if request.method == 'GET':
        qs = Attendance.objects.all().select_related('employee')
        if request.query_params.get('date'):
            qs = qs.filter(date=request.query_params['date'])
        if request.query_params.get('employee_id'):
            qs = qs.filter(employee__employee_id=request.query_params['employee_id'])
        return Response(AttendanceListSerializer(qs, many=True).data)
    serializer = AttendanceSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    serializer.save()
    return Response(AttendanceListSerializer(serializer.instance).data, status=status.HTTP_201_CREATED)
