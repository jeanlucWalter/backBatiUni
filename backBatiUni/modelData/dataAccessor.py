from ..models import *
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password, make_password
from django.apps import apps
from operator import attrgetter
import sys
import os
from datetime import datetime
import base64
from django.core.files.base import ContentFile
from .smtpConnector import SmtpConnector

from dotenv import load_dotenv

load_dotenv()
if os.getenv('PATH_MIDDLE'):
  sys.path.append(os.getenv('PATH_MIDDLE'))
  from profileScraping import searchUnitesLegalesByDenomination

import json

class DataAccessor():
  loadTables = {"user":[UserProfile, Company, JobForCompany, LabelForCompany, Files], "general":[Job, Role, Label]}
  dictTable = {}

  @classmethod
  def getData(cls, profile, user):
    dictAnswer = {}
    for table in cls.loadTables[profile]:
      dictAnswer.update(table.dumpStructure(user))
    with open(f"./backBatiUni/modelData/{profile}Data.json", 'w') as jsonFile:
        json.dump(dictAnswer, jsonFile, indent = 3)
    return dictAnswer

  @classmethod
  def register(cls, jsonString):
    print("register", jsonString)
    data = json.loads(jsonString)
    message = cls.__registerCheck(data, {})
    if message:
      return {"register":"Warning", "messages":message}
    token = SmtpConnector(6004).register(data["firstname"], data["lastname"], data["email"])
    print(token, isinstance(token, str))
    token = token if isinstance(token, str) else "empty token"
    cls.__registerAction(data, token)
    return {"register":"Error", "messages":"token not received"} if token == "empty token" else {"register":"OK"}

  @classmethod
  def __registerCheck(cls, data, message):
    if not data["firstname"]:
      message["firstname"] = "Le prénom est un champ obligatoire."
    if not data["lastname"]:
      message["lastname"] = "Le nom est un champ obligatoire."
    if not data["email"]:
      message["email"] = "L'adresse e-mail est un champ obligatoire."
    if not data["password"]:
      message["password"] = "Le mot de passe est un champ obligatoire."
    if not data["company"]:
      message["company"] = "Le nom de l'entreprise est un champ obligatoire."
    if User.objects.filter(username=data["email"]):
      message["email"] = "Cet email et déjà pris."
    return message

  @classmethod
  def __registerAction(cls, data, token):
    company = Company.objects.filter(name=data['company'])
    if not company:
      if os.getenv('PATH_MIDDLE'):
        searchSiren = searchUnitesLegalesByDenomination(data['company'])
        if searchSiren["status"] == "OK":
          company = Company.objects.create(name=data['company'], siret=searchSiren["data"]["siren"])
        else:
          company = Company.objects.create(name=data['company'])
      else:
        company = Company.objects.create(name=data['company'])
    else:
      company = company[0]
    role = Role.objects.get(id=data['role'])
    proposer = None
    if data['proposer'] and User.objects.get(id=data['proposer']):
      proposer = User.objects.get(id=data['proposer'])
    userProfile = UserProfile.objects.create(Company=company, firstName=data['firstname'], lastName=data['lastname'], proposer=proposer, role=role, token=token, email=data["email"], password=data["password"])
    if 'jobs' in data:
      for idJob in data['jobs']:
        job = Job.objects.get(id=idJob)
        jobCompany = JobForCompany.objects.filter(Job=job, Company=company)
        if not jobCompany:
          JobForCompany.objects.create(Job=job, Company=company, number=1)
    userProfile.save()

  @classmethod
  def dataPost(cls, jsonString, currentUser):
    data = json.loads(jsonString)
    if "action" in data:
      print("dataPost", data["action"])
      if data["action"] == "modifyPwd": return cls.__modifyPwd(data, currentUser)
      if data["action"] == "modifyUser": return cls.__updateUserInfo(data, currentUser)
      if data["action"] == "changeUserImage": return cls.__changeUserImage(data, currentUser)
      if data["action"] == "loadDocument": return cls.__loadDocument(data, currentUser)
      return {"dataPost":"Error", "messages":f"unknown action in post {data['action']}"}
    return {"dataPost":"Error", "messages":"no action in post"}

  # @classmethod
  # def __changeUserImage(cls, request, dictData, currentUser):
  #   print(dictData["imageBase64"])
  #   image = request.data.get('imageBase64')
  #   format, imgstr = image.split(';base64,')
  #   ext = format.split('/')[-1]
  #   if not dictData["name"]:
  #     return {"changeUserImage":"Error", "messages":"field name is empty"}
  #   objectFile = Files.createFile("userImage", dictData["name"], ext, currentUser)
  #   image = ContentFile(base64.b64decode(imgstr), name=objectFile.path + ext)
  #   with open(objectFile.path, "wb") as outfile:
  #       outfile.write(image.file.getbuffer())
  #   print({"changeUserImage":"OK", "file":objectFile.computeValues(objectFile.listFields(), currentUser)})
  #   return {"changeUserImage":"OK", "file":objectFile.computeValues(objectFile.listFields(), currentUser)}

  @classmethod
  def __changeUserImage(cls, dictData, currentUser):
    fileStr = dictData["imageBase64"]
    if not dictData["name"]:
      return {"changeUserImage":"Error", "messages":"field name is empty"}
    objectFile = Files.createFile("userImage", dictData["name"], dictData['ext'], currentUser)
    file = ContentFile(base64.b64decode(fileStr), name=objectFile.path + dictData['ext'])
    with open(objectFile.path, "wb") as outfile:
        outfile.write(file.file.getbuffer())
    return {"changeUserImage":"OK", objectFile.id:objectFile.computeValues(objectFile.listFields(), currentUser)[1]}

  @classmethod
  def loadImage(cls, id, currentUser):
    file = Files.objects.get(id=id)
    content = file.getAttr("file")
    listFields = file.listFields()
    fileList = file.computeValues(listFields, currentUser)
    indexContent = listFields.index("content")
    fileList[indexContent] = content
    return {"loadImage":"OK", id:fileList}

  @classmethod
  def __loadDocument(cls, request, data, currentUser):
    print(list(data.keys()))
    return {"loadDocument":"work in progress"}

  @classmethod
  def __modifyPwd(cls, data, currentUser):
    if data['oldPwd'] == data['newPwd']:
      return {"modifyPwd":"Warning", "messages":{"oldPwd", "L'ancien et le nouveau mot de passe sont identiques"}}
    currentUser.set_password(data['newPwd'])
    currentUser.save()
    return {"modifyPwd":"OK"}

  @classmethod
  def __updateUserInfo(cls, data, user):
    message, valueModified = {}, {}
    for key, dictValue in data.items():
      if key != "action":
        cls.__setValues(key, dictValue, user, message, valueModified)
    if message and valueModified:
      keys = []
      for key, value in message.items():
        if value == "Aucun champ n'a été modifié":
          keys.append(key)
      for key in keys:
        del message[key]
    for target, move in {"Company":"JobForCompany", "Company":"LabelForCompany", "Userprofile":"Company"}.items():
      if move in valueModified:
        if valueModified[move]:
          if not target in valueModified:
            valueModified[target] = {}
          valueModified[target][move] = valueModified[move]
        del valueModified[move]
    if message:
      return {"modifyUser":"Error", "messages":message, "valueModified": valueModified}
    return {"modifyUser":"OK", "valueModified": valueModified}


  @classmethod
  def __setValues(cls, modelName, dictValue, user, message, valueModified):
    listModelName = [value.lower() for value in map(attrgetter('__name__'), apps.get_models())]
    if modelName in ["JobForCompany", "LabelForCompany"]:
        cls.__setValuesLabelJob(modelName, dictValue, valueModified, user)
    elif modelName.lower() in listModelName:
      modelValue = apps.get_model('backBatiUni', modelName)
      objectValue = modelValue.objects.get(id=id) if id in dictValue else None
      if not objectValue:
        objectValue = modelValue.filter(user)
        objectValue = objectValue[0] if len(objectValue) == 1 else None
      if objectValue:
        for fieldName, value in dictValue.items():
          if fieldName != "id":
            messageFlag = True
            if objectValue.getAttr(fieldName, "does not exist") != "does not exist":
              if objectValue.getAttr(fieldName) != value:
                objectValue.setAttr(fieldName, value)
                if not modelName in valueModified:
                  valueModified[modelName] = {}
                valueModified[modelName][fieldName] = value
                messageFlag = False
            else:
              message[fieldName] = "is not an field"
        if messageFlag:
          if not valueModified:
            message[modelName] = "Aucun champ n'a été modifié"
        else:
          objectValue.save()
    else:
      message[modelName] = "can not find associated object"

  @classmethod
  def __setValuesLabelJob(cls, modelName, dictValue, valueModified, user):
    if modelName == "JobForCompany":
      cls.__setValuesJob(dictValue, valueModified, user)
    else:
      cls.__setValuesLabel(dictValue, valueModified, user)


  @classmethod
  def __setValuesJob(cls, dictValue, valueModified, user):
    JobForCompany.objects.all().delete()
    for listValue in dictValue:
      if listValue[1]:
        job = Job.objects.get(id=listValue[0])
        company = UserProfile.objects.get(userNameInternal=user).Company
        jobForCompany = JobForCompany.objects.create(Job=job, number=listValue[1], Company=company)
        if not "JobForCompany" in valueModified:
          valueModified["JobForCompany"] = {}
        valueModified["JobForCompany"][jobForCompany.id] = [jobForCompany.Job.id, jobForCompany.number]

  @classmethod
  def __setValuesLabel(cls, dictValue, valueModified, user):
    LabelForCompany.objects.all().delete()
    for listValue in dictValue:
      label = Label.objects.get(id=listValue[0])
      date = datetime.strptime(listValue[1], "%Y/%m/%d")
      company = UserProfile.objects.get(userNameInternal=user).Company
      labelForCompany = LabelForCompany.objects.create(Label=label, date=date, Company=company)
      if not "LabelForCompany" in valueModified:
        valueModified["LabelForCompany"] = {}
      valueModified["LabelForCompany"][labelForCompany.id] = [labelForCompany.Label.id, labelForCompany.date.strftime("%Y/%m/%d")]