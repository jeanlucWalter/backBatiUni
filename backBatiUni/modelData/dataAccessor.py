from ..models import *
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password, make_password
import json

class DataAccessor():
  tablesInitial = [Job, Role, Label, UserProfile, Company]

  @classmethod
  def getUserData(cls, user):
    dictAnswer = {}
    for table in cls.tablesInitial:
      dictAnswer.update(table.dumpStructure(user))
    with open("./backBatiUni/modelData/data.json", 'w') as jsonFile:
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
    company = Company.objects.create(name=data['company']) if not company else company[0]
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
      print("datapost", data)
      if data["action"] == "modifyPwd": return cls.__modifyPwd(data, currentUser)
    return {"dataPost":"Error", "messages":"no action in post"}

  @classmethod
  def __modifyPwd(cls, data, currentUser):
    if data['oldPwd'] == data['newPwd']:
      return {"modifyPwd":"Warning", "messages":{"oldPwd", "L'ancien et le nouveau mot de passe sont identiques"}}
    currentUser.set_password(data['newPwd'])
    currentUser.save()
    return {"modifyPwd":"OK"}

  
    
    
    


