from calendar import c
from logging.config import listen
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os
import base64
import datetime
from django.apps import apps
from pdf2image import convert_from_path

import io
import whatimage
import pyheif
from PIL import Image
from cairosvg import svg2png


class CommonModel(models.Model):
  manyToManyObject = []

  class Meta:
    abstract = True

  @classmethod
  def dumpStructure(cls, user):
    dictAnswer = {}
    tableName = cls._meta.verbose_name
    if len(cls.listFields()) > 1:
      if cls == UserProfile:
        newKey = {"FavoritePost":"favoritePosts", "ViewPost":"viewedPosts"}
        listF = [key if not key in newKey else newKey[key] for key in cls.listFields()]
        dictAnswer[tableName + "Fields"] = listF
      elif cls == Mission:
        dictAnswer[tableName + "Fields"] = cls.listFields() + ["subContractor"]
      else:
        dictAnswer[tableName + "Fields"] = cls.listFields()
      if len(cls.listIndices()) >= 1:
        if cls == Mission:
          dictAnswer[tableName + "Indices"] = cls.listIndices() + [len(cls.listFields())]
        else:
          dictAnswer[tableName + "Indices"] = cls.listIndices()
    dictAnswer[tableName + "Values"] = cls.dictValues(user)
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
    # if hasattr(cls, name) and isinstance(cls._meta.get_field(name), models.ManyToManyField): return True
    return False

  @classmethod
  def dictValues(cls, user):
    listFields, dictResult = cls.listFields(), {}
    for instance in cls.filter(user):
      if len(listFields) > 1:
        dictResult[instance.id] = instance.computeValues(listFields, user)
      else:
        dictResult[instance.id] = getattr(instance, listFields[0]) if listFields[0] != "date" else getattr(instance, "date").strftime("%Y-%m-%d")
    return dictResult

  def computeValues(self, listFields, user, dictFormat=False):
    values, listIndices = [], self.listIndices()
    for index in range(len(listFields)):
      field = listFields[index]
      fieldObject = None
      try:
        fieldObject = self._meta.get_field(field)
      except:
        pass
      if index in listIndices and isinstance(fieldObject, models.ForeignKey):
        values.append(getattr(self, field).id if getattr(self, field, None) else "")
      # elif index in listIndices and isinstance(fieldObject, models.ManyToManyField):
      #   values.append([element.id for element in getattr(self, field).all()])
      elif isinstance(fieldObject, models.DateField):
        values.append(getattr(self, field).strftime("%Y-%m-%d") if getattr(self, field) else "")
      elif isinstance(fieldObject, models.BooleanField):
        values.append(getattr(self, field))
      elif field in self.manyToManyObject:
        model = apps.get_model(app_label='backBatiUni', model_name=field)
        listFieldsModel = model.listFields()
        if field == "DatePost":
          listModel = [objectModel.date.strftime("%Y-%m-%d") for objectModel in DatePost.objects.filter(Post=self)]
          if not listModel:
            listModel = [objectModel.date.strftime("%Y-%m-%d") for objectModel in DatePost.objects.filter(Mission=self)]
        elif field == "ViewPost":
          listModel = [view.id for view in ViewPost.objects.filter(UserProfile=self)]
        elif field == "FavoritePost":
          listModel = [favorite.id for favorite in FavoritePost.objects.filter(UserProfile=self)]
        elif dictFormat:
          listModel = {objectModel.id:objectModel.computeValues(listFieldsModel, user, dictFormat=True) for objectModel in model.filter(user) if getattr(objectModel, self.__class__.__name__, False) == self}
          listModel = {key:valueList if len(valueList) != 1 else valueList[0] for key, valueList in listModel.items()}
        else:
          listModel = [objectModel.id for objectModel in model.filter(user) if getattr(objectModel, self.__class__.__name__, False) == self]
        values.append(listModel)
      else:
        value = getattr(self, field, "")
        values.append(value)
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
    # elif isinstance(self._meta.get_field(fieldName), models.ManyToManyField):
    #   foreign = self._meta.get_field(fieldName).remote_field.model
    #   for index in value:
    #     newValue = foreign.objects.get(id=index)
    else:
      setattr(self, fieldName, value)

  def getAttr(self, fieldName, answer=False):
    return getattr(self, fieldName, answer)

