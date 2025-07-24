from django.shortcuts import render, redirect
from django.http.response import HttpResponse
from django.http.request import HttpRequest
from django.core.exceptions import ValidationError
from django.contrib.messages import constants
from django.contrib import messages
from django.contrib.auth import authenticate, logout as dj_logout
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.urls.base import reverse

from datetime import datetime, timedelta

from .models import Usuario
from mentorados.models import (
    Mentorados, 
    Navigators, 
    DisponibilidadeHorario, 
    Reuniao, 
    Tarefa, 
    Video, 
)


# Create your views here.
def cadastro(request):
    if request.method == "GET":
        return render(request, "cadastro.html")
    elif request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("senha")
        password_confirm = request.POST.get("confirmar_senha")

        if password != password_confirm:
            messages.add_message(
                request, 
                constants.ERROR, 
                "Os dados no campo senha e confirmar senha devem ser iguais!"
            )
            return redirect("cadastro")
        
        if len(password) < 6:
            messages.add_message(request, constants.ERROR, "A senha deve ter 6 ou mais caracteres!")
            return redirect("cadastro")
        
        usuario = Usuario(username=username, password=password)

        try:
            usuario.full_clean()
        except ValidationError as e:
            [ messages.add_message(request, constants.ERROR, f"{v}") for k, v in e.message_dict.items() ]
            return redirect("cadastro")
        
        Usuario.objects.create_user(username=username, password=password)

        return redirect("login")
    
    return HttpResponse("Método HTTP não aceito.")

def login(request):
    if request.method == "GET":
        return render(request, "login.html")
    elif request.method == "POST":
        username = request.POST.get("username")
        senha = request.POST.get("senha")

        user = authenticate(username=username, password=senha)

        if user is not None:
            auth.login(request, user)
            return redirect("mentorados")
        
        messages.add_message(request, constants.ERROR, "Usuário ou senha inválidos!")
        return redirect("login")

    return HttpResponse("Método HTTP não aceito.")

def logout(request: HttpRequest) -> HttpResponse:
    dj_logout(request)

    return redirect("login")

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

        # Verifica se data do agendamento é menor que data atual - 1 hora
        # (Data do agendamento deve sempre ser uma hora adiante da data atual).
        if (data - timedelta(hours=1)) < datetime.now(): 
            messages.add_message(
                request, 
                constants.ERROR, 
                "Data do agendamento deve sempre ser uma hora adiante da data atual."
            )
            return redirect("reunioes")

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
    
        navigator = Navigators(nome=nav_nome, mentor=mentor)
        navigator.save()
        try: 
            pass
        except Exception as error:
            message = f"{error}"
            messages.add_message(request, level=constants.ERROR, message=message)
            return render(request, "navigators.html", context={"navigators": navs})

        return redirect("navigators")
    
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
        
        return redirect("tarefa", id=mentorado.id)

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

@login_required(login_url="login")
def deletar_gravacao(request: HttpRequest, gravacao_id: int) -> HttpResponse:
    mentor = request.user

    try: 
        gravacao = Video.objects.get(id=gravacao_id)
    except:
        url = reverse("mentorados")
        contexto = { 
            "erro": "Gravação não pôde ser encontrada para concluir a operação!", 
            "tempo_redirect": 5, 
            "redirect_url": url
        }

        return render(request, "pagina_erro_generico.html", context=contexto)
    
    mentorado = gravacao.mentorado

    on_error_url = reverse("tarefa", kwargs={"id": mentorado.id})
    on_error_context = { "tempo_redirect": 5, "redirect_url": on_error_url }

    if mentorado.mentor != mentor:
        on_error_context["erro"] = "O mentor logado não tem permissão sobre esse mentorado!"
        return render(request, "pagina_erro_generico.html", context=on_error_context)
    
    try: 
        gravacao.delete()
    except Exception as err:
        on_error_context["erro"] = "Devido à algum problema no banco de dados não foi possível deletar a gravação!"
        return render(request, "pagina_erro_generico.html", context=on_error_context)
    
    return redirect("tarefa", id=mentorado.id)
