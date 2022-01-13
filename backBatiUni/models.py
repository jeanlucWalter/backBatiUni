from django.db import models
from django.contrib.auth.models import User

class CommonModel(models.Model):
  class Meta:
    abstract = True

  @classmethod
  def dumpStructure(cls, user):
    dictAnswer = {}
    tableName = cls._meta.verbose_name.title().replace(" ", "")
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
      elif field == "date":
        values.append(instance.date.strftime("%Y/%m/%d"))
      else:
        values.append(getattr(instance, field))
    return values

  @classmethod
  def filter(cls, user):
    return cls.objects.all()

  def setAttr(self, fieldName, value):
    listMetaFields = [field.name for field in self._meta.fields]
    if fieldName + "Internal" in listMetaFields:
      self.setAttr(fieldName, value)
    elif isinstance(self._meta.get_field(fieldName), models.ForeignKey):
      foreign = self._meta.get_field(fieldName).remote_field.model
      newValue = foreign.objects.get(id=value)
      setattr(self, fieldName, newValue)
    elif isinstance(self._meta.get_field(fieldName), models.ManyToManyField):
      foreign = self._meta.get_field(fieldName).remote_field.model
      for index in value:
        newValue = foreign.objects.get(id=index)
    else:
      setattr(self, fieldName, value)

  def getAttr(self, fieldName, answer=False):
    return getattr(self, fieldName, answer)

class Label(CommonModel):
  name = models.CharField('Nom du label', unique=True, max_length=128, null=False, default=False, blank=False)

class Role(CommonModel):
  name = models.CharField('Profil du compte', unique=True, max_length=128)

class Job(CommonModel):
  name = models.CharField('Nom du métier', unique=True, max_length=128)

class Company(CommonModel):
  name = models.CharField('Nom de la société', unique=True, max_length=128, null=False, blank=False)
  siret = models.CharField('Numéro de Siret', unique=True, max_length=32, null=True, default=None)
  capital = models.IntegerField("Capital de l'entreprise", null=True, default=None)
  revenue = models.FloatField("Capital de l'entreprise", null=True, default=None)
  logo = models.CharField("Path du logo de l'entreprise", max_length=256, null=True, default=None)
  webSite = models.CharField("Url du site Web", max_length=256, null=True, default=None)
  stars = models.IntegerField("Notation sous forme d'étoile", null=True, default=None)
  companyPhone = models.CharField("Téléphone du standard", max_length=128, blank=False, null=True, default=None)

  @classmethod
  def filter(cls, user):
    userProfile = UserProfile.objects.get(userNameInternal=user)
    return [userProfile.company]


class JobForCompany(CommonModel):
  job = models.ForeignKey(Job, on_delete=models.PROTECT, blank=False, null=False)
  number = models.IntegerField("Nombre de profils ayant ce metier", null=False, default=1)
  company = models.ForeignKey(Company, on_delete=models.PROTECT, blank=False, null=False)

  class Meta:
    unique_together = ('job', 'company')

  @classmethod
  def filter(cls, user):
    userProfile = UserProfile.objects.get(userNameInternal=user)
    company = userProfile.company
    return cls.objects.filter(company=company)

class LabelForCompany(CommonModel):
  label = models.ForeignKey(Label, on_delete=models.PROTECT, blank=False, null=False)
  date = models.DateField(verbose_name="Date de péremption", null=True, default=None)
  company = models.ForeignKey(Company, on_delete=models.PROTECT, blank=False, null=False)

  class Meta:
    unique_together = ('label', 'company')

  @classmethod
  def filter(cls, user):
    userProfile = UserProfile.objects.get(userNameInternal=user)
    company = userProfile.company
    return cls.objects.filter(company=company)

class UserProfile(CommonModel):
  userNameInternal = models.OneToOneField(User, on_delete=models.PROTECT)
  company = models.ForeignKey(Company, on_delete=models.PROTECT, blank=False, null=False)
  firstName = models.CharField("Prénom", max_length=128, blank=False, default="Inconnu")
  lastName = models.CharField("Nom de famille", max_length=128, blank=False, default="Inconnu")
  proposer = models.IntegerField(blank=False, null=True, default=None)
  role = models.ForeignKey(Role, on_delete=models.PROTECT, blank=False, null=False)
  cellPhone = models.CharField("Téléphone mobile", max_length=128, blank=False, null=True, default=None)

  @property
  def userName(self):
    return self.userNameInternal.username

  def getAttr(self, fieldName, answer=False):
    if fieldName == "userName":
      user = self.userNameInternal
      return user.username
    return getattr(self, fieldName, answer)

  def setAttr(self, fieldName, value):
    if fieldName == "userName":
      user = self.userNameInternal
      user.username = value
      user.save()
    super().setAttr(fieldName, value)

  class Meta:
    verbose_name = "UserProfile"
  
  @classmethod
  def filter(cls, user):
    return [UserProfile.objects.get(userNameInternal=user)]

  @property
  def getRole(self):
    if self.role == 1:
      return "Entreprise"
    if self.role == 2:
      return "Sous-traitant"
    if self.role == 3:
      return "Sous-traitant et entreprise"

class Files(models.Model):
  nature = models.CharField('nature du fichier', unique=True, max_length=128, null=False, default=False, blank=False)
  name = models.CharField('Nom du fichier pour le front', unique=True, max_length=128, null=False, default=False, blank=False)
  path = models.CharField('path', max_length=256, null=False, default=False, blank=False)
  ext = models.CharField('extension', unique=True, max_length=8, null=False, default=False, blank=False)
  user = models.ForeignKey(UserProfile, on_delete=models.PROTECT, blank=False, null=False)
  dictPath = {"userImage":"./files/avatars"}

  class Meta:
    unique_together = ('nature', 'name', 'user')


  @classmethod
  def createFile(cls, nature, name, ext, user):
    userProfile = UserProfile.objects.get(userNameInternal=user)
    path = None
    if nature == "userImage":
      path = cls.dictPath[nature] + userProfile.firstName + '_' + userProfile.lastName + '_' + str(user.id) + '.' + ext
    if not Files.objects.filter(nature=nature, name=name, user=userProfile):
      cls.objects.create(nature=nature, name=name, path=path, ext=ext, user=userProfile)
    return path

    



