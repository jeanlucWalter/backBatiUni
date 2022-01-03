from django.db import models
from django.contrib.auth.models import User

class Company(models.Model):
  name = models.CharField('Nom de la société', unique=True, max_length=128, null=False, default=False, blank=False)
  siret = models.CharField('Numéro de Siret', max_length=32, unique=True)


class Job(models.Model):
  name = models.CharField('Nom du métier', unique=True, max_length=128)

class userProfile(models.Model):
  user = models.OneToOneField(User, on_delete=models.DO_NOTHING)
  company = models.ForeignKey(Company, on_delete=models.PROTECT, blank=False, null=False)
  firstName = models.CharField("Prénom", max_length=128, blank=False, default="Inconnu")
  lastName = models.CharField("Nom de famille", max_length=128, blank=False, default="Inconnu")
  jobs = models.OneToOneField('Job', on_delete=models.DO_NOTHING, default=None)
  proposer = models.IntegerField(blank=False, null=False, default=1)
  role = models.IntegerField(blank=False, null=False, default=1)

