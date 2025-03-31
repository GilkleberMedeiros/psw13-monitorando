from django.db import models

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

    nome = models.CharField(max_length=255)
    foto = models.ImageField(upload_to="mentorados/fotos/", null=True, blank=True)
    estagio = models.CharField(max_length=2, choices=estagio_choices)
    navigator = models.ForeignKey(Navigators, on_delete=models.CASCADE, null=True, blank=True)
    mentor = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    criado_em = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.nome