class Label(CommonModel):
  name = models.CharField('Nom du label', unique=True, max_length=128, null=False, default=False, blank=False)
  # description = models.CharField('Description du métier', unique=False, null=True, max_length=2048, default=None)
  # site = models.CharField('Site internet', unique=False, null=True, max_length=256, default=None)

  class Meta:
    verbose_name = "Label"

class Role(CommonModel):
  name = models.CharField('Profil du compte', unique=True, max_length=128)

  class Meta:
    verbose_name = "Role"

class Job(CommonModel):
  name = models.CharField('Nom du métier', unique=True, max_length=128)

  class Meta:
    verbose_name = "Job"

class Company(CommonModel):
  name = models.CharField('Nom de la société', unique=True, max_length=128, null=False, blank=False)
  Role = models.ForeignKey(Role, on_delete=models.PROTECT, blank=False, null=False, default=3)
  siret = models.CharField('Numéro de Siret', unique=True, max_length=32, null=True, default=None)
  address = models.CharField("Adresse de l'entreprise", unique=True, max_length=256, null=True, default=None)
  activity = models.CharField("Activite principale de l'entreprise", unique=False, max_length=256, null=False, default="")
  ntva = models.CharField("Numéro de TVA intra communautaire", unique=True, max_length=32, null=True, default=None)
  capital = models.IntegerField("Capital de l'entreprise", null=True, default=None)
  revenue = models.FloatField("Capital de l'entreprise", null=True, default=None)
  logo = models.CharField("Path du logo de l'entreprise", max_length=256, null=True, default=None)
  webSite = models.CharField("Url du site Web", max_length=256, null=True, default=None)
  stars = models.IntegerField("Notation sous forme d'étoile", null=True, default=None)
  companyPhone = models.CharField("Téléphone du standard", max_length=128, blank=False, null=True, default=None)
  amount = models.FloatField("Montant sous-traitant", null=True, default=None)
  unity = models.CharField("Unité du montant", max_length=64, null=True, default=None)
  latitude = models.FloatField("Latitude", null=True, default=None)
  longitude = models.FloatField("Longitude", null=True, default=None)
  saturdayDisponibility = models.BooleanField("Disponibilité le Samedi", null=False, default=False)
  allQualifications = models.BooleanField("Tous corps d'état", null=False, default=False)
  manyToManyObject = ["JobForCompany", "LabelForCompany", "File", "Post", "Mission", "Disponibility"]

  class Meta:
    verbose_name = "Company"

  # @classmethod
  # def filter(cls, user):
  #   userProfile = UserProfile.objects.get(userNameInternal=user)
  #   return [userProfile.Company]

  @property
  def jobs(self):
    return [jobForCompany.Job for jobForCompany in JobForCompany.objects.filter(Company=self)]

class Disponibility(CommonModel):
  Company = models.ForeignKey(Company, on_delete=models.PROTECT, blank=False, null=False)
  date = models.DateField(verbose_name="Date de disponibilité", null=True, default=None)
  nature = models.CharField('Disponibilité', unique=False, max_length=32, null=True, default="Disponible")

  class Meta:
    verbose_name = "Disponibility"

  @classmethod
  def listFields(cls):
    superList = super().listFields()
    superList.remove("Company")
    return superList

class JobForCompany(CommonModel):
  Job = models.ForeignKey(Job, on_delete=models.PROTECT, blank=False, null=False)
  number = models.IntegerField("Nombre de profils ayant ce metier", null=False, default=1)
  Company = models.ForeignKey(Company, on_delete=models.PROTECT, blank=False, null=False)

  class Meta:
    unique_together = ('Job', 'Company')
    verbose_name = "JobForCompany"

  @classmethod
  def listFields(cls):
    superList = super().listFields()
    superList.remove("Company")
    return superList

  # @classmethod
  # def filter(cls, user):
  #   userProfile = UserProfile.objects.get(userNameInternal=user)
  #   Company = userProfile.Company
  #   return cls.objects.filter(Company=Company)

