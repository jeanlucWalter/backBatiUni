from ..models import *
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password, make_password
from django.apps import apps
from operator import attrgetter
import sys
import os

from dotenv import load_dotenv

load_dotenv()
if os.getenv('PATH_MIDDLE'):
  sys.path.append(os.getenv('PATH_MIDDLE'))
  from profileScraping import searchUnitesLegalesByDenomination

import json

class DataAccessor():
  loadTables = {"user":[UserProfile, Company, JobForCompany, LabelForCompany], "general":[Job, Role, Label]}
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
    cls.__registerAction(data, message)
    if message:
      return {"register":"Warning", "messages":message}
    return {"register":"OK"}

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
    return message

  @classmethod
  def __registerAction(cls, data, message):
    company = Company.objects.filter(name=data['company'])
    if not company:
      if os.getenv('PATH_MIDDLE'):
        searchSiren = searchUnitesLegalesByDenomination(data['company'])
        if searchSiren["status"] == "OK":
          print('siren')
          company = Company.objects.create(name=data['company'], siret=searchSiren["data"]["siren"])
        else:
          print('no siren')
          message = {"searchSiren":"did not work"}
          company = Company.objects.create(name=data['company'])
      else:
        company = Company.objects.create(name=data['company'])
    else:
      company[0]
    user = User.objects.filter(username=data['email'])
    if user:
      message["email"] = "L'email est déjà utilisé dans la base de données."
    if message:
      print("message", message)
    user = User.objects.create_user(username=data['email'], email=data['email'], password=data['password'])
    role = Role.objects.get(id=data['role'])
    proposer = None
    if data['proposer'] and User.objects.get(id=data['proposer']):
      proposer = User.objects.get(id=data['proposer'])
    userProfile = UserProfile.objects.create(userNameInternal=user, company=company, firstName=data['firstname'], lastName=data['lastname'], proposer=proposer, role=role)
    for idJob in data['jobs']:
      job = Job.objects.get(id=idJob)
      jobCompany = JobForCompany.objects.filter(job=job, company=company)
      if not jobCompany:
        JobForCompany.objects.create(job=job, company=company, number=1)
    userProfile.save()
    return message


  @classmethod
  def dataPost(cls, jsonString, currentUser):
    data = json.loads(jsonString)
    print("dataPost", data)
    if "action" in data:
      if data["action"] == "modifyPwd": return cls.__modifyPwd(data, currentUser)
      if data["action"] == "modifyUser": return cls.__updateUserInfo(data, currentUser)
      return {"dataPost":"Error", "messages":f"unknown action in post {data['action']}"}
    return {"dataPost":"Error", "messages":"no action in post"}

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
    if message:
      return {"modifyUser":"Error", "messages":message, "valueModified": valueModified}
    return {"modifyUser":"OK", "valueModified": valueModified}


  @classmethod
  def __setValues(cls, modelName, dictValue, user, message, valueModified):
    listModelName = [value.lower() for value in map(attrgetter('__name__'), apps.get_models())]
    if modelName in ["JobForCompany", "LabelForCompany"]:
        cls.__setValuesLabelJob(modelName, dictValue, valueModified)
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
  def __setValuesLabelJob(cls, modelName, dictValue, valueModified):
    modelValue = apps.get_model('backBatiUni', modelName)
    modelInside = Job if modelName == "JobForCompany" else Label
    company = None
    for listValue in dictValue:
      objectInside = modelInside.objects.get(id=listValue[0])
      company = Company.objects.get(id=listValue[2])
      objectLabelJob = modelValue.objects.filter(job=objectInside, company=company) if modelName == "JobForCompany" else modelValue.objects.filter(label=objectInside, company=company)
      if objectLabelJob:
        objectLabelJob = objectLabelJob[0]
        if modelName == "JobForCompany" and objectLabelJob.number != listValue[1]:
          objectLabelJob.number = listValue[1]
          objectLabelJob.save()
          if not "JobForCompany" in valueModified:
            valueModified["JobForCompany"] = []
          valueModified["JobForCompany"].append([objectLabelJob.job.id, objectLabelJob.number, objectLabelJob.company.id])
      elif modelName == "JobForCompany":
        objectLabelJob = modelValue.objects.create(job=objectInside, number=listValue[1], company=company)
        if not "JobForCompany" in valueModified:
          valueModified["JobForCompany"] = []
        valueModified["JobForCompany"].append([objectLabelJob.job.id, objectLabelJob.number, objectLabelJob.company.id])
    
    
    


