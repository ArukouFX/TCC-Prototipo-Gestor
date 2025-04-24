import pygad
import numpy as np
from scheduler.models import Room, Course, Subject, Teacher
import random

class ScheduleGenerator:
    def __init__(self, **validated_data):
        self.validated_data = validated_data
        self.courses = list(Course.objects.all())
        self.subjects = list(Subject.objects.all())
        self.teachers = list(Teacher.objects.all())
        self.rooms = list(Room.objects.all())
        self.DAYS = ['MON', 'TUE', 'WED', 'THU', 'FRI']
        self.TIME_SLOTS = ['08:00', '10:00', '14:00', '16:00', '19:00', '21:00']
        self.assignment_size = 7  # course, subject, teacher, room, day, start_time, slot_hours
        self.assignments = self._build_assignment_list()
        self.num_assignments = len(self.assignments)
        self.num_genes = self.num_assignments * self.assignment_size
        self.gene_space = self._build_gene_space()

    def _build_assignment_list(self):
        assignments = []
        for course in self.courses:
            course_subjects = list(Subject.objects.filter(course=course))
            for subject in course_subjects:
                hours = subject.hours_per_week
                blocks = []
                # Preferir bloques de 3h, el resto de 2h
                while hours >= 3:
                    blocks.append(3)
                    hours -= 3
                while hours >= 2:
                    blocks.append(2)
                    hours -= 2
                # Si queda 1h, penalizará en fitness (no se asigna bloque de 1h)
                for slot_hours in blocks:
                    assignments.append((course, subject, slot_hours))
        return assignments

    def _build_gene_space(self):
        gene_space = []
        for course, subject, slot_hours in self.assignments:
            # course_id
            gene_space.append({'low': course.id, 'high': course.id})
            # subject_id
            gene_space.append({'low': subject.id, 'high': subject.id})
            # teacher_id (solo los que pueden dictar la materia)
            valid_teachers = list(Teacher.objects.filter(subjects=subject))
            teacher_ids = [t.id for t in valid_teachers] if valid_teachers else [self.teachers[0].id]
            gene_space.append(teacher_ids)
            # room_id (todas las posibles)
            room_ids = [r.id for r in self.rooms]
            gene_space.append(room_ids)
            # day
            gene_space.append(list(range(len(self.DAYS))))
            # start_time
            gene_space.append(list(range(len(self.TIME_SLOTS))))
            # slot_hours (fijo para este bloque)
            gene_space.append([slot_hours])
        return gene_space

    def _decode_solution(self, solution):
        assignments = []
        for i in range(self.num_assignments):
            idx = i * self.assignment_size
            course_id = int(solution[idx])
            subject_id = int(solution[idx+1])
            teacher_id = int(solution[idx+2])
            room_id = int(solution[idx+3])
            day_idx = int(solution[idx+4])
            time_idx = int(solution[idx+5])
            slot_hours = int(solution[idx+6])
            day = self.DAYS[day_idx]
            start_time = self.TIME_SLOTS[time_idx]
            duration = slot_hours * 60
            start_hour, start_minute = map(int, start_time.split(':'))
            end_hour = start_hour + (duration // 60)
            end_minute = start_minute + (duration % 60)
            if end_minute >= 60:
                end_hour += 1
                end_minute -= 60
            # Limitar end_time a un máximo de 23:00:00
            if end_hour > 23 or (end_hour == 23 and end_minute > 0):
                end_hour = 23
                end_minute = 0
            end_time = f"{end_hour:02d}:{end_minute:02d}:00"
            assignments.append({
                'course_id': course_id,
                'subject_id': subject_id,
                'teacher_id': teacher_id,
                'room_id': room_id,
                'day': day,
                'start_time': start_time,
                'slot_hours': slot_hours,
                'duration': duration,
                'end_time': end_time
            })
        return assignments

    def fitness_func(self, ga_instance, solution, solution_idx):
        assignments = self._decode_solution(solution)
        subjects_dict = {s.id: s for s in self.subjects}
        teachers_dict = {t.id: t for t in self.teachers}
        rooms_dict = {r.id: r for r in self.rooms}
        penalties = {
            'overlap': self.calculate_overlap_penalty(assignments),
            'teacher_movement': self.calculate_teacher_movement_penalty(assignments, teachers_dict),
            'lab_usage': self.calculate_lab_usage_penalty(assignments, subjects_dict, rooms_dict),
            'teacher_preference': self.calculate_teacher_preference_penalty(assignments, teachers_dict),
            'course_shift': self.calculate_course_shift_penalty(assignments),
            'hours': self.calculate_hours_penalty(assignments, subjects_dict),
            'duplicate': self.calculate_duplicate_penalty(assignments),
            'distribution': self.calculate_distribution_penalty(assignments),
            'split_teacher': self.calculate_split_teacher_penalty(assignments),
            'odd_hours': self.calculate_odd_hours_penalty(assignments, subjects_dict),
            'course_overlap': self.calculate_course_overlap_penalty(assignments),
            'daily_hours': self.calculate_daily_hours_penalty(assignments),
            'weekly_hours': self.calculate_weekly_hours_penalty(assignments),
        }
        weights = {
            'overlap': 20,            # Duplicado
            'course_overlap': 25,     # Duplicado
            'hours': 15,              # Casi duplicado
            'lab_usage': 10,          # Duplicado
            'course_shift': 10,       # Más que duplicado
            'duplicate': 5,           
            'teacher_movement': 2,    
            'teacher_preference': 2,  
            'split_teacher': 2,      
            'distribution': 1.5,       
            'odd_hours': 0.15,         
            'daily_hours': 1,        
            'weekly_hours': 0.5,        
        }
        total_penalty = sum(penalties[k] * weights[k] for k in penalties)
        return -total_penalty  # PyGAD maximiza

    def calculate_overlap_penalty(self, assignments):
        """Calcula penalización por solapamientos"""
        penalty = 0
        schedule = {}
        for assignment in assignments:
            key = (assignment['room_id'], assignment['day'], assignment['start_time'])
            if key in schedule:
                penalty += 10  # Penalización alta por solapamiento
            schedule[key] = assignment
        return penalty

    def calculate_teacher_movement_penalty(self, assignments, teachers_dict):
        """Calcula penalización por movimiento de profesores"""
        penalty = 0
        teacher_assignments = {}
        for assignment in assignments:
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

    def calculate_lab_usage_penalty(self, assignments, subjects_dict, rooms_dict):
        """Verifica uso correcto de laboratorios"""
        penalty = 0
        for assignment in assignments:
            subject = subjects_dict[assignment['subject_id']]
            room = rooms_dict[assignment['room_id']]
            if subject.requires_lab and room.room_type not in ['COMP', 'LOG']:
                penalty += 10
            if not subject.requires_lab and room.room_type in ['COMP', 'LOG']:
                penalty += 5
        return penalty

    def calculate_teacher_preference_penalty(self, assignments, teachers_dict):
        """Penalización más estricta para profesores de Montevideo"""
        penalty = 0
        for assignment in assignments:
            teacher = teachers_dict[assignment['teacher_id']]
            hour = int(assignment['start_time'].split(':')[0])
            if teacher.from_montevideo:
                if hour >= 21:
                    penalty += 5  # Penalización muy alta para horarios nocturnos
                elif hour >= 19:
                    penalty += 3  # Penalización alta para horarios tarde-noche
        return penalty

    def calculate_course_shift_penalty(self, assignments):
        penalty = 0
        shift_hours = {
            'MORNING': (8, 12),
            'AFTERNOON': (14, 18),
            'NIGHT': (19, 23)
        }
        for assignment in assignments:
            course = Course.objects.get(id=assignment['course_id'])
            hour = int(assignment['start_time'].split(':')[0])
            start, end = shift_hours[course.shift]
            if not (start <= hour < end):
                penalty += 5  # Penalización más fuerte por bloque fuera de turno
        return penalty

    def calculate_hours_penalty(self, assignments, subjects_dict):
        """Penaliza cuando una materia no cumple sus horas semanales requeridas"""
        penalty = 0
        subject_hours = {}
        # Count assigned hours per subject
        for assignment in assignments:
            subject_id = assignment['subject_id']
            if subject_id not in subject_hours:
                subject_hours[subject_id] = 0
            subject_hours[subject_id] += 2
        # Check required hours with stricter penalties
        for subject_id, hours in subject_hours.items():
            required_hours = subjects_dict[subject_id].hours_per_week
            if hours != required_hours:  # Must be exact match
                penalty += 2 * abs(hours - required_hours)
        return penalty

    def calculate_duplicate_penalty(self, assignments):
        """Penaliza horarios duplicados de la misma materia"""
        penalty = 0
        subject_slots = {}
        for assignment in assignments:
            subject_id = assignment['subject_id']
            day = assignment['day']
            time = assignment['start_time']
            key = (subject_id, day, time)
            if key in subject_slots:
                penalty += 2  # Penalización muy alta por duplicados
            subject_slots[key] = True
        return penalty

    def calculate_distribution_penalty(self, assignments):
        """Penalización para distribución de horas, permitiendo bloques de 3 horas"""
        penalty = 0
        subject_days = {}
        subject_hours_per_day = {}
        for assignment in assignments:
            subject_id = assignment['subject_id']
            day = assignment['day']
            # Contabilizar horas por día para cada materia
            key = (subject_id, day)
            if key not in subject_hours_per_day:
                subject_hours_per_day[key] = 0
            subject_hours_per_day[key] += 2
            # Penalizar más de 3 horas por día de la misma materia
            if subject_hours_per_day[key] > 3:
                penalty += 1  # Penalización reducida por exceder 3 horas
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
                    penalty += 5  # Penalización reducida para días consecutivos
        return penalty

    def calculate_split_teacher_penalty(self, assignments):
        """Penaliza cuando una materia tiene diferentes profesores"""
        penalty = 0
        subject_teachers = {}
        for assignment in assignments:
            subject_id = assignment['subject_id']
            teacher_id = assignment['teacher_id']
            if subject_id not in subject_teachers:
                subject_teachers[subject_id] = set()
            subject_teachers[subject_id].add(teacher_id)
            # Penalizar fuertemente si hay más de un profesor por materia
            if len(subject_teachers[subject_id]) > 1:
                penalty += 3
        return penalty

    def calculate_odd_hours_penalty(self, assignments, subjects_dict):
        """Penaliza la mala distribución de horas para materias con horas impares"""
        penalty = 0
        subject_hours_per_day = {}
        # Agrupar horas por materia y día
        for assignment in assignments:
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
                    penalty += 10  # Penalización por no tener un día de 3 horas
                # El resto de los días deberían ser de 2 horas
                expected_two_hour_days = (required_hours - 3) // 2
                if two_hour_days != expected_two_hour_days:
                    penalty += 5 * abs(two_hour_days - expected_two_hour_days)
        return penalty

    def calculate_course_overlap_penalty(self, assignments):
        """Penaliza si dos materias del mismo curso se superponen en el mismo horario (aunque en diferentes salas)"""
        penalty = 0
        course_slots = {}
        for assignment in assignments:
            course_id = assignment['course_id']
            day = assignment['day']
            start = assignment['start_time']
            duration = assignment['duration']
            # Calcula el rango de tiempo ocupado
            start_hour, start_minute = map(int, start.split(':'))
            end_hour = start_hour + (duration // 60)
            end_minute = start_minute + (duration % 60)
            if end_minute >= 60:
                end_hour += 1
                end_minute -= 60
            slot = (day, start_hour, end_hour)
            if course_id not in course_slots:
                course_slots[course_id] = []
            # Verifica solapamiento con otros bloques del mismo curso
            for other in course_slots[course_id]:
                other_day, other_start, other_end = other
                if day == other_day and not (end_hour <= other_start or start_hour >= other_end):
                    penalty += 10  # Penalización fuerte por solapamiento
            course_slots[course_id].append((day, start_hour, end_hour))
        return penalty

    def calculate_daily_hours_penalty(self, assignments):
        """Penaliza si la suma de horas por día por curso es mayor a 4."""
        penalty = 0
        daily_hours = {}
        for assignment in assignments:
            course_id = assignment['course_id']
            day = assignment['day']
            key = (course_id, day)
            if key not in daily_hours:
                daily_hours[key] = 0
            daily_hours[key] += assignment['slot_hours']
        for key, hours in daily_hours.items():
            if hours > 4:
                penalty += 5 * (hours - 4)  # Penalización fuerte por cada hora extra
        return penalty

    def calculate_weekly_hours_penalty(self, assignments):
        """Penaliza si la suma de horas por semana por curso es mayor a 20."""
        penalty = 0
        weekly_hours = {}
        for assignment in assignments:
            course_id = assignment['course_id']
            if course_id not in weekly_hours:
                weekly_hours[course_id] = 0
            weekly_hours[course_id] += assignment['slot_hours']
        for course_id, hours in weekly_hours.items():
            if hours > 20:
                penalty += 10 * (hours - 20)  # Penalización más suave por cada hora extra
        return penalty

    def log_generation(self, ga_instance):
        print(f"Generation {ga_instance.generations_completed} | Best Fitness: {ga_instance.best_solution()[1]}")

    def generate(self):
        ga_instance = pygad.GA(
            num_generations=200,            # Más generaciones para mejor exploración
            num_parents_mating=50,         # Aumentar padres para más diversidad
            fitness_func=self.fitness_func,
            sol_per_pop=150,               # Población más grande
            num_genes=self.num_genes,
            gene_space=self.gene_space,
            mutation_percent_genes=60,      # Mutación más agresiva
            mutation_type="random",
            crossover_type="two_points",   # Crossover más disruptivo
            init_range_low=0,              # Rango inicial más amplio
            init_range_high=100,
            parent_selection_type="tournament", # Selección más competitiva
            K_tournament=5,                # Tamaño del torneo
            keep_parents=2,                # Elitismo moderado
            stop_criteria=["reach_100", "saturate_50"], # Criterios de parada más flexibles
            on_generation=self.log_generation
        )
        ga_instance.run()
        solution, solution_fitness, _ = ga_instance.best_solution()
        assignments = self._decode_solution(solution)
        return {
            'assignments': assignments,
            'fitness': float(solution_fitness)
        }