class LabelForCompany(CommonModel):
  Label = models.ForeignKey(Label, on_delete=models.PROTECT, blank=False, null=False)
  date = models.DateField(verbose_name="Date de péremption", null=True, default=None)
  Company = models.ForeignKey(Company, on_delete=models.PROTECT, blank=False, null=False)

  class Meta:
    unique_together = ('Label', 'Company')
    verbose_name = "LabelForCompany"

  @classmethod
  def listFields(cls):
    superList = super().listFields()
    superList.remove("Company")
    return superList

  # @classmethod
  # def filter(cls, user):
  #   userProfile = UserProfile.objects.get(userNameInternal=user)
  #   company = userProfile.Company
  #   return cls.objects.filter(Company=company)

class UserProfile(CommonModel):
  userNameInternal = models.ForeignKey(User, on_delete=models.PROTECT, null=True, default=None)
  Company = models.ForeignKey(Company, on_delete=models.PROTECT, blank=False, null=False)
  firstName = models.CharField("Prénom", max_length=128, blank=False, default="Inconnu")
  lastName = models.CharField("Nom de famille", max_length=128, blank=False, default="Inconnu")
  proposer = models.IntegerField(blank=False, null=True, default=None)
  cellPhone = models.CharField("Téléphone mobile", max_length=128, blank=False, null=True, default=None)
  token = models.CharField("Token de validation", max_length=512, blank=True, null=True, default="empty token")
  email = models.CharField("Email", max_length=128, blank=True, null=True, default="Inconnu")
  password = models.CharField("Mot de passe", max_length=128, blank=True, null=True, default="Inconnu")
  function = models.CharField("Fonction dans l'entreprise", max_length=128, blank=True, null=True, default="")
  manyToManyObject = ["FavoritePost", "ViewPost"]

  class Meta:
    verbose_name = "UserProfile"

  @classmethod
  def listFields(cls):
    superList = super().listFields()
    superList.remove("token")
    superList.remove("password")
    return superList

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
    else:
      super().setAttr(fieldName, value)

  # @classmethod
  # def dictValues (cls, user):
  #   dictVal = super().dictValues(user)
  #   for key, newKey in {"FavoritePost":"favoritePosts", "ViewPost":"viewedPosts"}.items():
  #     if key in dictVal:
  #       dictVal[newKey] = dictVal[key]
  #       del dictVal[key]
  #     print("dictValues, userProfile", type(dictVal), dictVal)
  #   return dictVal 
  
  @classmethod
  def filter(cls, user):
    return [UserProfile.objects.get(userNameInternal=user)]

class FavoritePost(CommonModel):
  UserProfile = models.ForeignKey(UserProfile, related_name='UserProfileforFavorite', on_delete=models.PROTECT, null=True, default=None)
  postId = models.IntegerField("id du Post", blank=True, null=True, default=None)

  class Meta:
    verbose_name = "FavoritePost"
    unique_together = ('UserProfile', 'postId')

  @classmethod
  def listFields(cls):
    return ["Post"]

  @classmethod
  def dictValues(cls, user):
    return [favorite.postId for favorite in cls.filter(user)]

  @classmethod
  def filter(cls, user):
    userProfile = UserProfile.objects.get(userNameInternal=user)
    return [favorite for favorite in cls.objects.filter(UserProfile=userProfile)]



class ViewPost(CommonModel):
  UserProfile = models.ForeignKey(UserProfile, related_name='UserProfileforView', on_delete=models.PROTECT, null=True, default=None)
  postId = models.IntegerField("id du Post", blank=True, null=True, default=None)

  class Meta:
    verbose_name = "ViewPost"
    unique_together = ('UserProfile', 'postId')

  @classmethod
  def listFields(cls):
    return ["Post"]

  @classmethod
  def dictValues(cls, user):
    return [favorite.postId for favorite in cls.filter(user)]

  @classmethod
  def filter(cls, user):
    userProfile = UserProfile.objects.get(userNameInternal=user)
    return [favorite for favorite in cls.objects.filter(UserProfile=userProfile)]

