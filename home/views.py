from django.shortcuts import render, redirect
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.contrib.messages import constants
from django.contrib import messages

from mentorados.models import Mentorados


def home(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        return render(request, "home.html")
    
    elif request.method == "POST":
        role = request.POST.get("role", None)
        
        if role.lower() == "mentor": 
            # se mentor já está logado
            if request.user.is_authenticated: 
                return redirect("mentorados")
            
            # se não, redirecionar para login
            return redirect("login")
        
        if role.lower() == "mentorado":
            token = request.COOKIES.get("auth_token", None)
            # Verificar se token existe no banco de dados
            mentorados = Mentorados.objects.filter(token=token)

            # Se mentorado já está logado
            if mentorados.exists():
                mentorado = mentorados.get(token=token)
                return redirect("tarefas_mentorado", id=mentorado.id)

            # Se não, redirecionar para login mentorado
            return redirect("auth_mentorado")

        # Se role inválida
        messages.add_message(request, level=constants.ERROR, message="Opção de usuário inválida!")
        return redirect("home")
    

    return HttpResponse("Método HTTP não aceito.")