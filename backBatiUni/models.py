from django.db import models
from django.contrib.auth.models import User

class CommonModel(models.Model):
  class Meta:
    abstract = True

  @classmethod
  def dumpStructure(cls, user):
    dictAnswer = {}
    tableName = cls._meta.verbose_name.title()
    if len(cls.listFields()) > 1:
      dictAnswer[tableName + "Fields"] = cls.listFields()
      if len(cls.listIndices()) > 1:
        dictAnswer[tableName + "Indices"] = cls.listIndices()
    dictAnswer[tableName + "Values"] = cls.dictValues(user)
    return dictAnswer

  @classmethod
  def listFields(cls):
    return [field.name.replace("Internal", "") for field in cls._meta.fields][1:]

  @classmethod
  def listIndices(cls):
    listName = cls.listFields()
    listMetaFields = [field.name for field in cls._meta.fields]
    listNameF = [name for name in listName if cls.testListIndices(name, listMetaFields)]
    return [listName.index(name) for name in listNameF]

  @classmethod
  def testListIndices(cls, name, listMetaFields):
    if name + "Internal" in listMetaFields: return False
    if isinstance(cls._meta.get_field(name), models.ForeignKey): return True
    if isinstance(cls._meta.get_field(name), models.ManyToManyField): return True
    return False

  @classmethod
  def dictValues(cls, user):
    listFields = cls.listFields()
    return {instance.id:cls.computeValues(instance, listFields) if len(listFields) > 1 else getattr(instance, listFields[0]) for instance in cls.filter(user)}

  @classmethod
  def computeValues(cls, instance, listFields):
    values, listIndices = [], cls.listIndices()
    for index in range(len(listFields)):
      field = listFields[index]
      if index in listIndices and isinstance(cls._meta.get_field(field), models.ForeignKey):
        values.append(getattr(instance, field).id)
      elif index in listIndices and isinstance(cls._meta.get_field(field), models.ManyToManyField):
        values.append([element.id for element in getattr(instance, field).all()])
      else:
        values.append(getattr(instance, field))
    return values

  @classmethod
  def filter(cls, user):
    return cls.objects.all()

class Label(CommonModel):
  name = models.CharField('Nom du label', unique=True, max_length=128, null=False, default=False, blank=False)

class Company(CommonModel):
  name = models.CharField('Nom de la société', unique=True, max_length=128, null=False, blank=False)
  siret = models.CharField('Numéro de Siret', unique=True, max_length=32, null=True, default=None)
  capital = models.IntegerField("Capital de l'entreprise", null=True, default=None)
  logo = models.CharField("Path du logo de l'entreprise", max_length=256, null=True, default=None)
  webSite = models.CharField("Url du site Web", max_length=256, null=True, default=None)
  labels = models.ManyToManyField(Label)
  stars = models.IntegerField("Notation sous forme d'étoile", null=True, default=None)
  companyPhone = models.CharField("Téléphone du standard", max_length=128, blank=False, null=True, default=None)

  @classmethod
  def filter(cls, user):
    userProfile = UserProfile.objects.get(userInternal=user)
    return [userProfile.company]

class Role(CommonModel):
  name = models.CharField('Profil du compte', unique=True, max_length=128)

class Job(CommonModel):
  name = models.CharField('Nom du métier', unique=True, max_length=128)

class UserProfile(CommonModel):
  userInternal = models.OneToOneField(User, on_delete=models.PROTECT)
  company = models.ForeignKey(Company, on_delete=models.PROTECT, blank=False, null=False)
  firstName = models.CharField("Prénom", max_length=128, blank=False, default="Inconnu")
  lastName = models.CharField("Nom de famille", max_length=128, blank=False, default="Inconnu")
  jobs = models.ManyToManyField(Job)
  proposer = models.IntegerField(blank=False, null=True, default=None)
  role = models.ForeignKey(Role, on_delete=models.PROTECT, blank=False, null=False)
  cellPhone = models.CharField("Téléphone mobile", max_length=128, blank=False, null=True, default=None)

  @classmethod
  def listFields(cls):
    base = super().listFields()
    base.append("jobs")
    return base

  @property
  def user(self):
    return self.userInternal.username

  class Meta:
    verbose_name = "UserProfile"
  
  @classmethod
  def filter(cls, user):
    return [UserProfile.objects.get(userInternal=user)]

  @property
  def getRole(self):
    if self.role == 1:
      return "Entreprise"
    if self.role == 2:
      return "Sous-traitant"
    if self.role == 3:
      return "Sous-traitant et entreprise"
    



