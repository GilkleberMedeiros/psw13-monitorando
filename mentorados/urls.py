from django.urls import path

from . import views


urlpatterns = [
    path("", views.mentorados, name="mentorados"),
    path("reunioes/", views.reunioes, name="reunioes"),
    path("auth_mentorado/", views.auth_mentorado, name="auth_mentorado"),
]