class Post(CommonModel):
  Company = models.ForeignKey(Company, related_name='Company', verbose_name='Société demandeuse', on_delete=models.PROTECT, null=True, default=None) 
  Job = models.ForeignKey(Job, verbose_name='Métier', on_delete=models.PROTECT, blank=False, default=None) 
  numberOfPeople = models.IntegerField("Nombre de personne(s) demandées", blank=False, null=False, default=1)
  address = models.CharField("Adresse du chantier", max_length=1024, null=True, default=None)
  latitude = models.FloatField("Latitude", null=True, default=None)
  longitude = models.FloatField("Longitude", null=True, default=None)
  contactName = models.CharField("Nom du contact responsable de la mission", max_length=256, null=True, default=None)
  draft = models.BooleanField("Brouillon ou validé", null=False, default=True)
  manPower = models.BooleanField("Main d'oeuvre ou fourniture et pose", null=False, default=True)
  dueDate = models.DateField(verbose_name="Date de d'échéance de l'annonce", null=True, default=None)
  startDate = models.DateField(verbose_name="Date de début de chantier", null=True, default=None)
  endDate = models.DateField(verbose_name="Date de fin de chantier", null=True, default=None)
  hourlyStart = models.CharField("Horaire de début de chantier", max_length=128, null=True, default=None)
  hourlyEnd = models.CharField("Horaire de fin de chantier", max_length=128, null=True, default=None)
  amount = models.FloatField("Montant du chantier", null=False, default=0.0)
  currency = models.CharField("Unité monétaire", max_length=128, null=True, default="€")
  unitOfTime = models.CharField("Unité de temps", max_length=128, null=True, default="Prix Journalier")
  counterOffer = models.BooleanField("Autoriser une contre offre", null=False, default=False)
  description = models.CharField("Description du chantier", max_length=4096, null=True, default=None)
  signedByCompany = models.BooleanField("Signature de la PME", null=False, default=False)
  signedBySubContractor = models.BooleanField("Signature du ST", null=False, default=False)
  subContractorContact = models.CharField("Contact chez le sous traitant", max_length=128, null=True, default=None)
  subContractorName = models.CharField("Nom le sous traitant", max_length=128, null=True, default=None)
  quality = models.IntegerField("Qualité du travail fourni", blank=False, null=False, default=1)
  qualityComment = models.TextField("Qualité du travail fourni Commentaire", blank=False, null=False, default="")
  security = models.IntegerField("Respect de la sécurité et de la propreté du chantier", blank=False, null=False, default=1)
  securityComment = models.TextField("Respect de la sécurité et de la propreté du chantier Commentaire", blank=False, null=False, default="")
  organisation = models.IntegerField("Organisation fourni", blank=False, null=False, default=1)
  organisationComment = models.TextField("Organisation Commentaire", blank=False, null=False, default="")

  contract = models.IntegerField("Image du contrat", blank=False, null=True, default=None)
  manyToManyObject = ["DetailedPost", "File", "Candidate", "DatePost", "Supervision"]

  class Meta:
    verbose_name = "Post"

  @classmethod
  def listFields(cls):
      superList = super().listFields()
      for fieldName in ["signedByCompany", "signedBySubContractor", "contract", "Supervision", "subContractorContact", "subContractorName", "quality", "qualityComment", "security", "securityComment", "organisation", "organisationComment"]:
        index = superList.index(fieldName)
        del superList[index]
      return superList

  @classmethod
  def filter(cls, user):
    listMission = {candidate.Mission.id for candidate in Candidate.objects.all() if candidate.Mission != None}
    return [post for post in Post.objects.all() if not post.id in listMission]

