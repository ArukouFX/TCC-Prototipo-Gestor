from django.contrib import admin
from .models import Room, Course, Subject, Teacher, Schedule

admin.site.register(Room)
admin.site.register(Course)
admin.site.register(Subject)
admin.site.register(Teacher)
admin.site.register(Schedule)