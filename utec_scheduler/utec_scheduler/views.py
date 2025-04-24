import traceback
from rest_framework.response import Response
from rest_framework.views import APIView

from scheduler.models import Schedule
from scheduler.serializers import ScheduleSerializer
from .genetic_algorithm import ScheduleGenerator


class ScheduleView(APIView):
    def generate(self, request, *args, **kwargs):
        try:
            # Instancia el generador
            generator = ScheduleGenerator()
            result = generator.generate()
            
            if not isinstance(result, dict) or 'assignments' not in result:
                raise ValueError("Formato de resultado inválido")
            
            # Asegurarse de que fitness es un número
            fitness = result.get('fitness')
            if fitness is not None:
                fitness = float(fitness)
            
            return Response({
                'status': 'success',
                'message': f'Se generaron {len(result["assignments"])} horarios',
                'schedules': result['assignments'],
                'fitness': fitness
            })
        except Exception as e:
            tb = traceback.format_exc()
            return Response({
                'status': 'error',
                'message': str(e),
                'traceback': tb
            }, status=500)