class Mission(Post):
  class Meta:
    proxy = True
    verbose_name = "Mission"

  @classmethod
  def listFields(cls):
      superList = [field.name.replace("Internal", "") for field in cls._meta.fields][1:] + cls.manyToManyObject
      for fieldName in ["Candidate"]: #"Company", 
        index = superList.index(fieldName)
        del superList[index]
      return superList

  @classmethod
  def listIndices(cls):
    parentList = super().listIndices()
    listFields = cls.listFields()
    index = listFields.index("contract")
    parentList.append(index)
    parentList.sort()
    return parentList

  def computeValues(self, listFields, user, dictFormat=False):
    listV = super().computeValues(listFields, user, dictFormat)
    cd = [candidate for candidate in Candidate.objects.filter(Mission=self) if candidate.isChoosen][0]
    return listV + [cd.Company.id]

  @classmethod
  def filter(cls, user):
    userProfile = UserProfile.objects.get(userNameInternal=user)
    return [candidate.Mission for candidate in Candidate.objects.all() if candidate.Mission != None]


  # @classmethod
  # def filter(cls, user):
  #   userProfile = UserProfile.objects.get(userNameInternal=user)
  #   jobList = [jobForCompany.Job for jobForCompany in JobForCompany.objects.filter(Company = userProfile.Company)]
  #   if userProfile.Company.allQualifications:
  #     return [candidate.Mission for candidate in Candidate.objects.all() if candidate.Mission != None]
  #   else:
  #     return [candidate.Mission for candidate in Candidate.objects.all() if candidate.Mission != None and (candidate.Company == userProfile.Company or candidate.Mission.Job in jobList)]

class DatePost(CommonModel):
  Post = models.ForeignKey(Post, verbose_name='Annonce associée', related_name='PostDate', on_delete=models.CASCADE, null=True, default=None)
  Mission = models.ForeignKey(Mission, verbose_name='Mission associée', related_name='MissionDate', on_delete=models.CASCADE, null=True, default=None)
  date = models.DateField(verbose_name="Date du chantier", null=False, default=timezone.now)

  class Meta:
    unique_together = ('Post', 'Mission', 'date')
    verbose_name = "DatePost"

  @classmethod
  def listFields(cls):
    superList= super().listFields()
    for fieldName in ["Post", "Mission"]: #"Company", 
        index = superList.index(fieldName)
        del superList[index]
    return superList


class Candidate(CommonModel):
  Post = models.ForeignKey(Post, verbose_name='Annonce associée', on_delete=models.CASCADE, null=True, default=None)
  Mission = models.ForeignKey(Mission, verbose_name='Mission associée', related_name='selectedMission', on_delete=models.CASCADE, null=True, default=None)
  Company = models.ForeignKey(Company, verbose_name='Sous-Traitant', related_name='selecteCompany', on_delete=models.PROTECT, null=True, default=None)
  contact = models.CharField("Le nom du contact", max_length=128, null=False, default="")
  isChoosen = models.BooleanField("Sous traitant selectionné", null=True, default=None)
  date = models.DateField(verbose_name="Date de candidature ou date d'acceptation", null=False, default=timezone.now)
  amount = models.FloatField("Prix unitaire", null=False, default=0.0)
  unitOfTime = models.CharField("Unité de temps", max_length=128, null=True, default="Prix Journalier")

  class Meta:
    unique_together = ('Post', 'Mission', 'Company')
    verbose_name = "Candidate"

  @classmethod
  def listFields(cls):
      superList = super().listFields()
      for fieldName in ["Post", "Mission"]:
        index = superList.index(fieldName)
        del superList[index]
      return superList

class DetailedPost(CommonModel):
  Post = models.ForeignKey(Post, related_name='Post', verbose_name='Annonce associée', on_delete=models.PROTECT, null=True, default=None)
  Mission = models.ForeignKey(Mission, related_name='Mission', verbose_name='Mission associée', on_delete=models.PROTECT, null=True, default=None)
  content = models.CharField("Détail de la prescription", max_length=256, null=True, default=None)
  date = models.DateField(verbose_name="Date de la tâche", null=True, default=None)
  validated = models.BooleanField("Validation de la tache", null=False, default=False)
  refused = models.BooleanField("Refus de validation de la tache", null=False, default=False)
  manyToManyObject = ["Supervision"]

  class Meta:
    verbose_name = "DetailedPost"


  @classmethod
  def listFields(cls):
      superList = super().listFields()
      for fieldName in ["Post", "Mission"]:
        index = superList.index(fieldName)
        del superList[index]
      return superList

