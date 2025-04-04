from django.contrib import admin

from .models import Mentorados, Navigators, DisponibilidadeHorario, Reuniao, Tarefa, Video


admin.site.register(Mentorados)
admin.site.register(Navigators)
admin.site.register(DisponibilidadeHorario)
admin.site.register(Reuniao)
admin.site.register(Tarefa)
admin.site.register(Video)