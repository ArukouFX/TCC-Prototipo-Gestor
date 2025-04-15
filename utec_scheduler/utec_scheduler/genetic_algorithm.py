import random
from deap import base, creator, tools, algorithms
import numpy as np
from django.db.models import Q
from utec_scheduler.scheduler.models import Room, Course, Subject, Teacher, Schedule

# Definición de tipos para el algoritmo genético
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))  # Minimizamos la función de fitness
creator.create("Individual", list, fitness=creator.FitnessMin)

class ScheduleGenerator:
    def __init__(self):
        self.toolbox = base.Toolbox()
        self.setup_algorithm()
        
    def setup_algorithm(self):
        """Configura los componentes del algoritmo genético"""
        # Registramos las operaciones genéticas
        self.toolbox.register("individual", self.init_individual)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        self.toolbox.register("evaluate", self.evaluate_schedule)
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", self.mutate_schedule, indpb=0.1)
        self.toolbox.register("select", tools.selTournament, tournsize=3)
        
    def init_individual(self):
        """Inicializa un individuo con asignaciones aleatorias"""
        # Obtenemos todos los datos necesarios
        courses = Course.objects.all()
        subjects = Subject.objects.all()
        teachers = Teacher.objects.all()
        rooms = Room.objects.all()
        time_slots = self.get_time_slots()
        days = ['MON', 'TUE', 'WED', 'THU', 'FRI']
        
        individual = []
        for course in courses:
            for subject in subjects.filter(course=course):
                # Creamos una asignación aleatoria
                assignment = {
                    'course_id': course.id,
                    'subject_id': subject.id,
                    'teacher_id': random.choice(teachers.filter(subjects=subject).values_list('id', flat=True)),
                    'room_id': random.choice(self.filter_rooms(subject, rooms).values_list('id', flat=True)),
                    'day': random.choice(days),
                    'start_time': random.choice(time_slots),
                    'duration': subject.hours_per_week // 2  # Asumimos 2 sesiones por semana
                }
                individual.append(assignment)
        return individual

    def filter_rooms(self, subject, rooms):
        """Filtra salas según los requisitos de la materia"""
        if subject.requires_lab:
            return rooms.filter(room_type__in=['COMP', 'LOG'])
        return rooms.exclude(room_type__in=['COMP', 'LOG'])
    
    def get_time_slots(self):
        """Genera los slots horarios según los turnos"""
        return [
            '08:00', '10:00', '14:00', '16:00',  # Mañana/Tarde
            '19:00', '21:00'  # Noche
        ]
        
    def evaluate_schedule(self, individual):
        """Calcula el fitness del horario (menor es mejor)"""
        total_penalty = 0
        
        # 1. Penalizar solapamientos de horarios
        total_penalty += self.calculate_overlap_penalty(individual)
        
        # 2. Penalizar movimiento excesivo de profesores
        total_penalty += self.calculate_teacher_movement_penalty(individual)
        
        # 3. Priorizar laboratorios para materias que los requieren
        total_penalty += self.calculate_lab_usage_penalty(individual)
        
        # 4. Considerar preferencias de horarios para profesores de Montevideo
        total_penalty += self.calculate_teacher_preference_penalty(individual)
        
        # 5. Penalizar horarios fuera del turno del curso
        total_penalty += self.calculate_course_shift_penalty(individual)
        
        return (total_penalty,)

    def calculate_overlap_penalty(self, individual):
        """Calcula penalización por solapamientos"""
        penalty = 0
        schedule = {}
        
        for assignment in individual:
            key = (assignment['room_id'], assignment['day'], assignment['start_time'])
            if key in schedule:
                penalty += 100  # Penalización alta por solapamiento
            schedule[key] = assignment
            
        return penalty

    def calculate_teacher_movement_penalty(self, individual):
        """Calcula penalización por movimiento de profesores"""
        penalty = 0
        teacher_assignments = {}
        
        for assignment in individual:
            teacher_id = assignment['teacher_id']
            day = assignment['day']
            time = assignment['start_time']
            
            if teacher_id not in teacher_assignments:
                teacher_assignments[teacher_id] = {}
                
            if day not in teacher_assignments[teacher_id]:
                teacher_assignments[teacher_id][day] = []
                
            # Penalizar si el profesor tiene clases muy separadas
            if teacher_assignments[teacher_id][day]:
                last_time = teacher_assignments[teacher_id][day][-1]
                time_diff = abs(int(time.split(':')[0]) - int(last_time.split(':')[0]))
                if time_diff > 2:  # Más de 2 horas entre clases
                    penalty += 10 * time_diff
                    
            teacher_assignments[teacher_id][day].append(time)
            
        return penalty

    def calculate_lab_usage_penalty(self, individual):
        """Verifica uso correcto de laboratorios"""
        penalty = 0
        
        for assignment in individual:
            subject = Subject.objects.get(id=assignment['subject_id'])
            room = Room.objects.get(id=assignment['room_id'])
            
            if subject.requires_lab and room.room_type not in ['COMP', 'LOG']:
                penalty += 50  # Materia que necesita lab en sala normal
                
            if not subject.requires_lab and room.room_type in ['COMP', 'LOG']:
                penalty += 30  # Lab usado para materia que no lo necesita
                
        return penalty

    def calculate_teacher_preference_penalty(self, individual):
        """Considera preferencias de profesores de Montevideo"""
        penalty = 0
        
        for assignment in individual:
            teacher = Teacher.objects.get(id=assignment['teacher_id'])
            if teacher.from_montevideo:
                # Penalizar horarios muy temprano o muy tarde para profesores de Montevideo
                hour = int(assignment['start_time'].split(':')[0])
                if hour < 10 or hour > 18:  # Fuera de horario "cómodo"
                    penalty += 20
                    
        return penalty

    def calculate_course_shift_penalty(self, individual):
        """Verifica que los horarios coincidan con el turno del curso"""
        penalty = 0
        shift_hours = {
            'MORNING': (8, 12),
            'AFTERNOON': (14, 18),
            'NIGHT': (19, 22)
        }
        
        for assignment in individual:
            course = Course.objects.get(id=assignment['course_id'])
            hour = int(assignment['start_time'].split(':')[0])
            start, end = shift_hours[course.shift]
            
            if not (start <= hour < end):
                penalty += 40  # Horario fuera del turno del curso
                
        return penalty
        
    def mutate_schedule(self, individual, indpb):
        """Operador de mutación personalizado"""
        teachers = Teacher.objects.all()
        rooms = Room.objects.all()
        days = ['MON', 'TUE', 'WED', 'THU', 'FRI']
        time_slots = self.get_time_slots()
        
        for i in range(len(individual)):
            if random.random() < indpb:
                # Mutar profesor (solo si enseña la materia)
                subject = Subject.objects.get(id=individual[i]['subject_id'])
                valid_teachers = teachers.filter(subjects=subject).values_list('id', flat=True)
                valid_teachers = list(valid_teachers)
                if valid_teachers:
                    individual[i]['teacher_id'] = random.choice(valid_teachers)
                
                # Mutar sala (respetando requisitos de laboratorio)
                valid_rooms = self.filter_rooms(subject, rooms).values_list('id', flat=True)
                valid_rooms = list(valid_rooms)
                if valid_rooms:
                    individual[i]['room_id'] = random.choice(valid_rooms)
                
                # Mutar día y hora
                individual[i]['day'] = random.choice(days)
                individual[i]['start_time'] = random.choice(time_slots)
                
        return individual,
        
    def generate(self):
        """Genera el horario óptimo"""
        population = self.toolbox.population(n=100)
        algorithms.eaSimple(
            population, 
            self.toolbox, 
            cxpb=0.7,  # Probabilidad de cruce
            mutpb=0.3,  # Probabilidad de mutación
            ngen=50,    # Número de generaciones
            verbose=True
        )
        return tools.selBest(population, k=1)[0]