class Supervision(CommonModel):
  Mission = models.ForeignKey(Mission, verbose_name='Mission associée', on_delete=models.PROTECT, null=True, default=None)
  DetailedPost = models.ForeignKey(DetailedPost, verbose_name='Tâche associée', on_delete=models.PROTECT, null=True, default=None)
  SupervisionAssociated = models.ForeignKey('self', verbose_name='Supervision associée', related_name='associatedSupervision', on_delete=models.PROTECT, null=True, default=None)
  # superVisionId = models.IntegerField("id de la supervision dans le cas d'une réponse", blank=False, null=False, default=-1)
  author = models.CharField("Nom de l'auteur du message", max_length=256, null=True, default=None)
  date = models.DateField(verbose_name="Date du suivi", null=False, default=timezone.now)
  comment = models.CharField("Commentaire sur le suivi", max_length=4906, null=True, default=None)
  manyToManyObject = ["File", "Supervision"]

  class Meta:
    verbose_name = "Supervision"

  @classmethod
  def listFields(cls):
      superList = super().listFields()
      for fieldName in ["Mission", "DetailedPost", "SupervisionAssociated"]:
        index = superList.index(fieldName)
        del superList[index]
      return superList


class File(CommonModel):
  nature = models.CharField('nature du fichier', max_length=128, null=False, default=False, blank=False)
  name = models.CharField('Nom du fichier pour le front', max_length=128, null=False, default=False, blank=False)
  path = models.CharField('path', max_length=256, null=False, default=False, blank=False)
  ext = models.CharField('extension', max_length=8, null=False, default=False, blank=False)
  Company = models.ForeignKey(Company, on_delete=models.PROTECT, null=True, default=None)
  expirationDate = models.DateField(verbose_name="Date de péremption", null=True, default=None)
  timestamp = models.FloatField(verbose_name="Timestamp de mise à jour", null=False, default=datetime.datetime.now().timestamp())
  Post = models.ForeignKey(Post, verbose_name="Annonce associée", related_name='selectPost', on_delete=models.PROTECT, null=True, default=None)
  Mission = models.ForeignKey(Mission, verbose_name="Mission associée", related_name='selectMission', on_delete=models.PROTECT, null=True, default=None)
  Supervision = models.ForeignKey(Supervision, verbose_name="Suivi associé", on_delete=models.PROTECT, null=True, default=None)
  dictPath = {"userImage":"./files/avatars/", "labels":"./files/labels/", "admin":"./files/admin/", "post":"./files/posts/", "supervision":"./files/supervisions/", "contract":"./files/contracts/"}
  authorizedExtention = ["png", "PNG", "jpg", "JPG", "jpeg", "JPEG", "svg", "SVG", "pdf", "HEIC", "heic"]

  class Meta:
    unique_together = ('nature', 'name', 'Company', "Post", "Mission", "Supervision")
    verbose_name = "File"

  @classmethod
  def listFields(cls):
    superList = super().listFields()
    for fieldName in ["path", "Company", "Post", "Mission", "Supervision"]:
      index = superList.index(fieldName)
      del superList[index]
    superList.append("content")
    return superList

  def getAttr(self, fieldName, answer=False):
    if fieldName == "file":
      if self.ext == "pdf":
        return self.encodedStringListForPdf()
      if self.ext.lower() == "heic":
        return self.decodeHeic()
      if self.ext.lower() == "svg":
        return self.decodeSvg()
      return self.readFile(self.path)
    return getattr(self, fieldName, answer)

  def readFile(self, path):
    with open(path, "rb") as fileData:
        encoded_string = base64.b64encode(fileData.read())
        return encoded_string.decode("utf-8")


  def encodedStringListForPdf(self):
    path = self.path.replace(".pdf", "/")
    if not os.path.isdir(path):
      os.mkdir(path)
      images = convert_from_path(self.path)
      for index in range(len(images)):
        # Save pages as images in the pdf
        images[index].save(f'{path}page_{str(index)}.jpg', 'JPEG')
    listFiles, listEncode  = [os.path.join(path, file) for file in os.listdir(path)], []
    for file in listFiles:
      with open(file, "rb") as fileData:
        listEncode.append(base64.b64encode(fileData.read()))
    return [encodedString.decode("utf-8") for encodedString in listEncode]

  def decodeHeic(self):
    equivJpg = self.path.replace(f"{self.ext}", "jpg")
    if not os.path.exists(equivJpg):
      with open(self.path, "rb") as fileData:
        bytesIo = fileData.read()
        imageType = whatimage.identify_image(bytesIo)
        if imageType in ['heic', 'avif']:
          image = pyheif.read_heif(bytesIo)
          picture = Image.frombytes(mode=image.mode, size=image.size, data=image.data)
          picture.save(equivJpg, format="jpeg")
    return self.readFile(equivJpg)

  def decodeSvg(self):
    equivJpg = self.path.replace(f"{self.ext}", "png")
    if not os.path.exists(equivJpg):
      with open(self.path, "rb") as fileData:
        bytesIo = fileData.read()
        svg2png(bytestring=bytesIo, write_to=equivJpg)
    return self.readFile(equivJpg)

  @classmethod
  def findAvatar(cls, user):
    userProfile = UserProfile.objects.get(userNameInternal=user)
    file = cls.objects.filter(nature="userImage", Company=userProfile.Company)
    if file:
      return file[0].getAttr("file")
    return {}

  @classmethod
  def createFile(cls, nature, name, ext, user, expirationDate = None, post=None, mission=None, detailedPost=None, supervision=None):
    print("createFile name", name)
    userProfile = UserProfile.objects.get(userNameInternal=user)
    objectFile, mission = None, None
    if nature == "userImage":
      path = cls.dictPath[nature] + userProfile.Company.name + '_' + str(userProfile.Company.id) + '.' + ext
    if nature in ["labels", "admin"]:
      path = cls.dictPath[nature] + name + '_' + str(userProfile.Company.id) + '.' + ext
    if nature == "post":
      path = cls.dictPath[nature] + name + '_' + str(post.id) + '.' + ext
    if nature == "supervision":
      endName = '_' + str(mission.id) if mission else '_N'
      endName += '_' + str(detailedPost.id) if detailedPost else '_N'
      endName += '_' + str(supervision.id) if supervision else '_N'
      name +=  endName
      print("endName", endName, name)
      path = cls.dictPath[nature] + name + '.' + ext
    if nature == "contract":
      mission = post
      post = None
      path = cls.dictPath[nature] + name + '_' + str(mission.id) + '.' + ext
    company = userProfile.Company if not post and not supervision else None
    objectFile = File.objects.filter(nature=nature, name=name, Company=company, Post=post, Mission=mission, Supervision=supervision)
    if objectFile:
      objectFile = objectFile[0]
      oldPath = objectFile.path
      if os.path.exists(oldPath):
        os.remove(oldPath)
      objectFile.path = path
      objectFile.timestamp = datetime.datetime.now().timestamp()
      objectFile.ext = ext
      if expirationDate:
        objectFile.expirationDate = expirationDate
      objectFile.save()
    else:
      objectFile = cls.objects.create(nature=nature, name=name, path=path, ext=ext, Company=company, expirationDate=expirationDate, Post=post, Mission=mission, Supervision=supervision)
    return objectFile

# class FilesPost(CommonModel):
#   Post = models.ForeignKey(Post, verbose_name="Annonce associée", on_delete=models.PROTECT, blank=False, default=None)

# @classmethod
#   def listFields(cls):
#     superList = super().listFields()
#     for fieldName in ["Post"]:
#       index = superList.index(fieldName)
#       del superList[index]
#     superList.append("content")
#     return superList
  

    



