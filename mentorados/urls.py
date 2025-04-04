from django.urls import path

from . import views


urlpatterns = [
    path("", views.mentorados, name="mentorados"),
    path("reunioes/", views.reunioes, name="reunioes"),
    path("auth_mentorado/", views.auth_mentorado, name="auth_mentorado"),
    path("escolher_dia/", views.escolher_dia, name="escolher_dia"),
    path("agendar_reuniao/", views.agendar_reuniao, name="agendar_reuniao"),
]