from django.shortcuts import render, redirect
from django.http.response import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.messages import constants
from django.contrib import messages
from django.core.exceptions import ValidationError

from .models import Mentorados, Navigators


# Create your views here.
@login_required(login_url="login")
def mentorados(request):
    logged_user = request.user

    if request.method == "GET":
        navigators = Navigators.objects.filter(mentor=logged_user.id)
        mentorados = Mentorados.objects.filter(mentor=logged_user)

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
            messages.add_message(request, level=constants.ERRROR, message=f"{errors}")
            return redirect("mentorados")

        mentorado.save()

        messages.add_message(request, level=constants.SUCCESS, message="Mentorado cadastrado com sucesso.")
        return redirect("mentorados")
    
    return HttpResponse("Método Http não aceito.")