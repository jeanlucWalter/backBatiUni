from django.db import models
from django.contrib.auth.models import User

class CommonModel(models.Model):
  class Meta:
    abstract = True

  @classmethod
  def listFields(cls):
    return [field.name for field in cls._meta.fields][1:]

  @classmethod
  def dictValues(cls):
    listFields = cls.listFields()
    return {instance.id:[getattr(instance, field) for field in listFields] if len(listFields) > 1 else getattr(instance, listFields[0]) for instance in cls.objects.all()}

class Company(models.Model):
  name = models.CharField('Nom de la société', unique=True, max_length=128, null=False, default=False, blank=False)
  siret = models.CharField('Numéro de Siret', max_length=32, null=True, default=None)

class Role(CommonModel):
  name = models.CharField('Profil du compte', unique=True, max_length=128)

class Job(CommonModel):
  name = models.CharField('Nom du métier', unique=True, max_length=128)

class UserProfile(models.Model):
  user = models.OneToOneField(User, on_delete=models.DO_NOTHING)
  company = models.ForeignKey(Company, on_delete=models.PROTECT, blank=False, null=False)
  firstName = models.CharField("Prénom", max_length=128, blank=False, default="Inconnu")
  lastName = models.CharField("Nom de famille", max_length=128, blank=False, default="Inconnu")
  jobs = models.ManyToManyField(Job)
  proposer = models.IntegerField(blank=False, null=True, default=None)
  role = models.ForeignKey(Role, on_delete=models.PROTECT, blank=False, null=False)

  @property
  def getRole(self):
    if self.role == 1:
      return "Entreprise"
    if self.role == 2:
      return "Sous-traitant"
    if self.role == 3:
      return "Sous-traitant et entreprise"
    



