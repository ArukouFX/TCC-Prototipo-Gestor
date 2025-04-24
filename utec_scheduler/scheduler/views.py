from django.shortcuts import render
from django.http import JsonResponse

#from scheduler.genetic_algorithm import ScheduleGenerator

from rest_framework import viewsets
from .models import Room, Course, Subject, Teacher, Schedule
from .serializers import (RoomSerializer, CourseSerializer, 
                         SubjectSerializer, TeacherSerializer, 
                         ScheduleSerializer)

# froms to fix
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Schedule
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status
from .models import Schedule

from utec_scheduler.genetic_algorithm import ScheduleGenerator


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

    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        Genera horarios usando el algoritmo genético.
        Endpoint: POST /api/schedules/generate/
        """
        try:
            # Instancia el generador
            generator = ScheduleGenerator()
            
            # Genera el mejor horario
            result = generator.generate()
            
            if not isinstance(result, dict) or 'assignments' not in result:
                raise ValueError("Formato de resultado inválido")
            
            # Limpia los horarios existentes
            Schedule.objects.all().delete()
            
            # Guarda los nuevos horarios
            created_schedules = []
            for assignment in result['assignments']:
                schedule = Schedule.objects.create(
                    course_id=assignment['course_id'],
                    subject_id=assignment['subject_id'],
                    teacher_id=assignment['teacher_id'],
                    room_id=assignment['room_id'],
                    day=assignment['day'],
                    start_time=f"{assignment['start_time']}:00" if len(assignment['start_time']) == 5 else assignment['start_time'],
                    end_time=assignment['end_time'],
                    duration=assignment['duration']
                )
                created_schedules.append(schedule)
            
            return Response({
                'status': 'success',
                'message': f'Se generaron {len(created_schedules)} horarios',
                'schedules': self.get_serializer(created_schedules, many=True).data,
                'fitness': result.get('fitness')
            })
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def generate_schedules(request):
    try:
        # Instancia el generador
        generator = ScheduleGenerator()
        
        # Genera el mejor horario
        best_schedule = generator.generate()
        
        # Limpia los horarios existentes
        Schedule.objects.all().delete()
        
        # Guarda los nuevos horarios
        for assignment in best_schedule:
            Schedule.objects.create(
                course_id=assignment['course_id'],
                subject_id=assignment['subject_id'],
                teacher_id=assignment['teacher_id'],
                room_id=assignment['room_id'],
                day=assignment['day'],
                start_time=f"{assignment['start_time']}:00",
                end_time=f"{int(assignment['start_time'].split(':')[0]) + 2}:00"
            )
        
        return Response({
            'status': 'success',
            'message': 'Horarios generados correctamente'
        })
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=400)