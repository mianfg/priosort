import uuid
from django.db import models


class Sorteo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=50)
    id_asignacion = models.UUIDField(default=uuid.uuid4, editable=False)
    visible = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

class Item(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    sorteo = models.ForeignKey(Sorteo, on_delete=models.CASCADE)

class Persona(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=50)
    sorteo = models.ForeignKey(Sorteo, on_delete=models.CASCADE)

class Prioridad(models.Model):
    id = models.AutoField(primary_key=True)
    prioridad = models.IntegerField()
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

class Resultado(models.Model):
    id = models.AutoField(primary_key=True)
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    sorteo = models.ForeignKey(Sorteo, on_delete=models.CASCADE)
    orden = models.IntegerField(editable=False)