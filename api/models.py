from django.db import models
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class Course(models.Model):
    """Course Database Model"""

    id = models.CharField(max_length=30, primary_key=True)
    name = models.CharField(max_length=128)
    desc = models.CharField(max_length=30, blank=True)


class Student(User):
    """Student Database Model"""

    user_id = models.CharField(max_length=30, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Student'
        verbose_name_plural = 'Students'

    def is_registered_on(self, lab_idx):
        return self.lab_set.filter(index=lab_idx).count() == 1

    def __str__(self):
        return self.user_id


class Admin(User):
    """admin model"""
    
    class Meta:
        verbose_name = 'Admin'
        verbose_name_plural = 'Admins'

    def __str__(self):
        return self.username


class Lab(models.Model):
    """Lab Database Model"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='labs')
    index = models.CharField(max_length=30, primary_key=True)
    name = models.CharField(max_length=30)
    students = models.ManyToManyField(Student)

    class Meta:
        unique_together = ['name', 'course']

    def __str__(self):
        return f"{self.course}-{self.index}"


class Schedule(models.Model):
    """Lab timing schedule"""
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE)
    time = models.DateTimeField(default=now)
    
    class Meta:
        unique_together = ['lab', 'time']


class Attendance(models.Model):
    """Attendance model"""

    lab = models.ForeignKey(Lab, on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='attendances')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['lab', 'schedule', 'student']

    def __str__(self):
        return f"{self.student.username}-{self.lab.index}-{self.lab.course_id}"


class Semester(models.Model):
    number = models.IntegerField()
    first_week = models.DateField()
    year_start = models.IntegerField()

    class Meta:
        unique_together = ['number', 'year_start']

    def __str__(self):
        return f"Semester {self.number} (AY {self.year_start}/{self.year_start + 1})"


class Timetable(models.Model):
    class Week(models.TextChoices):
        ODD = 'odd'
        EVEN = 'even'
        ALL = 'all'

    lab = models.ForeignKey(Lab, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    day = models.IntegerField()
    start_at = models.TimeField()
    end_at = models.TimeField()
    start_week = models.IntegerField()
    end_week = models.IntegerField()
    week = models.CharField(max_length=4, choices=Week.choices, default=Week.ALL)

    class Meta:
        unique_together = ['lab_id', 'semester_id']

    def __str__(self):
        return f"Timetable for {self.lab}"

    def clean_start_and_end_week(self):
        errors = {}
        is_error = False
        if self.week == self.Week.ODD:
            if self.start_week % 2 != 1:
                errors['start_week'] = 'This field must be odd when "week" is "odd"'
                is_error = True

            if self.end_week % 2 != 1:
                errors['end_week'] = 'This field must be odd when "week" is "odd"'
                is_error = True

        if self.week == self.Week.EVEN:
            if self.start_week % 2 != 0:
                errors['start_week'] = 'This field must be odd when "week" is "even"'
                is_error = True

            if self.end_week % 2 != 0:
                errors['end_week'] = 'This field must be odd when "week" is "even"'
                is_error = True
        if is_error:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.clean_start_and_end_week()
        super().save(*args, **kwargs)
