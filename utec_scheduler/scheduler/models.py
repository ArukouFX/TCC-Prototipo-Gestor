from django.db import models

class Room(models.Model):
    ROOM_TYPES = [
        ('CLASS', 'Salón de clase'),
        ('MULTI', 'Salón multipropósito'),
        ('COWORK', 'Espacio de coworking'),
        ('COMP', 'Laboratorio de Informática'),
        ('LOG', 'Laboratorio de Logística'),
    ]
    
    name = models.CharField(max_length=100)
    room_type = models.CharField(max_length=10, choices=ROOM_TYPES)
    capacity = models.IntegerField()

class Course(models.Model):
    SHIFTS = [
        ('MORNING', 'Mañana'),
        ('AFTERNOON', 'Tarde'),
        ('NIGHT', 'Noche'),
    ]
    
    name = models.CharField(max_length=100)
    shift = models.CharField(max_length=10, choices=SHIFTS)

class Subject(models.Model):
    PRIORITY_SUBJECTS = [
        ('PHYSICS', 'Física'),
        ('ELECTRO', 'Electro Electrónica'),
        ('ATO', 'ATO'),
        ('MATERIALS', 'Ciencia de los materiales'),
    ]
    
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    priority = models.BooleanField(default=False)
    priority_type = models.CharField(max_length=10, choices=PRIORITY_SUBJECTS, null=True, blank=True)
    requires_lab = models.BooleanField(default=False)
    hours_per_week = models.IntegerField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='subjects')

class Teacher(models.Model):
    name = models.CharField(max_length=100)
    subjects = models.ManyToManyField(Subject)
    from_montevideo = models.BooleanField(default=False)

class Schedule(models.Model):
    DAYS = [
        ('MON', 'Lunes'),
        ('TUE', 'Martes'),
        ('WED', 'Miércoles'),
        ('THU', 'Jueves'),
        ('FRI', 'Viernes'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    day = models.CharField(max_length=3, choices=DAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()