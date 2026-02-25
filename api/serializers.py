from rest_framework import serializers
from .models import Employee, Attendance


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'employee_id', 'full_name', 'email', 'department']

    def validate_employee_id(self, value):
        value = (value or '').strip()
        if not value:
            raise serializers.ValidationError("Employee ID is required.")
        qs = Employee.objects.filter(employee_id=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Employee ID already exists.")
        return value

    def validate_email(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Email is required.")
        return value.strip()

    def validate_full_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Full name is required.")
        return value.strip()

    def validate_department(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Department is required.")
        return value.strip()


class AttendanceSerializer(serializers.ModelSerializer):
    employee_id = serializers.CharField(write_only=True)
    employee_id_display = serializers.CharField(source='employee.employee_id', read_only=True)

    class Meta:
        model = Attendance
        fields = ['id', 'employee', 'employee_id', 'employee_id_display', 'date', 'status']
        extra_kwargs = {'employee': {'read_only': True}}

    def validate_employee_id(self, value):
        if not value:
            raise serializers.ValidationError("employee_id is required.")
        try:
            Employee.objects.get(employee_id=value)
        except Employee.DoesNotExist:
            raise serializers.ValidationError("Employee not found.")
        return value

    def validate_status(self, value):
        if value not in ('Present', 'Absent'):
            raise serializers.ValidationError("Status must be 'Present' or 'Absent'.")
        return value

    def validate_date(self, value):
        if not value:
            raise serializers.ValidationError("Date is required.")
        return value

    def create(self, validated_data):
        emp_id = validated_data.pop('employee_id')
        employee = Employee.objects.get(employee_id=emp_id)
        obj, _ = Attendance.objects.update_or_create(
            employee=employee,
            date=validated_data['date'],
            defaults={'status': validated_data['status']}
        )
        return obj


class AttendanceListSerializer(serializers.ModelSerializer):
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)

    class Meta:
        model = Attendance
        fields = ['id', 'employee_id', 'date', 'status']
