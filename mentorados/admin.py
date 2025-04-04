from django.contrib import admin

from .models import Mentorados, Navigators, DisponibilidadeHorario, Reuniao


admin.site.register(Mentorados)
admin.site.register(Navigators)
admin.site.register(DisponibilidadeHorario)
admin.site.register(Reuniao)