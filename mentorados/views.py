from django.shortcuts import render, redirect
from django.http.response import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.messages import constants
from django.contrib import messages
from django.core.exceptions import ValidationError

from datetime import datetime, timedelta

from .models import Mentorados, Navigators, DisponibilidadeHorario


# Create your views here.
@login_required(login_url="login")
def mentorados(request):
    logged_user = request.user

    if request.method == "GET":
        navigators = Navigators.objects.filter(mentor=logged_user.id)
        mentorados = Mentorados.objects.filter(mentor=logged_user)

        # Carregando dados do gráfico
        qtd_estagios = []
        estagios = []
        for i, j in Mentorados.estagio_choices:
            x = mentorados.filter(estagio=i)
            estagios.append(j)
            qtd_estagios.append(x.count())

        return render(
            request, 
            "mentorados.html", 
            {
                "estagios": Mentorados.estagio_choices, 
                "navigators": navigators, 
                "mentorados": mentorados,
                "qtd_estagios": qtd_estagios,
                "estagios_mentorados": estagios,
            }
        )
    
    elif request.method == "POST":
        nome = request.POST.get("nome")
        foto = request.FILES.get("foto")
        estagio = request.POST.get("estagio")
        navigator = request.POST.get("navigator", None)

        mentorado = Mentorados(
            nome=nome, 
            foto=foto, 
            estagio=estagio, 
            navigator_id=navigator, 
            mentor=logged_user
        )

        try:
            mentorado.full_clean()
        except ValidationError as e:
            errors = [v for v in e.message_dict.values() ]
            messages.add_message(request, level=constants.ERROR, message=f"{errors}")
            return redirect("mentorados")

        mentorado.save()

        messages.add_message(request, level=constants.SUCCESS, message="Mentorado cadastrado com sucesso.")
        return redirect("mentorados")
    
    return HttpResponse("Método Http não aceito.")

@login_required(login_url="login")
def reunioes(request):
    if request.method == "GET":
        horarios = DisponibilidadeHorario.objects.filter(mentor=request.user)

        return render(request, "reunioes.html")
    elif request.method == "POST":
        data = request.POST["data"]
        data = datetime.strptime(data, r"%Y-%m-%dT%H:%M")

        horarios = DisponibilidadeHorario.objects.filter(mentor=request.user).filter(
            data_inicial__gte=(data - timedelta(minutes=50)), 
            data_inicial__lte=(data + timedelta(minutes=50)),
        )

        # Verifica se já existe um reunião que acontecerá no horário desejado
        if horarios.exists():
            messages.add_message(
                request, 
                constants.ERROR, 
                "Você já possui outro horário agendado!"
            )
            return redirect("reunioes")

        disponibilidade = DisponibilidadeHorario(
            data_inicial=data,
            mentor=request.user,
        )
        disponibilidade.save()

        messages.add_message(request, constants.SUCCESS, "Horário agendado com sucesso.")
        return redirect("reunioes")
    
    return HttpResponse("Método HTTP não aceito.")

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
        
        response = redirect("escolher_dia")
        response.headers["auth_token"] = token

        return response
        ...

    return HttpResponse("Método HTTP não aceito.")