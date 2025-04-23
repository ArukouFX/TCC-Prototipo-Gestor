import random
from deap import base, creator, tools, algorithms
import numpy as np
from scheduler.models import Room, Course, Subject, Teacher, Schedule

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
        try:
            courses = list(Course.objects.all())
            subjects = list(Subject.objects.all())
            teachers = list(Teacher.objects.all())
            rooms = list(Room.objects.all())
            
            if not courses or not subjects or not teachers or not rooms:
                raise ValueError("Faltan datos necesarios para generar horarios")

            assignments = []
            TIME_SLOTS = ['08:00', '10:00', '14:00', '16:00', '19:00', '21:00']
            DAYS = ['MON', 'TUE', 'WED', 'THU', 'FRI']

            for course in courses:
                course_subjects = list(Subject.objects.filter(course=course))
                if not course_subjects:
                    continue

                for subject in course_subjects:
                    valid_teachers = list(Teacher.objects.filter(subjects=subject))
                    if not valid_teachers:
                        continue

                    assigned_teacher = random.choice(valid_teachers)
                    assigned_room = random.choice(rooms)
                    available_days = DAYS.copy()
                    selected_slots = []

                    hours = subject.hours_per_week
                    slots = []

                    # Si es impar, un bloque de 3h y el resto de 2h
                    if hours % 2 != 0:
                        slots.append(3)
                        hours -= 3
                    while hours > 0:
                        slots.append(2)
                        hours -= 2

                    for slot_hours in slots:
                        if not available_days:
                            available_days = DAYS.copy()
                        day = random.choice(available_days)
                        available_days.remove(day)

                        # Selección de hora de inicio según el bloque y turno
                        if course.shift == 'NIGHT':
                            if slot_hours == 3:
                                time = '19:00'  # 19:00-22:00 (ideal para bloque de 3h)
                            else:
                                time = random.choice(['19:00', '21:00'])
                        elif course.shift == 'MORNING':
                            if slot_hours == 3:
                                time = '08:00'
                            else:
                                time = random.choice(['08:00', '10:00'])
                        elif course.shift == 'AFTERNOON':
                            if slot_hours == 3:
                                time = '14:00'
                            else:
                                time = random.choice(['14:00', '16:00'])

                        assignment = {
                            'course_id': course.id,
                            'subject_id': subject.id,
                            'teacher_id': assigned_teacher.id,
                            'room_id': assigned_room.id,
                            'day': day,
                            'start_time': time,
                            'slot_hours': slot_hours  # Puedes usar este campo para control interno
                        }
                        assignments.append(assignment)

            individual = creator.Individual(assignments)
            return individual

        except Exception as e:
            print(f"Error en init_individual: {str(e)}")
            raise

    def filter_rooms(self, subject, rooms):
        """Filtra salas según los requisitos de la materia"""
        if subject.requires_lab:
            return rooms.filter(room_type__in=['COMP', 'LOG'])
        return rooms.filter(room_type__in=['COMP', 'LOG'])
    
    def get_time_slots(self):
        """Genera los slots horarios según los turnos"""
        return [
            '08:00', '10:00', '14:00', '16:00',  # Mañana/Tarde
            '19:00', '21:00'  # Noche
        ]
        
    def calculate_hours_penalty(self, individual, subjects_dict):
        """Penaliza cuando una materia no cumple sus horas semanales requeridas"""
        penalty = 0
        subject_hours = {}
        
        # Count assigned hours per subject
        for assignment in individual:
            subject_id = assignment['subject_id']
            if subject_id not in subject_hours:
                subject_hours[subject_id] = 0
            subject_hours[subject_id] += 2
        
        # Check required hours with stricter penalties
        for subject_id, hours in subject_hours.items():
            required_hours = subjects_dict[subject_id].hours_per_week
            if hours != required_hours:  # Must be exact match
                penalty += 2000 * abs(hours - required_hours)
                    
        return penalty
    
    def calculate_odd_hours_penalty(self, individual, subjects_dict):
        """Penaliza la mala distribución de horas para materias con horas impares"""
        penalty = 0
        subject_hours_per_day = {}
        
        # Agrupar horas por materia y día
        for assignment in individual:
            subject_id = assignment['subject_id']
            day = assignment['day']
            key = (subject_id, day)
            
            if key not in subject_hours_per_day:
                subject_hours_per_day[key] = 0
            subject_hours_per_day[key] += 2
        
        # Verificar distribución para materias con horas impares
        subject_total_hours = {}
        for (subject_id, day), hours in subject_hours_per_day.items():
            if subject_id not in subject_total_hours:
                subject_total_hours[subject_id] = []
            subject_total_hours[subject_id].append(hours)
        
        for subject_id, hours_list in subject_total_hours.items():
            required_hours = subjects_dict[subject_id].hours_per_week
            
            # Si la materia tiene horas impares
            if required_hours % 2 != 0:
                # Debe haber exactamente un día con 3 horas
                three_hour_days = sum(1 for h in hours_list if h == 3)
                two_hour_days = sum(1 for h in hours_list if h == 2)
                
                if three_hour_days != 1:
                    penalty += 1000  # Penalización por no tener un día de 3 horas
                
                # El resto de los días deberían ser de 2 horas
                expected_two_hour_days = (required_hours - 3) // 2
                if two_hour_days != expected_two_hour_days:
                    penalty += 500 * abs(two_hour_days - expected_two_hour_days)
        
        return penalty

    def evaluate_schedule(self, individual):
        """Calcula el fitness del horario (menor es mejor)"""
        # Cache database queries
        subjects_dict = {s.id: s for s in Subject.objects.all()}
        teachers_dict = {t.id: t for t in Teacher.objects.all()}
        rooms_dict = {r.id: r for r in Room.objects.all()}
        courses_dict = {c.id: c for c in Course.objects.all()}
        
        total_penalty = 0
        total_penalty += self.calculate_overlap_penalty(individual)
        total_penalty += self.calculate_teacher_movement_penalty(individual, teachers_dict)
        total_penalty += self.calculate_lab_usage_penalty(individual, subjects_dict, rooms_dict)
        total_penalty += self.calculate_teacher_preference_penalty(individual, teachers_dict)
        total_penalty += self.calculate_course_shift_penalty(individual)
        total_penalty += self.calculate_hours_penalty(individual, subjects_dict)  # Nueva penalización
        total_penalty += self.calculate_duplicate_penalty(individual)  # Nueva penalización
        total_penalty += self.calculate_distribution_penalty(individual)  # Nueva penalización
        total_penalty += self.calculate_split_teacher_penalty(individual)
        total_penalty += self.calculate_odd_hours_penalty(individual, subjects_dict)  # Nueva penalización

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

    def calculate_teacher_movement_penalty(self, individual, teachers_dict):
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

    def calculate_lab_usage_penalty(self, individual, subjects_dict, rooms_dict):
        """Verifica uso correcto de laboratorios"""
        penalty = 0
        
        for assignment in individual:
            subject = subjects_dict[assignment['subject_id']]
            room = rooms_dict[assignment['room_id']]
            
            if subject.requires_lab and room.room_type not in ['COMP', 'LOG']:
                penalty += 1000
            if not subject.requires_lab and room.room_type in ['COMP', 'LOG']:
                penalty += 500
                
        return penalty

    def calculate_teacher_preference_penalty(self, individual, teachers_dict):
        """Penalización más estricta para profesores de Montevideo"""
        penalty = 0
        for assignment in individual:
            teacher = teachers_dict[assignment['teacher_id']]
            if teacher.from_montevideo:
                hour = int(assignment['start_time'].split(':')[0])
                if hour >= 21:
                    penalty += 500  # Penalización muy alta para horarios nocturnos
                elif hour >= 19:
                    penalty += 300  # Penalización alta para horarios tarde-noche
        return penalty

    def calculate_course_shift_penalty(self, individual):
        """Verifica que los horarios coincidan con el turno del curso"""
        penalty = 0
        shift_hours = {
            'MORNING': (8, 12),
            'AFTERNOON': (14, 18),
            'NIGHT': (19, 23)  # Extended until 23:00
        }
        
        for assignment in individual:
            course = Course.objects.get(id=assignment['course_id'])
            hour = int(assignment['start_time'].split(':')[0])
            start, end = shift_hours[course.shift]
            
            if not (start <= hour < end):
                penalty += 1000  # Increased penalty for wrong shift
                    
        return penalty
    
    def calculate_duplicate_penalty(self, individual):
        """Penaliza horarios duplicados de la misma materia"""
        penalty = 0
        subject_slots = {}
        
        for assignment in individual:
            subject_id = assignment['subject_id']
            day = assignment['day']
            time = assignment['start_time']
            key = (subject_id, day, time)
            
            if key in subject_slots:
                penalty += 200  # Penalización muy alta por duplicados
            subject_slots[key] = True
            
        return penalty
    
    def calculate_distribution_penalty(self, individual):
        """Penalización para distribución de horas, permitiendo bloques de 3 horas"""
        penalty = 0
        subject_days = {}
        subject_hours_per_day = {}
        
        for assignment in individual:
            subject_id = assignment['subject_id']
            day = assignment['day']
            
            # Contabilizar horas por día para cada materia
            key = (subject_id, day)
            if key not in subject_hours_per_day:
                subject_hours_per_day[key] = 0
            subject_hours_per_day[key] += 2
            
            # Penalizar más de 3 horas por día de la misma materia
            if subject_hours_per_day[key] > 3:
                penalty += 100  # Penalización reducida por exceder 3 horas
            
            if subject_id not in subject_days:
                subject_days[subject_id] = set()
            subject_days[subject_id].add(day)
        
        # Penalizar concentración de clases
        day_order = {'MON': 0, 'TUE': 1, 'WED': 2, 'THU': 3, 'FRI': 4}
        for days in subject_days.values():
            days_list = sorted([day_order[day] for day in days])
            # Penalización más suave para días consecutivos
            for i in range(len(days_list) - 1):
                if days_list[i + 1] - days_list[i] == 1:
                    penalty += 50  # Penalización reducida para días consecutivos
        
        return penalty
    
    def calculate_split_teacher_penalty(self, individual):
        """Penaliza cuando una materia tiene diferentes profesores"""
        penalty = 0
        subject_teachers = {}
        
        for assignment in individual:
            subject_id = assignment['subject_id']
            teacher_id = assignment['teacher_id']
            
            if subject_id not in subject_teachers:
                subject_teachers[subject_id] = set()
            subject_teachers[subject_id].add(teacher_id)
            
            # Penalizar fuertemente si hay más de un profesor por materia
            if len(subject_teachers[subject_id]) > 1:
                penalty += 300
                
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
        try:
            # Verifica que haya datos suficientes
            courses = Course.objects.all()
            subjects = Subject.objects.all()
            teachers = Teacher.objects.all()
            rooms = Room.objects.all()

            if not (courses.exists() and subjects.exists() and teachers.exists() and rooms.exists()):
                raise ValueError("No hay suficientes datos para generar horarios")

            # Configuración del algoritmo
            population = self.toolbox.population(n=100)
            
            if not population:
                raise ValueError("No se pudo generar la población inicial")

            # Evolución
            result, logbook = algorithms.eaSimple(
                population, 
                self.toolbox, 
                cxpb=0.7,  # probabilidad de cruce
                mutpb=0.4,  # probabilidad de mutación
                ngen=200,   # número de generaciones
                verbose=True
            )

            # Obtén el mejor individuo
            best = tools.selBest(result, k=1)[0]
            
            # Retorna la lista de asignaciones del mejor individuo
            return list(best)  # Convertir a lista normal para serialización

        except Exception as e:
            print(f"Error generando horarios: {str(e)}")
            raise