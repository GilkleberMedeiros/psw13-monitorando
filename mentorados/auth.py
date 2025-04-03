from django.contrib.messages import constants, add_message
from django.shortcuts import redirect

from .models import Mentorados


def auth_mentorado_token_required(
        func = None, 
        *,
        redirect_to: str, 
        token_name: str = "auth_token",
        use_messages: bool = True, 
        message: str = "Token inválido.",
):
    """
        Valida se o usuário (mentorado) possui o token de autenticação.
    """
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            mentorado = valida_token(request, token_name)
            if mentorado is None:
                if use_messages: add_message(request, constants.ERROR, message)

                return redirect(redirect_to)
            
            return func(request, *args, **kwargs)
            
        return wrapper
    
    return decorator if func is None else decorator(func)

def valida_token(request, token_name="auth_token") -> Mentorados | None:
    """
        Retorna o mentorado se o token for válido, None caso contrário.
    """
    token = request.COOKIES.get("auth_token")
    return Mentorados.objects.filter(token=token).first()