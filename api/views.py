from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import viewsets, status, views
from api import serializers, models
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import render
from PIL import Image
import logging
from .obj_classification_api import faceRec
from django.core.exceptions import ObjectDoesNotExist

predictor = faceRec.FacialRecognition()


class LoginView(views.APIView):
    def post(self, request):
        if not request.data:
            return Response({'detail': "Please provide username/password"}, status=status.HTTP_400_BAD_REQUEST)

        username = request.data['username']
        password = request.data['password']
        domain = request.data['domain']

        user = authenticate(username=username, password=password)
        if user is None:
            return Response({'detail': "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        is_student = hasattr(user, 'student')
        is_admin = hasattr(user, 'admin')

        if domain == 'student':
            if not is_student:
                return Response({'detail': f"No user found for this domain: {domain}"}, status=status.HTTP_401_UNAUTHORIZED)
        elif domain == 'admin':
            if not is_admin:
                return Response({'detail': f"No user found for this domain: {domain}"}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        response_data = {
            'access': str(refresh.access_token),
            'username': user.username,
        }
        if is_student:
            response_data['user_id'] = user.student.user_id
        return Response(response_data)


def home(request):
    return render(request, 'home/local.html')


class ImageClassificationView(views.APIView):
    def post(self, request):
        try:
            image_file = request.FILES['image']
            threshold = float(request.POST.get('threshold', 0.9))

            image_object = Image.open(image_file)
            name, probability, boxes = predictor.predict_face(image_object)

            if name is None or name == 'ignored':
                return Response(data={
                    'detections': [],
                    'student': {},
                })

            # return Response({'detections': [{
            #     'class_name': name,
            #     'score': float(probability) if probability is not None else '',
            #     'x': float(boxes['x']) if boxes is not None else '',
            #     'y': float(boxes['y']) if boxes is not None else '',
            #     'width': float(boxes['width']) if boxes is not None else '',
            #     'height': float(boxes['height']) if boxes is not None else '',
            #     }]},
            # )

            result = {
                'meta': {
                    'version': "0.0.1", 'numObjects': 'blah', 'threshold': threshold
                },
                'detections': [],
            }

            output = {
                'class_name': name,
                'score': float(probability) if probability is not None else '',
                'x': float(boxes['x']) if boxes is not None else '',
                'y': float(boxes['y']) if boxes is not None else '',
                'width': float(boxes['width']) if boxes is not None else '',
                'height': float(boxes['height']) if boxes is not None else '',
            }

            result['detections'].append(output)

            def label_to_username(label):
                username = label.lower().replace(' ', '')
                return username

            try:
                first_user = result['detections'][0]['class_name']
                if first_user:
                    username = label_to_username(first_user)
                    try:
                        student = models.Student.objects.get(username=username)
                        lab = request.POST.get('lab')
                        if student.is_registered_on(lab):
                            result['student'] = serializers.StudentSerializer(student).data
                        else:
                            result['student'] = {}
                            result['message'] = 'Student is not registered on the lab'
                    except ObjectDoesNotExist:
                        result['student'] = {}
                        pass
            except IndexError:
                pass

            return Response(data=result)
            
        except Exception as e:
            logging.exception(e)
            return Response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data={
                    'message': 'Error while recognizing the picture'
                }
            )


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = serializers.UserSerializer


class StudentViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing student instances
    """
    serializer_class = serializers.StudentSerializer
    queryset = models.Student.objects.all()


class CourseViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing course instances
    """
    serializer_class = serializers.CourseSerializer
    queryset = models.Course.objects.all()


class LabViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing lab instances
    """
    serializer_class = serializers.LabSerializer
    queryset = models.Lab.objects.all()

    def get_queryset(self):
        queryset = models.Lab.objects.all()
        user_id = self.request.query_params.get('user_id', None)
        if user_id is not None:
            queryset = queryset.filter(students__user_id=user_id)
        return queryset


class ScheduleViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing schedule instances
    """
    serializer_class = serializers.ScheduleSerializer
    queryset = models.Schedule.objects.all().order_by('-time')


class AttendanceViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing attendance instances
    """
    serializer_class = serializers.AttendanceSerializer
    queryset = models.Attendance.objects.all().order_by('-created_at')

    def get_queryset(self):
        queryset = self.queryset
        user_id = self.request.query_params.get('user_id', None)
        if user_id is not None:
            queryset = queryset.filter(student_id=user_id)
        return queryset


class TimetableViewSet(viewsets.ModelViewSet):
    """
    a viewset for viewing and editing timetable instances
    """
    serializer_class = serializers.TimeTableSerializer
    queryset = models.Timetable.objects.all()


class AdminViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing admin instances
    """
    serializer_class = serializers.AdminSerializer
    queryset = models.Admin.objects.all()


class SemesterViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A view set for viewing semester instances
    """
    serializer_class = serializers.SemesterSerializer
    queryset = models.Semester.objects.all()
