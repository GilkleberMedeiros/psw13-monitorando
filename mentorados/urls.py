from django.urls import path
from django.shortcuts import redirect

from . import views


urlpatterns = [
    path("", views.mentorados, name="mentorados"),
    path("reunioes/", views.reunioes, name="reunioes"),
    path("auth_mentorado/", views.auth_mentorado, name="auth_mentorado"),
    path("escolher_dia/", views.escolher_dia, name="escolher_dia"),
    path("agendar_reuniao/", views.agendar_reuniao, name="agendar_reuniao"),
    path("tarefa/<int:id>/", views.tarefa, name="tarefa"),
    path("tarefa/<int:tarefa_id>/deletar/", views.deletar_tarefa, name="deletar_tarefa"),
    path("tarefas_mentorado/<int:id>/", views.tarefas_mentorados, name="tarefas_mentorado"),
    path("marcar_tarefa/<int:id>/", views.marcar_tarefa, name="marcar_tarefa"),
    path("navigators/", views.navigators, name="navigators"),
]