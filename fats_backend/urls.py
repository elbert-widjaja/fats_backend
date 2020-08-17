from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from api import views
from rest_framework_simplejwt import views as jwt_views

router = routers.DefaultRouter()
router.register('users', views.UserViewSet)
router.register('students', views.StudentViewSet)
router.register('courses', views.CourseViewSet)
router.register('labs', views.LabViewSet)
router.register('schedules', views.ScheduleViewSet)
router.register('attendances', views.AttendanceViewSet)
router.register('admins', views.AdminViewSet)
router.register('timetables', views.TimetableViewSet)
router.register('semesters', views.SemesterViewSet)

urlpatterns = [
    # Application
    path('home/', views.home, name='home'),
    # Internal
    path('api/', include(router.urls)),
    path('swagger/', include('swagger.urls')),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/token/', views.LoginView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('api/image/', views.ImageClassificationView.as_view(), name='image'),
]
