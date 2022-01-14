from django.db import models
from django.contrib.auth.models import User
from PIL import Image
import os
import base64
from io import BytesIO
import datetime
from django.apps import apps

class CommonModel(models.Model):
  manyToManyObject = []

  class Meta:
    abstract = True

  @classmethod
  def dumpStructure(cls, user):
    dictAnswer = {}
    tableName = cls._meta.verbose_name.title().replace(" ", "")
    if len(cls.listFields()) > 1:
      dictAnswer[tableName + "Fields"] = cls.listFields()
      if len(cls.listIndices()) >= 1:
        dictAnswer[tableName + "Indices"] = cls.listIndices()
    subModels, values = cls.dictValues(user)
    dictAnswer[tableName + "Values"] = values
    if subModels:
      for subM in subModels:
        tableName = subM._meta.verbose_name.title().replace(" ", "")
        if len(subM.listFields()) > 1:
          dictAnswer[tableName + "Fields"] = subM.listFields()
          if len(subM.listIndices()) >= 1:
            dictAnswer[tableName + "Indices"] = subM.listIndices()
    return dictAnswer

  @classmethod
  def listFields(cls):
    return [field.name.replace("Internal", "") for field in cls._meta.fields][1:] + cls.manyToManyObject

  @classmethod
  def listIndices(cls):
    listName = cls.listFields()
    listMetaFields = [field.name for field in cls._meta.fields]
    listNameF = [name for name in listName if cls.testListIndices(name, listMetaFields)]
    return [listName.index(name) for name in listNameF]

  @classmethod
  def testListIndices(cls, name, listMetaFields):
    if name + "Internal" in listMetaFields: return False
    if name in cls.manyToManyObject: return True
    if hasattr(cls, name) and isinstance(cls._meta.get_field(name), models.ForeignKey): return True
    if hasattr(cls, name) and isinstance(cls._meta.get_field(name), models.ManyToManyField): return True
    return False

  @classmethod
  def dictValues(cls, user):
    listFields, dictResult, subModels = cls.listFields(), {}, []
    for instance in cls.filter(user):
      if len(listFields) > 1:
        subM, values = instance.computeValues(listFields, user)
        subModels += subM
        dictResult[instance.id] = values
      else:
        dictResult[instance.id] = getattr(instance, listFields[0])
    return subModels, dictResult

  def computeValues(self, listFields, user):
    values, subModel, listIndices = [], [], self.listIndices()
    for index in range(len(listFields)):
      field = listFields[index]
      fieldObject = None
      try:
        fieldObject = self._meta.get_field(field)
      except:
        pass
      if index in listIndices and isinstance(fieldObject, models.ForeignKey):
        values.append(getattr(self, field).id)
      elif index in listIndices and isinstance(fieldObject, models.ManyToManyField):
        values.append([element.id for element in getattr(self, field).all()])
      elif isinstance(fieldObject, models.DateField):
        values.append(getattr(self, field).strftime("%Y/%m/%d") if getattr(self, field) else None)
      elif field in self.manyToManyObject:
        model = apps.get_model(app_label='backBatiUni', model_name=field)
        subModel.append(model)
        values.append(model.dictValues(user))
      else:
        values.append(getattr(self, field, None))
    return subModel, values

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
  manyToManyObject = ["JobForCompany", "LabelForCompany", "Files"]

  @classmethod
  def filter(cls, user):
    userProfile = UserProfile.objects.get(userNameInternal=user)
    return [userProfile.Company]


class JobForCompany(CommonModel):
  job = models.ForeignKey(Job, on_delete=models.PROTECT, blank=False, null=False)
  number = models.IntegerField("Nombre de profils ayant ce metier", null=False, default=1)
  Company = models.ForeignKey(Company, on_delete=models.PROTECT, blank=False, null=False)

  class Meta:
    unique_together = ('job', 'Company')

  @classmethod
  def listFields(cls):
    return super().listFields()[:-1]

  @classmethod
  def filter(cls, user):
    userProfile = UserProfile.objects.get(userNameInternal=user)
    Company = userProfile.Company
    return cls.objects.filter(Company=Company)

class LabelForCompany(CommonModel):
  label = models.ForeignKey(Label, on_delete=models.PROTECT, blank=False, null=False)
  date = models.DateField(verbose_name="Date de péremption", null=True, default=None)
  Company = models.ForeignKey(Company, on_delete=models.PROTECT, blank=False, null=False)
  class Meta:
    unique_together = ('label', 'Company')

  @classmethod
  def listFields(cls):
    return super().listFields()[:-1]

  @classmethod
  def filter(cls, user):
    userProfile = UserProfile.objects.get(userNameInternal=user)
    Company = userProfile.Company
    return cls.objects.filter(Company=Company)

class UserProfile(CommonModel):
  userNameInternal = models.OneToOneField(User, on_delete=models.PROTECT)
  Company = models.ForeignKey(Company, on_delete=models.PROTECT, blank=False, null=False)
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

class Files(CommonModel):
  nature = models.CharField('nature du fichier', max_length=128, null=False, default=False, blank=False)
  name = models.CharField('Nom du fichier pour le front', max_length=128, null=False, default=False, blank=False)
  path = models.CharField('path', max_length=256, null=False, default=False, blank=False)
  ext = models.CharField('extension', max_length=8, null=False, default=False, blank=False)
  Company = models.ForeignKey(Company, on_delete=models.PROTECT, blank=False, default=None)
  expirationDate = models.DateField(verbose_name="Date de péremption", null=True, default=None)
  timestamp = models.FloatField(verbose_name="Timestamp de mise à jour", null=False, default=datetime.datetime.now().timestamp())
  dictPath = {"userImage":"./files/avatars/"}

  class Meta:
    unique_together = ('nature', 'name', 'Company')
    verbose_name = "Files"

  @classmethod
  def listFields(cls):
    superList = super().listFields()
    for fieldName in ["path", "Company"]:
      index = superList.index(fieldName)
      del superList[index]
    superList.append("content")
    return superList

  def getAttr(self, fieldName, answer=False):
    if fieldName == "file":
      image = Image.open(self.path)
      buffered = BytesIO()
      image.save(buffered, format=self.ext)
      return base64.b64encode(buffered.getvalue()).decode("utf-8")
    return getattr(self, fieldName, answer)

  @classmethod
  def findAvatar(cls, user):
    userProfile = UserProfile.objects.get(userNameInternal=user)
    file = cls.objects.filter(nature="userImage", Company=userProfile.Company)
    if file:
      return file[0].getAttr("file")
    return {}

  @classmethod
  def createFile(cls, nature, name, ext, user):
    userProfile = UserProfile.objects.get(userNameInternal=user)
    objectFile = None
    if nature == "userImage":
      path = cls.dictPath[nature] + userProfile.Company.name + '_' + str(userProfile.Company.id) + '.' + ext
      objectFile = Files.objects.filter(nature=nature, name=name, Company=userProfile.Company)
    if objectFile:
      objectFile = objectFile[0]
      oldPath = objectFile.path
      if os.path.exists(oldPath):
        os.remove(oldPath)
      objectFile.path = path
      objectFile.timestamp = datetime.datetime.now().timestamp()
      objectFile.ext = ext
      objectFile.save()
    else:
      objectFile = cls.objects.create(nature=nature, name=name, path=path, ext=ext, Company=userProfile.Company)
    return objectFile

    



