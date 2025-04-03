from django.db import models

from datetime import timedelta
from secrets import token_urlsafe

from usuarios.models import Usuario


class Navigators(models.Model):
    nome = models.CharField(max_length=255)
    mentor = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome

class Mentorados(models.Model):
    estagio_choices = (
        ("E1", "10-100K"),
        ("E2", "101-500K"),
        ("E3", "501-1.000.000"),
        ("E4", "1.000.001-10.000.000"),
        ("E5", "10.000.001-100.000.000"),
    )
    token_size = 16

    nome = models.CharField(max_length=255)
    foto = models.ImageField(upload_to="mentorados/fotos/", null=True, blank=True)
    estagio = models.CharField(max_length=2, choices=estagio_choices)
    navigator = models.ForeignKey(Navigators, on_delete=models.CASCADE, null=True, blank=True)
    mentor = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    token = models.CharField(max_length=token_size, default="", blank=True)
    criado_em = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.nome
    
    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_unique_token()

        return super().save(*args,**kwargs)
    
    def generate_unique_token(self):
        limit = 4000
        current = 0

        while current <= limit:
            token = token_urlsafe(self.token_size)
            mentorados = Mentorados.objects.filter(token=token)

            if not mentorados.exists():
                return token
            
            current += 1
        
        raise Exception(f"Não conseguiu gerar um token único para mentorado com {limit} tentativas.")
    

class DisponibilidadeHorario(models.Model):
    duracao_reuniao = 50 # Duração da reunião em minutos
    data_inicial = models.DateTimeField(null=True, blank=True)
    mentor = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    agendado = models.BooleanField(default=False)

    @property
    def data_final(self):
        return self.data_inicial + timedelta(minutes=self.duracao_reuniao)
    

class Reuniao(models.Model):
    tag_choices = (
        ('G', "Gestão"),
        ("M", "Marketing"),
        ("RH", "Gestão de pessoas"),
        ("I", "Impostos"),
    )

    data = models.ForeignKey(DisponibilidadeHorario, on_delete=models.CASCADE)
    mentorado = models.ForeignKey(Mentorados, on_delete=models.CASCADE)
    tag = models.CharField(max_length=2, choices=tag_choices)
    descricao = models.TextField()