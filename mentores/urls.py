from django.urls import path

from . import views


urlpatterns = [
    path("", views.mentorados, name="mentorados"), 
    path("cadastro/", views.cadastro, name="cadastro"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("reunioes/", views.reunioes, name="reunioes"), 
    path("navigators/", views.navigators, name="navigators"), 
    path("tarefa/<int:id>/", views.tarefa, name="tarefa"),
    path("tarefa/<int:tarefa_id>/deletar/", views.deletar_tarefa, name="deletar_tarefa"),
    path("tarefa/gravacoes/<int:gravacao_id>/deletar/", views.deletar_gravacao, name="deletar_gravacao"),
]