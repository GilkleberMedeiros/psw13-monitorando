from django.shortcuts import render, redirect
from django.http.response import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.messages import constants
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http.request import HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse

from datetime import datetime, timedelta
from urllib.parse import urljoin

from .models import (
    Mentorados, 
    Navigators, 
    DisponibilidadeHorario, 
    Reuniao,
    Tarefa,
    Video,
)
from .auth import auth_mentorado_token_required, valida_token


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
        reunioes = Reuniao.objects.filter(data__mentor=request.user)

        return render(request, "reunioes.html", context={"reunioes": reunioes})
    elif request.method == "POST":
        data = request.POST["data"]
        data = datetime.strptime(data, r"%Y-%m-%dT%H:%M")

        duracao_reuniao = DisponibilidadeHorario.duracao_reuniao

        horarios = DisponibilidadeHorario.objects.filter(mentor=request.user).filter(
            data_inicial__gte=(data - timedelta(minutes=duracao_reuniao)), 
            data_inicial__lte=(data + timedelta(minutes=duracao_reuniao)),
        )

        # Verifica se já existe uma reunião que acontecerá no horário desejado
        if horarios.exists():
            messages.add_message(
                request, 
                constants.ERROR, 
                "Você já possui outra reunião nesse horário!"
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
        
        mentorado = mentorado.get(token=token)
        response = redirect("tarefas_mentorado", id=mentorado.id)
        response.set_cookie("auth_token", token, max_age=3600)

        return response

    return HttpResponse("Método HTTP não aceito.")

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

        horario.agendado = True
        horario.save()
        reuniao.save()

        messages.add_message(request, constants.SUCCESS, "Horário agendado com sucesso!")
        return redirect("escolher_dia")

    return HttpResponse("Método HTTP não aceito.")

@login_required(login_url="login")
def tarefa(request: HttpRequest, id: int):
    try:
        mentorado = Mentorados.objects.get(id=id)
    except:
        messages.add_message(request, constants.ERROR, "Mentorado não encontrado.")
        return redirect("mentorados")
    
    # validando se mentorado selecionado é do mentor usuário.
    if mentorado.mentor != request.user:
        messages.add_message(request, constants.ERROR, "Mentorado selecionado não encontrado.")
        return redirect("mentorados")

    if request.method == "GET":
        tarefas = Tarefa.objects.filter(mentorado=mentorado)
        videos = Video.objects.filter(mentorado=mentorado)

        return render(request, "tarefa.html", context={
            "mentorado": mentorado, 
            "tarefas": tarefas, 
            "videos": videos
        })

    elif request.method == "POST":
        tarefa = request.POST.get("tarefa")
        video = request.FILES.get("video")

        if tarefa is not None:
            Tarefa(mentorado=mentorado, tarefa=tarefa).save()
        
        if video is not None:
            Video(mentorado=mentorado, video=video).save()
        
        return redirect(f"/mentorados/tarefa/{mentorado.id}/")

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

        return redirect(f"/mentorados/tarefas_mentorado/{mentorado.id}/")
    
    return HttpResponse("Método HTTP não aceito.")

@login_required(login_url="login")
def navigators(request: HttpRequest) -> HttpResponse:
    mentor = request.user
    navs = Navigators.objects.all()
    navs = navs.filter(mentor=mentor)

    if request.method == "GET":
        return render(request, "navigators.html", context={"navigators": navs})
    
    elif request.method == "POST":
        nav_nome = request.POST.get("name", None)

        if not nav_nome:
            message="Não foi possível pegar o nome do navigator!"
            messages.add_message(request, level=constants.ERROR, message=message)
            return redirect("navigators")
    
        try: 
            navigator = Navigators(nome=nav_nome, mentor=mentor)
            navigator.save()
        except Exception as error:
            message = f"{error}"
            messages.add_message(request, level=constants.ERROR, message=message)
            return render(request, "navigators.html", context={"navigators": navs})

        return redirect("navigators")
    
    return HttpResponse("Método HTTP não aceito.")

@login_required(login_url="login")
def deletar_tarefa(request: HttpRequest, tarefa_id: int) -> HttpResponse:
    mentor = request.user

    try:
        tarefa = Tarefa.objects.get(id=tarefa_id)
    except Exception as err:
        on_error_url = reverse("mentorados")
        on_error_context = { "tempo_redirect": 5, "redirect_url": on_error_url }
        on_error_context["erro"] = f"Não pôde encontrar a tarefa com id {tarefa_id}!"

        return render(request, "pagina_erro_generico.html", context=on_error_context)
    
    mentorado = tarefa.mentorado

    on_error_url = reverse("tarefa", kwargs={ "id": mentorado.id })
    on_error_context = { "tempo_redirect": 5, "redirect_url": on_error_url }
    
    # Se mentorado não pertence ao mentor
    if mentorado.mentor != mentor:
        on_error_context["erro"] = "O mentorado informado não pertence ao mentor logado!"
        return render(request, "pagina_erro_generico.html", context=on_error_context)
    
    try:
        tarefa.delete()
    except Exception as err:
        on_error_context["erro"] = "Devido à algum erro no banco de dados, não foi possível apagar a tarefa!"
        return render(request, "pagina_erro_generico.html", context=on_error_context)
    
    return redirect("tarefa", id=mentorado.id)
