from ..models import *
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password, make_password
from django.apps import apps
import sys
sys.path.append("../../middle/temp/")
# sys.path.append("../../middle/")
from profileScraping import searchUnitesLegalesByDenomination

import json

class DataAccessor():
  loadTables = {"user":[UserProfile, Company], "general":[Job, Role, Label]}
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
      searchSiren = searchUnitesLegalesByDenomination(data['company'])
      print("searchSiren", searchSiren, searchSiren["status"] == "ok")
      if searchSiren["status"] == "ok":
        print("ok")
        company = Company.objects.create(name=data['company'], siret=searchSiren["data"]["siren"])
      else:
        message = {"searchSiren":"did not work"}
        company = Company.objects.create(name=data['company'])
    else:
      company[0]
    user = User.objects.filter(username=data['email'])
    if user:
      message["email"] = "L'email est déjà utilisé dans la base de données."
    if message:
      return message
    user = User.objects.create_user(username=data['email'], email=data['email'], password=data['password'])
    role = Role.objects.get(id=data['role'])
    proposer = None
    if data['proposer'] and User.objects.get(id=data['proposer']):
      proposer = User.objects.get(id=data['proposer'])
    userProfile = UserProfile.objects.create(userInternal=user, company=company, firstName=data['firstname'], lastName=data['lastname'], proposer=proposer, role=role)
    for idJob in data['jobs']:
      job = Job.objects.get(id=idJob)
      userProfile.jobs.add(job)
    userProfile.save()
    return message


  @classmethod
  def dataPost(cls, jsonString, currentUser):
    data = json.loads(jsonString)
    if "action" in data:
      print("datapost", data["action"])
      if data["action"] == "modifyPwd": return cls.__modifyPwd(data, currentUser)
      if data["action"] == "updateUserInfo": return cls.__updateUserInfo(data, currentUser)
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
    message = {}
    for key, dictValue in data.items():
      if key != "action":
        cls.__setValues(key, dictValue, user, message)
    if message:
      return {"updateUserInfo":"Error", "messages":message}
    return {"updateUserInfo":"OK"}


  @classmethod
  def __setValues(cls, key, dictValue, user, message):
    modelName = key.replace("Values", "")
    if modelName == key:
      message[key] = "is not an object"
    else:
      modelValue = apps.get_model('backBatiUni', modelName)
      objectValue = modelValue.objects.get(id=id) if id in dictValue else None
      if not objectValue:
        objectValue = modelValue.filter(user)
        objectValue = objectValue[0] if len(objectValue) == 1 else None
      if objectValue:
        for fieldName, value in dictValue.items():
          messageFlag = True
          if getattr(objectValue, fieldName, "does not exist") != "does not exist":
            if getattr(objectValue, fieldName) != value:
              print("setAttr", fieldName, objectValue.setAttr(fieldName, value))
              messageFlag = False
          else:
            message[fieldName] = "is not an field"
        if messageFlag:
          message[modelName] = "Aucun champ n'a été modifié"
        else:
          objectValue.save()
      else:
        message[modelName] = "can not find associated object"
    

  
    
    
    


