from django.shortcuts import render
from django.http.response import HttpResponse


# Create your views here.
def mentorados(request):
    if request.method == "GET":
        return render(request, "mentorados.html")
    elif request.method == "POST":
        return HttpResponse(f"Post request para {request.path}")
    
    return HttpResponse("Método Http não aceito.")