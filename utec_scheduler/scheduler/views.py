from django.shortcuts import render
from django.http import JsonResponse
#from scheduler.genetic_algorithm import ScheduleGenerator

from rest_framework import viewsets
from .models import Room, Course, Subject, Teacher, Schedule
from .serializers import (RoomSerializer, CourseSerializer, 
                         SubjectSerializer, TeacherSerializer, 
                         ScheduleSerializer)

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer

class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer

'''def generate_schedules(request):
    if request.method == 'POST':
        generator = ScheduleGenerator()
        best_schedule = generator.generate()
        
        # Limpiar horarios existentes
        Schedule.objects.all().delete()
        
        # Guardar el mejor horario encontrado
        for assignment in best_schedule:
            Schedule.objects.create(
                course_id=assignment['course_id'],
                subject_id=assignment['subject_id'],
                teacher_id=assignment['teacher_id'],
                room_id=assignment['room_id'],
                day=assignment['day'],
                start_time=assignment['start_time'],
                    end_time=calculate_end_time(assignment['start_time'], assignment['duration'])
                )
            
            return JsonResponse({'status': 'success', 'schedule': best_schedule})
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)
    
    def calculate_end_time(start_time, duration):
        """Calcula la hora de fin basada en la duración"""
        hour = int(start_time.split(':')[0])
        return f"{hour + duration}:00"
'''