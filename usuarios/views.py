from django.shortcuts import render, redirect
from django.http.response import HttpResponse
from django.core.exceptions import ValidationError
from django.contrib.messages import constants
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib import auth

from .models import Usuario


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
            print(e.message_dict)
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
