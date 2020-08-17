from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Student, Course, Attendance, Lab, Schedule, Admin, Timetable, Semester
from django.contrib.auth.hashers import make_password


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email']


class StudentSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password', 'placeholder': 'Password'})

    class Meta:
        model = Student
        fields = ('user_id', 'username', 'email', 'password', 'created_at', 'attendance_set', 'lab_set')

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.get('password'))
        return super(StudentSerializer, self).create(validated_data)


class LabSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lab
        fields = ('course', 'index', 'students', 'name', 'schedule_set')

    def update(self, instance, validated_data):
        students = validated_data.pop('students')
        for student in students:
            student_instance = Student.objects.get(user_id=student)
            if student_instance.is_registered_on(instance.index):
                raise serializers.ValidationError(f'Student {student} is already registered on this index')
            instance.students.add(student_instance)
        instance.index = validated_data.get('index', instance.index)
        instance.name = validated_data.get('name', instance.name)
        return instance

    def to_representation(self, instance):
        response = super().to_representation(instance)
        serialized = StudentSerializer(data=instance.students, many=True)
        serialized.is_valid()
        response['students'] = serialized.data
        return response


class CourseSerializer(serializers.ModelSerializer):
    labs = LabSerializer(many=True)

    class Meta:
        model = Course
        fields = ('id', 'name', 'desc', 'labs')


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ('id', 'lab', 'schedule', 'student', 'created_at', 'updated_at')

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['student'] = StudentSerializer(instance.student).data
        return response


class ScheduleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Schedule
        fields = ('id', 'lab', 'time', 'attendances')
        extra_kwargs = {'attendances': {'required': False}}

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['attendances'] = AttendanceSerializer(instance.attendances, many=True).data
        response['lab'] = LabSerializer(instance.lab).data
        return response


class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = ['id', 'timetable_set', 'year_start', 'number', 'first_week']


class TimeTableSerializer(serializers.ModelSerializer):
    semester = SemesterSerializer()
    lab = LabSerializer()

    class Meta:
        model = Timetable
        fields = '__all__'


class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = ('username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.get('password'))
        return super(AdminSerializer, self).create(validated_data)

