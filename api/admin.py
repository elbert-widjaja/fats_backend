from django.contrib import admin
from .models import Student, Course, Lab, Schedule, Attendance, Admin, Timetable, Semester
# Register your models here.


admin.site.register(Student)
admin.site.register(Course)
admin.site.register(Lab)
admin.site.register(Schedule)
admin.site.register(Attendance)
admin.site.register(Admin)
admin.site.register(Timetable)
admin.site.register(Semester)
