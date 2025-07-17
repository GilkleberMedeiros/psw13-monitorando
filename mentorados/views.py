from django.shortcuts import render, redirect
from django.http.response import HttpResponse
from django.contrib.messages import constants
from django.contrib import messages
from django.http.request import HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.db.transaction import atomic

from datetime import datetime, timedelta

from .models import (
    Mentorados, 
    DisponibilidadeHorario, 
    Reuniao,
    Tarefa,
    Video,
)
from .auth import auth_mentorado_token_required, valida_token


# Create your views here.
def auth_mentorado(request):
    if request.method == "GET":
        return render(request, "auth_mentorado.html")
    elif request.method == "POST":
        token = request.POST.get("token")

        mentorado = Mentorados.objects.filter(token=token)
        
        if not mentorado.exists():
            messages.add_message(
                request, 
                constants.ERROR, 
                "Token inválido! Não existe nenhum mentorado com esse token cadastrado."
            )
            return redirect("auth_mentorado")
        
        mentorado = mentorado.get(token=token)
        response = redirect("tarefas_mentorado", id=mentorado.id)
        response.set_cookie("auth_token", token, max_age=3600)

        return response

    return HttpResponse("Método HTTP não aceito.")

def logout_mentorado(request: HttpRequest) -> HttpResponse:
    mentorado = valida_token(request, "auth_token") 

    if mentorado is None:
        messages.add_message(request, constants.ERROR, "Token inválido.")
        return redirect("auth_mentorado")
    
    response = redirect("auth_mentorado")
    response.set_cookie("auth_token", ".", -1) # Deletando Cookie de Autenticação

    return response

def escolher_dia(request):
    if request.method == "GET":
        mentorado = valida_token(request, "auth_token")

        if mentorado is None:
            messages.add_message(request, constants.ERROR, "Token inválido.")
            return redirect("auth_mentorado")

        mentor = mentorado.mentor
        horarios = DisponibilidadeHorario.objects.filter(mentor=mentor).filter(
            data_inicial__gt=datetime.now(), 
            agendado=False
        ).values_list("data_inicial", flat=True)
        horarios = list(map(lambda i: {"datetime": i, "date": i.strftime(r"%d/%m/%Y")}, horarios))

        # Deixa os dados únicos
        conjunto = set()
        i = 0
        while i < len(horarios):
            if horarios[i]["date"] in conjunto:
                horarios.pop(i)
            else:
                conjunto.add(horarios[i]["date"])
                i += 1

        return render(request, "escolher_dia.html", context={"horarios": horarios, "mentorado": mentorado})

    return HttpResponse("Método HTTP não aceito.")

@auth_mentorado_token_required(redirect_to="auth_mentorado")
def agendar_reuniao(request):
    mentorado = valida_token(request) # Pega mentorado

    if request.method == "GET":
        data = request.GET.get("data")
        data = datetime.strptime(data, r"%d/%m/%Y")

        # Pega todos os horários que tem a data especificada.
        horarios = DisponibilidadeHorario.objects.filter(
            data_inicial__gte=data,
            data_inicial__lt=(data + timedelta(days=1)),
            mentor=mentorado.mentor,
        )

        return render(
            request, 
            "agendar_reuniao.html", 
            context={"horarios": horarios, "tags": Reuniao.tag_choices}
        )
    elif request.method == "POST": 
        horario_id = request.POST.get("horario")
        tag = request.POST.get("tag")
        descricao = request.POST.get("descricao")

        # Pega o model horario
        try:
            horario = DisponibilidadeHorario.objects.get(id=horario_id)
        except Exception as e:
            messages.add_message(request, constants.ERROR, "Horário não encontrado.")
            return redirect("escolher_dia")

        if horario.agendado or horario.mentor != mentorado.mentor:
            messages.add_message(request, constants.ERROR, "O horário escolhido já está agendado.")
            return redirect("escolher_dia")

        reuniao = Reuniao(data=horario, mentorado=mentorado, tag=tag, descricao=descricao)

        try:
            horario.agendado = True
            with atomic(using="default"): 
                horario.save()
                reuniao.save()
        except Exception as _:
            messages.add_message(
                request, 
                constants.ERROR, 
                "Houve um erro no banco de dados e por isso a operação não pôde ser completada."
            )
            return redirect("escolher_dia")

        messages.add_message(request, constants.SUCCESS, "Horário agendado com sucesso!")
        return redirect("escolher_dia")

    return HttpResponse("Método HTTP não aceito.")

@auth_mentorado_token_required(redirect_to="auth_mentorado")
def tarefas_mentorados(request: HttpRequest, id: int):
    mentorado = valida_token(request)

    if mentorado is None or mentorado.id != id:
        messages.add_message(request, constants.ERROR, "Mentorado selecionado não é o mesmo mentorado logado.")
        return redirect("auth_mentorado")
    
    if request.method == "GET":
        tarefas = Tarefa.objects.filter(mentorado_id=mentorado.id)
        videos = Video.objects.filter(mentorado_id=mentorado.id)

        return render(request, "tarefas_mentorado.html", context={
            "mentorado": mentorado,
            "tarefas": tarefas,
            "videos": videos,
        })

    return HttpResponse("Método HTTP não aceito.")

@csrf_exempt
def marcar_tarefa(request: HttpRequest, id: int):
    mentorado = valida_token(request)

    try:
        tarefa = Tarefa.objects.get(id=id)
    except:
        messages.add_message(request, constants.ERROR, "Tarefa não existe.")
        return redirect("tarefas_mentorado")

    if mentorado is None or mentorado.id != tarefa.mentorado.id:
        messages.add_message(request, constants.ERROR, "Tarefa não pertence ao mentorado logado.")
        return redirect("auth_mentorado")
    
    if request.method == "POST":
        tarefa.realizada = not tarefa.realizada
        tarefa.save()

        return redirect("tarefas_mentorado", id=mentorado.id)
    
    return HttpResponse("Método HTTP não aceito.")

