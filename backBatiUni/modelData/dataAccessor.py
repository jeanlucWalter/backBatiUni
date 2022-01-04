from ..models import *
from django.contrib.auth.models import User
import json

class DataAccessor():
  tablesInitial = {"job":Job, "role":Role}

  @classmethod
  def getInitialData(cls):
    dictAnswer = {}
    for tableName, table in cls.tablesInitial.items():
      if len(table.listFields()) > 1:
        dictAnswer[tableName + "Fields"] = table.listFields()
      dictAnswer[tableName + "Values"] = table.dictValues()
    return dictAnswer

  @classmethod  
  def register(cls, jsonString):
    print("string", jsonString)
    data = json.loads(jsonString)
    message = cls.__registerCheck(data)
    if message:
      return {"register":"Warning", "message":message}
    message = cls.__registerAction(data)
    if message:
      return {"register":"Warning", "message":message}
    print("register", data)
    return {"register":"OK"}

  @classmethod
  def __registerCheck(cls, data):
    if not data["firstname"]:
      return "Le prénom est un champ obligatoire."
    if not data["lastname"]:
      return "Le nom est un champ obligatoire."
    if not data["email"]:
      return "L'adresse e-mail est un champ obligatoire."
    if not data["password"]:
      return "Le mot de passe est un champ obligatoire."
    if not data["company"]:
      return "Le nom de l'entreprise est un champ obligatoire."
    return False

  @classmethod
  def __registerAction(cls, data):
    company = Company.objects.filter(name=data['company'])
    company = Company.objects.create(name=data['company']) if not company else company[0]
    user = User.objects.filter(username=data['email'])
    if user:
      return f"L'email est déjà utilisé dans la base de données."
    user = User.objects.create_user(username=data['email'], email=data['email'], password=data['password'])
    role = Role.objects.get(id=data['role'])
    proposer = None
    if data['proposer'] and User.objects.get(id=data['proposer']):
      proposer = User.objects.get(id=data['proposer'])
    userProfile = UserProfile.objects.create(user=user, company=company, firstName=data['firstname'], lastName=data['lastname'], proposer=proposer, role=role)
    for idJob in data['jobs']:
      job = Job.objects.get(id=idJob)
      userProfile.jobs.add(job)
    userProfile.save()
    return False

    
    
    
    


