from asyncio import subprocess
from asyncio.unix_events import _UnixSelectorEventLoop
from re import sub
from ..models import *
from django.contrib.auth.models import User, UserManager
from django.contrib.auth.hashers import check_password, make_password
from django.utils import timezone
from django.apps import apps
from operator import attrgetter
import sys
import os
import shutil
from datetime import datetime, timedelta
import base64
from django.core.files.base import ContentFile
from ..smtpConnector import SmtpConnector
import json

from dotenv import load_dotenv

load_dotenv()
if os.getenv('PATH_MIDDLE'):
  sys.path.append(os.getenv('PATH_MIDDLE'))
  from profileScraping import getEnterpriseDataFrom
  from geocoding import getCoordinatesFrom # argument str address


class DataAccessor():
  loadTables = {"user":[UserProfile, Company, JobForCompany, LabelForCompany, File, Post, Candidate, DetailedPost, DatePost, Mission, Disponibility, Supervision], "general":[Job, Role, Label]}
  dictTable = {}
  portSmtp = os.getenv('PORT_SMTP')

  @classmethod
  def getData(cls, profile, user):
    if not UserProfile.objects.filter(userNameInternal=user) and profile == "user":
      {"register":"Error", "messages":"currentUser does not exist"} 
    dictAnswer = {"currentUser":UserProfile.objects.get(userNameInternal=user).id} if profile == "user" else {}
    for table in cls.loadTables[profile]:
      dictAnswer.update(table.dumpStructure(user))
    with open(f"./backBatiUni/modelData/{profile}Data.json", 'w') as jsonFile:
      json.dump(dictAnswer, jsonFile, indent = 3)
    return dictAnswer

  @classmethod
  def register(cls, data):
    message = cls.__registerCheck(data, {})
    if message:
      return {"register":"Warning", "messages":message}
    token = SmtpConnector(cls.portSmtp).register(data["firstname"], data["lastname"], data["email"])
    if token != "token not received" or data["email"] == "walter.jeanluc@gmail.com":
      cls.__registerAction(data, token)
      return {"register":"OK"}
    cls.__registerAction(data, "empty token")
    return {"register":"Error", "messages":"token not received"} 

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
    userProfile = UserProfile.objects.filter(email=data["email"])
    if userProfile or User.objects.filter(username=data["email"]):
      userProfile = userProfile[0]
      if userProfile.password:
        userProfile.delete()
      else:
        message["email"] = "Cet email et déjà utilisé."
    companyData = data['company']
    company = Company.objects.filter(name=companyData['name'])
    if company:
      message["company"] = "Le nom de l'entreprise est déjà utilisé."
    return message

  @classmethod
  def __registerAction(cls, data, token):
    print("registerAction", data)
    companyData = data['company']
    company = Company.objects.create(name=companyData['name'], address=companyData['address'], activity=companyData['activity'], ntva=companyData['ntva'], siret=companyData['siret'])
    cls.__getGeoCoordinates(company)
    company.Role = Role.objects.get(id=data['Role'])
    company.save()
    proposer = None
    if data['proposer'] and User.objects.get(id=data['proposer']):
      proposer = User.objects.get(id=data['proposer'])
    userProfile = UserProfile.objects.create(Company=company, firstName=data['firstname'], lastName=data['lastname'], proposer=proposer, token=token, email=data["email"], password=data["password"])
    if 'jobs' in data:
      for idJob in data['jobs']:
        job = Job.objects.get(id=idJob)
        jobCompany = JobForCompany.objects.filter(Job=job, Company=company)
        if not jobCompany:
          JobForCompany.objects.create(Job=job, Company=company, number=1)
    userProfile.save()

  @classmethod
  def registerConfirm(cls, token):
    userProfile = UserProfile.objects.filter(token=token)
    print("registerConfirm token", token, userProfile)
    if userProfile:
      userProfile = userProfile[0]
      user = User.objects.create(username=userProfile.email, email=userProfile.email)
      user.set_password(userProfile.password)
      user.save()
      userProfile.userNameInternal = user
      userProfile.token = None
      userProfile.password = None
      userProfile.save()
      return {"registerConfirm":"OK"}
    return {"registerConfirm":"Error", "messages":"wrong token or email"}


  @classmethod
  def dataPost(cls, jsonString, currentUser):
    data = json.loads(jsonString)
    if "action" in data:
      if data["action"] == "modifyPwd": return cls.__modifyPwd(data, currentUser)
      elif data["action"] == "modifyUser": return cls.__updateUserInfo(data, currentUser)
      elif data["action"] == "changeUserImage": return cls.__changeUserImage(data, currentUser)
      elif data["action"] == "uploadPost": return cls.__uploadPost(data, currentUser)
      elif data["action"] == "modifyPost": return cls.__modifyPost(data, currentUser)
      elif data["action"] == "createDetailedPost": return cls.__createDetailedPost(data, currentUser)
      elif data["action"] == "modifyDetailedPost": return cls.__modifyDetailedPost(data, currentUser)
      elif data["action"] == "deleteDetailedPost": return cls.__deleteDetailedPost(data, currentUser)
      elif data["action"] == "createSupervision": return cls.__createSupervision(data, currentUser)
      elif data["action"] == "modifySupervision": return cls.__modifySupervision(data, currentUser)
      elif data["action"] == "deleteSupervision": return cls.__deleteSupervision(data, currentUser)
      elif data["action"] == "uploadFile": return cls.__uploadFile(data, currentUser)
      elif data["action"] == "modifyDisponibility": return cls.__modifyDisponibility(data["disponibility"], currentUser)
      elif data["action"] == "uploadSupervision": return cls.uploadSupervision(data["detailedPost"], data["comment"], currentUser)
      elif data["action"] == "uploadImageSupervision": return cls.__uploadImageSupervision(data, currentUser)
      elif data["action"] == "closeMission": return cls.__closeMission(data, currentUser)
      return {"dataPost":"Error", "messages":f"unknown action in post {data['action']}"}
    return {"dataPost":"Error", "messages":"no action in post"}

  @classmethod
  def __changeUserImage(cls, dictData, currentUser):
    fileStr = dictData["imageBase64"]
    if not dictData["name"]:
      return {"changeUserImage":"Error", "messages":"field name is empty"}
    objectFile = File.createFile("userImage", dictData["name"], dictData['ext'], currentUser)
    file = ContentFile(base64.b64decode(fileStr), name=objectFile.path + dictData['ext'])
    with open(objectFile.path, "wb") as outfile:
        outfile.write(file.file.getbuffer())
    return {"changeUserImage":"OK", objectFile.id:objectFile.computeValues(objectFile.listFields(), currentUser, True)}

  @classmethod
  def __uploadPost(cls, dictData, currentUser):
    kwargs, listObject = cls.__createPostKwargs(dictData, currentUser)
    if "uploadPost" in kwargs and kwargs["uploadPost"] == "Error":
      return kwargs
    objectPost = Post.objects.create(**kwargs)
    cls.__getGeoCoordinates(objectPost)
    if listObject:
      for subObject in listObject:
        subObject.Post = objectPost
        subObject.save()
    return {"uploadPost":"OK", objectPost.id:objectPost.computeValues(objectPost.listFields(), currentUser, True)}

  @classmethod
  def __getGeoCoordinates(cls, objectPost):
    if os.getenv('PATH_MIDDLE'):
      dictCoord = getCoordinatesFrom(objectPost.address)
      if dictCoord["getCoordinatesFrom"] == "OK":
        objectPost.address = dictCoord["address"]
        objectPost.latitude = dictCoord["latitude"]
        objectPost.longitude = dictCoord["longitude"]
        objectPost.save()
        return
    objectPost.latitude = 0.0
    objectPost.longitude = 0.0

  @classmethod
  def __createPostKwargs(cls, dictData, currentUser):
    userProfile = UserProfile.objects.get(userNameInternal=currentUser)
    kwargs, listFields, listObject = {"Company":userProfile.Company, "startDate":None, "endDate":None, "subContractorName":None}, Post.listFields(), []
    for fieldName, value in dictData.items():
      fieldObject = None
      try:
        fieldObject = Post._meta.get_field(fieldName)
      except:
        fieldObject = None
      if fieldName in listFields:
        if fieldObject and isinstance(fieldObject, models.ForeignKey):
          foreign = Post._meta.get_field(fieldName).remote_field.model
          objectForeign = foreign.objects.filter(id=value)
          if objectForeign:
            kwargs[fieldName]=objectForeign[0]
          else:
            return {"uploadPost":"Error", "messages":{fieldName:"is not documented"}}, False
        if fieldObject and isinstance(fieldObject, models.DateField):
          date = datetime.strptime(dictData[fieldName], "%Y-%m-%d") if dictData[fieldName] else None
          kwargs[fieldName]=date
        if fieldObject and isinstance(fieldObject, models.IntegerField):
          kwargs[fieldName]=int(dictData[fieldName]) if dictData[fieldName] else 0
        if fieldObject and isinstance(fieldObject, models.FloatField):
          kwargs[fieldName]=float(dictData[fieldName]) if dictData[fieldName] else 0.0
        if fieldObject and isinstance(fieldObject, models.BooleanField) or isinstance(fieldObject, models.CharField) :
          kwargs[fieldName]= dictData[fieldName]
        if fieldName in Post.manyToManyObject:
          modelObject = apps.get_model(app_label='backBatiUni', model_name=fieldName)
          for content in value:
            if fieldName == "DatePost":
              cls.__computeStartEndDate(kwargs, content)
              listObject.append(modelObject.objects.create(date=content))
            else:
              listObject.append(modelObject.objects.create(content=content))
    kwargs["contactName"] = f"{userProfile.firstName} {userProfile.lastName}"
    return kwargs, listObject


  @classmethod
  def __computeStartEndDate(cls, limitDate, strDate):
    date = datetime.strptime(strDate, "%Y-%m-%d")
    if not limitDate["startDate"] or limitDate["startDate"] > date:
      limitDate["startDate"] = date
    if not limitDate["endDate"] or limitDate["endDate"] < date:
      limitDate["endDate"] = date
    


  @classmethod
  def __modifyPost(cls, dictData, currentUser):
    post = Post.objects.filter(id=dictData["id"])
    if post:
      post = post[0]
      DatePost.objects.filter(Post=post).delete()
      kwargs, listObject = cls.__createPostKwargs(dictData, currentUser)
      for key, value in kwargs.items():
        if getattr(post, key, "empty field") != "empty field" and getattr(post, key, "empty field") != value:
          setattr(post, key, value)
          if key == "address":
            cls.__getGeoCoordinates(post)
      post.save()
      if listObject:
        for subObject in listObject:
          subObject.Post = post
          subObject.save()
      if dictData["DetailedPost"]:
        DetailedPost.objects.filter(Post=post).delete()
        for content in dictData["DetailedPost"]:
          DetailedPost.objects.create(Post=post, content=content)
      return {"modifyPost":"OK", post.id:post.computeValues(post.listFields(), currentUser, True)}
    return {"modifyPost":"Error", "messages":f"{dictData['id']} is not a Post id"}

  @classmethod
  def applyPost(cls, postId, amount, unitOfTime, currentUser):
    userProfile = UserProfile.objects.get(userNameInternal=currentUser)
    subContractor = userProfile.Company
    contact = userProfile.firstName + " " + userProfile.lastName
    post = Post.objects.get(id=postId)
    company = post.Company
    if subContractor == company:
      return {"applyPost":"Warning", "messages":f"Le sous-traitant {subContractor.name} ne peut pas être l'entreprise commanditaire."}
    if subContractor.Role.id == 1:
      return {"applyPost":"Warning", "messages":f"La société {subContractor.name} n'est pas sous-traitante."}
    tce = Job.objects.get(name= "TCE (Tout Corps d'Etat)")
    if not(post.Job in subContractor.jobs or subContractor.allQualifications):
      return {"applyPost":"Warning", "messages":f"Le métier {post.Job.name} n'est pas une compétence du sous-traitant {subContractor.name}."}
    exists = Candidate.objects.filter(Post=post, Company=subContractor)
    if exists:
      return {"applyPost":"Warning", "messages":f"Le sous-traitant {subContractor.name} a déjà postulé."}
    candidate = Candidate.objects.create(Post=post, Company=subContractor, amount=amount, contact=contact, unitOfTime=unitOfTime)
    return {"applyPost":"OK", candidate.id:candidate.computeValues(candidate.listFields(), currentUser, True)}

  @classmethod
  def __createDetailedPost(cls, data, currentUser):
    kwargs, post, mission = {"Post":None, "Mission":None, "content":None, "date":None, "validated":False}, None, None
    if "postId" in data:
      post = Post.objects.get(id=data["postId"])
      kwargs["Post"] = post
    if "missionId" in data:
      mission = Mission.objects.get(id=data["missionId"])
      kwargs["Mission"] = mission
    if "content" in data:
      kwargs["content"] = data["content"]
    if "date" in data:
      kwargs["date"] = datetime.strptime(data["date"], "%Y-%m-%d")
    if "validated" in data:
      kwargs["validated"] = data["validated"]
    detailedPost = DetailedPost.objects.create(**kwargs)
    if detailedPost:
      if post:
        return {"createDetailedPost":"OK", post.id:post.computeValues(post.listFields(), currentUser, True)}
      if mission:
        return {"createDetailedPost":"OK", mission.id:mission.computeValues(mission.listFields(), currentUser, True)}
    return {"createDetailedPost":"Warning", "messages":"La tâche n'a pas été créée"}

  @classmethod
  def __modifyDetailedPost(cls, data, currentUser):
    data = data["detailedPost"]
    # return {"modifyDetailedPost":"OK", "d":["a", "b", "c"]}
    detailedPost = DetailedPost.objects.filter(id=data["id"])
    if detailedPost:
      detailedPost = detailedPost[0]
      if "date" in data and data["date"]:
        date = datetime.strptime(data["date"], "%Y-%m-%d")
        dateNowString = detailedPost.date.strftime("%Y-%m-%d") if detailedPost.date else None
        if dateNowString != data["date"] and dateNowString:
          detailedPost = DetailedPost.objects.create(Post=detailedPost.Post, Mission=detailedPost.Mission, content=detailedPost.content, date=date, validated=detailedPost.validated)
          if detailedPost:
            PorM = detailedPost.Post if detailedPost.Post else detailedPost.Mission
            return {"modifyDetailedPost":"OK", PorM.id:PorM.computeValues(PorM.listFields(), currentUser, True)}
        else:
          detailedPost.date = date
      for field in ["content", "validated", "refused"]:
        if field in data:
          setattr(detailedPost, field, data[field])
      detailedPost.save()
      PorM = detailedPost.Post if detailedPost.Post else detailedPost.Mission
      dumpPorM = PorM.computeValues(PorM.listFields(), currentUser, True)
      return {"modifyDetailedPost":"OK", PorM.id:dumpPorM}
    return {"modifyDetailedPost":"Error", "messages":f"No Detailed Post with id {data['detailedPostId']}"}

  @classmethod
  def __deleteDetailedPost(cls, data, currentUser):
    detailedPost = DetailedPost.objects.filter(id=data["detailedPostId"])
    if detailedPost:
      detailedPost = detailedPost[0]
      post, mission = detailedPost.Post, detailedPost.Mission
      Supervision.objects.filter(DetailedPost=detailedPost).delete()
      detailedPost.delete()
      if post:
        return {"deleteDetailedPost":"OK", post.id:post.computeValues(post.listFields(), currentUser, True)}
      if mission:
        return {"deleteDetailedPost":"OK", mission.id:mission.computeValues(mission.listFields(), currentUser, True)}
    return {"deleteDetailedPost":"Error", "messages":f"No Detailed Post with id {data['detailedPostId']}"}

  @classmethod
  def __createSupervision(cls, data, currentUser):
    print("createSupervision", data, currentUser.id)
    userProfile = UserProfile.objects.get(userNameInternal=currentUser)
    author = f'{userProfile.firstName} {userProfile.lastName}'
    kwargs, mission = {"DetailedPost":None, "author":author, "comment":""}, None
    if "missionId" in data and data["missionId"]:
      mission = Mission.objects.get(id=data["missionId"])
      kwargs["Mission"] = mission
    if "detailedPostId" in data and data["detailedPostId"]:
      detailedPost = DetailedPost.objects.get(id=data["detailedPostId"])
      mission = detailedPost.Mission
      kwargs["DetailedPost"] = detailedPost
    if "parentId" in data and data["parentId"]:
      parentSupervision = Supervision.objects.get(id=data["parentId"]) 
      kwargs["parentId"] = parentSupervision
    if "comment" in data:
      kwargs["comment"] = data["comment"]
    if "date" in data and data["date"]:
      kwargs["date"] = datetime.strptime(data["date"], "%Y-%m-%d")
    print('createSupervision kwargs', kwargs)
    supervision = Supervision.objects.create(**kwargs)
    if supervision:
      return {"createSupervision":"OK", mission.id:mission.computeValues(mission.listFields(), currentUser, True)}
      # return {"createSupervision":"OK", supervision.id:supervision.computeValues(supervision.listFields(), currentUser, True)}
    return {"createSupervision":"Warning", "messages":"La supervision n'a pas été créée"}

  @classmethod

  @classmethod
  def __modifySupervision(cls, data, currentUser):
    pass

  @classmethod
  def __deleteSupervision(cls, data, currentUser):
    pass

  @classmethod
  def setFavorite(cls, postId, value, currentUser):
    userProfile = UserProfile.objects.get(userNameInternal=currentUser)
    favorite = FavoritePost.objects.filter(UserProfile=userProfile, postId=postId)
    if favorite and value == "false":
        favorite[0].delete()
    elif value == "true" and not favorite:
      FavoritePost.objects.create(UserProfile=userProfile, postId=postId)
    return {"setFavorite":"OK"}

  @classmethod
  def isViewed(cls, postId, currentUser):
    userProfile = UserProfile.objects.get(userNameInternal=currentUser)
    viewPost = ViewPost.objects.filter(UserProfile=userProfile, postId=postId)
    if not viewPost:
      ViewPost.objects.create(UserProfile=userProfile, postId=postId)
    return {"isViewed":"OK"}

  @classmethod
  def getPost(cls, currentUser):
    return {objectPost.id:objectPost.computeValues(objectPost.listFields(), currentUser, dictFormat=True) for objectPost in Post.objects.all()}

  @classmethod
  def deletePost(cls, id):
    post = Post.objects.filter(id=id)
    if post:
      for detail in DetailedPost.objects.filter(Post=post[0]):
        detail.delete()
      for file in File.objects.filter(Post=post[0]):
        file.delete()
        
      post.delete()
      return {"deletePost":"OK", "id":id}
    return {"deletePost":"Error", "messages":f"{id} does not exist"}

  @classmethod
  def handleCandidateForPost(cls, candidateId, status, currentUser):
    candidate = Candidate.objects.get(id=candidateId)
    if candidate.Mission:
      return {"handleCandidateForPost":"Error", "messages":f"The post of id {candidate.Mission.id} is allready a mission"}
    postId = candidate.Post.id
    status = True if status == "true" else status
    status = False if status == "false" else status
    candidate.isChoosen = status
    if status:
      candidate.Post = None
      candidate.Mission = Mission.objects.get(id=postId)
      candidate.date = timezone.now()
      candidate.save()
      mission = candidate.Mission
      for model in [DetailedPost, File]:
        for modelObject in model.objects.all():
          if modelObject.Post and modelObject.Post.id == postId:
            modelObject.Post = None
            modelObject.Mission = mission
            modelObject.save()
      contractImage = cls.createContract(candidate.Mission, currentUser)
      userProfile = UserProfile.objects.get(userNameInternal=currentUser)
      # candidate.Mission.subContractorContact = userProfile.firstName + " " + userProfile.lastName
      candidate.Mission.subContractorName = candidate.Company.name
      candidate.Mission.subContractorContactn = candidate.contact
      candidate.Mission.contract = contractImage.id
      candidate.Mission.save()
      return {"handleCandidateForPost":"OK", mission.id:mission.computeValues(mission.listFields(), currentUser, dictFormat=True)}
    post = candidate.Post
    return {"handleCandidateForPost":"OK", post.id:post.computeValues(post.listFields(), currentUser, dictFormat=True)}


  @classmethod
  def createContract(cls, mission, user):
    contractImage = File.createFile("contract", "contract", "png", user, post=mission)
    source = "./files/documents/contractUnsigned.png"
    dest = contractImage.path
    shutil.copy2(source, dest)
    return contractImage

  @classmethod
  def signContract(cls, missionId, view, currentUser):
    mission = Mission.objects.get(id=missionId)
    contractImage = File.objects.get(id=mission.contract)
    if view == "PME":
      source = "./files/documents/ContractSignedST_PME.png" if mission.signedBySubContractor else "./files/documents/ContractSignedPME.png"
    else:
      source = "./files/documents/ContractSignedST_PME.png" if mission.signedByCompany else "./files/documents/ContractSignedST.png"
    dest = contractImage.path
    shutil.copy2(source, dest)
    contractImage.timestamp = datetime.now().timestamp()
    contractImage.save()
    if view == "PME" : mission.signedByCompany = True
    else: mission.signedBySubContractor = True
    mission.save()
    return {"signContract":"OK", mission.id:mission.computeValues(mission.listFields(), currentUser, dictFormat=True)}



  @classmethod
  def uploadSupervision(cls, detailedPostId, comment, currentUser):
    detailed = DetailedPost.objects.get(id=detailedPostId)
    userProfile = UserProfile.objects.get(userNameInternal=currentUser)
    if detailed.Post:
      return {"uploadSuperVision":"Error", "messages":"associated Post is not a mission"}
    supervision = Supervision.objects.create(DetailedPost=detailed, UserProfile=userProfile, comment=comment)
    return {"uploadSupervision":"OK", supervision.id:supervision.computeValues(supervision.listFields(), currentUser, dictFormat=True)}

  @classmethod
  def switchDraft(cls, id, currentUser):
    company = UserProfile.objects.get(userNameInternal=currentUser).Company
    post = Post.objects.filter(id=id)
    if post:
      post = post[0]
      if company == post.Company:
        post.draft = not post.draft
        post.save()
        return {"switchDraft":"OK", post.id:post.computeValues(post.listFields(), currentUser, dictFormat=True)}
      return {"switchDraft":"Error", "messages":f"{currentUser.username} does not belongs to {company.name}"}
    return {"switchDraft":"Error", "messages":f"{id} does not exist"}

  @classmethod
  def __closeMission(cls, data, currentUser):
    print("closeMission start data", data)
    print("closeMission start", {mission.id:mission.signedByCompany for mission in Mission.objects.all()})
    mission = Mission.objects.get(id=data["missionId"])
    mission.quality = data["qualityStars"]
    mission.qualityComment = data["qualityComment"]
    mission.security = data["securityStars"]
    mission.securityComment = data["securityComment"]
    mission.organisation = data["organisationStars"]
    mission.organisationComment = data["organisationComment"]
    mission.isClosed = True
    mission.save()
    return {"closeMission":"OK", mission.id:mission.computeValues(mission.listFields(), currentUser, dictFormat=True)}

  @classmethod
  def duplicatePost(cls, id, currentUser):
    company = UserProfile.objects.get(userNameInternal=currentUser).Company
    post = Post.objects.filter(id=id)
    if post:
      post = post[0]
      if company == post.Company:
        kwargs = {field.name:getattr(post, field.name) for field in Post._meta.fields[1:]}
        kwargs["draft"] = True
        duplicate = Post.objects.create(**kwargs)
        for detailPost in DetailedPost.objects.filter(Post=post):
          DetailedPost.objects.create(Post=duplicate, content=detailPost.content)
        for file in File.objects.filter(Post=post):
          kwargs =  {field.name:getattr(file, field.name) for field in File._meta.fields[1:]}
          newName = File.dictPath["post"] + kwargs["name"] + '_' + str(duplicate.id) + '.' + kwargs["ext"]
          shutil.copy(kwargs["path"], newName)
          kwargs["path"] = File.dictPath["post"] + kwargs["name"] + '_' + str(duplicate.id) + '.' + kwargs["ext"]
          newFile= File.objects.create(**kwargs)
          newFile.Post = duplicate
          newFile.save()
        return {"duplicatePost":"OK", duplicate.id:duplicate.computeValues(duplicate.listFields(), currentUser, dictFormat=True)}
      return {"duplicatePost":"Error", "messages":f"{currentUser.username} does not belongs to {company.name}"}
    return {"duplicatePost":"Error", "messages":f"{id} does not exist"}

  @classmethod
  def downloadFile(cls, id, currentUser):
    file = File.objects.get(id=id)
    content = file.getAttr("file")
    listFields = file.listFields()
    fileList = file.computeValues(listFields, currentUser)
    indexContent = listFields.index("content")
    fileList[indexContent] = content
    return {"downloadFile":"OK", id:fileList}

  @classmethod
  def deleteFile(cls, id):
    file = File.objects.filter(id=id)
    if file:
      file = file[0]
      os.remove(file.path)
      file.delete()
      return {"deleteFile":"OK", "id":id}
    return {"deleteFile":"Error", "messages":f"No file width id {id}"}


  @classmethod
  def __uploadFile(cls, data, currentUser):
    if not data['ext'] in File.authorizedExtention:
      return {"uploadFile":"Warning", "messages":f"L'extention {data['ext']} n'est pas traitée"}
    fileStr, message = data["fileBase64"], {}
    for field in ["name", "ext", "nature"]:
      if not data[field]:
        message[field] = f"field {field} is empty"
    if not fileStr:
      message["fileBase64"] = "field fileBase64 is empty"
    if message:
      return {"uploadFile":"Error", "messages":message}
    expirationDate = datetime.strptime(data["expirationDate"], "%Y-%m-%d") if "expirationDate" in data and data["expirationDate"] else None
    post = None
    if "Post" in data:
      post = Post.objects.filter(id=data["Post"])
      if not post:
        return {"uploadFile":"Error", "messages":f"no post with id {data['Post']}"}
      else:
        post = post[0]
    objectFile = File.createFile(data["nature"], data["name"], data['ext'], currentUser, expirationDate=expirationDate, post=post)
    file = None
    try:
      file = ContentFile(base64.urlsafe_b64decode(fileStr), name=objectFile.path + data['ext']) if data['ext'] != "txt" else fileStr
      with open(objectFile.path, "wb") as outfile:
          outfile.write(file.file.getbuffer())
      return {"uploadFile":"OK", objectFile.id:objectFile.computeValues(objectFile.listFields(), currentUser, True)[:-1]}
    except:
      if file: file.delete()
      return {"uploadFile":"Warning", "messages":"Le fichier ne peut être sauvegardé"}

  @classmethod
  def __uploadImageSupervision(cls, data, currentUser):
    print("__uploadSupervision", data.keys(), currentUser, data["taskId"], data["missionId"])
    if not data['ext'] in File.authorizedExtention:
      return {"uploadFile":"Warning", "messages":f"L'extention {data['ext']} n'est pas traitée"}
    fileStr = data["imageBase64"]
    if not fileStr:
      return {"uploadFile":"Error", "messages":"field fileBase64 is empty"}
    name = "supervision"
    if data["taskId"]:
      detailedPost = DetailedPost.objects.get(id=data["taskId"])
      supervisions = Supervision.objects.filter(Mission=None, DetailedPost=detailedPost)
      mission = None
    else:
      detailedPost = None
      mission = Mission.objects.get(id=data["missionId"])
      supervisions = Supervision.objects.filter(Mission=mission)
      print("supervisions", supervisions)
      if supervisions:
        supervision = supervisions[len(supervisions) - 1]
      else:
        return {"uploadFile":"Error", "messages":f"No supervision associated to mission id {mission.id}"}

    objectFile = File.createFile("supervision", name, data['ext'], currentUser, post=None, mission=mission, detailedPost=detailedPost, supervision=supervision)
    file = None
    try:
      file = ContentFile(base64.urlsafe_b64decode(fileStr), name=objectFile.path + data['ext']) if data['ext'] != "txt" else fileStr
      with open(objectFile.path, "wb") as outfile:
          outfile.write(file.file.getbuffer())
      return {"uploadSupervision":"OK", objectFile.id:objectFile.computeValues(objectFile.listFields(), currentUser, True)[:-1]}
    except:
      if file: file.delete()
      return {"uploadSupervision":"Warning", "messages":"Le fichier ne peut être sauvegardé"}

  @classmethod
  def getEnterpriseDataFrom(cls, request):
    subName = request.GET["subName"]
    siret = request.GET["siret"] if "siret" in request.GET else None
    if os.getenv('PATH_MIDDLE'):
      externalResponse = getEnterpriseDataFrom(subName=subName, siret=siret)
      externalResponse = externalResponse["data"] if "data" in externalResponse else None
      if isinstance(externalResponse, dict) and externalResponse:
        response = {"getEnterpriseDataFrom":"OK"}
        response.update(externalResponse)
        return response
      else:
        return {"getEnterpriseDataFrom":"Error", "messages":{"list":"empty"}}
    else:
      return {"getEnterpriseDataFrom":"Error", "messages":{"local":"no installation"}}


  @classmethod
  def __modifyPwd(cls, data, currentUser):
    if data['oldPwd'] == data['newPwd']:
      return {"modifyPwd":"Warning", "messages":{"oldPwd", "L'ancien et le nouveau mot de passe sont identiques"}}
    currentUser.set_password(data['newPwd'])
    currentUser.save()
    return {"modifyPwd":"OK"}

  @classmethod
  def __updateUserInfo(cls, data, user):
    print("__updateUserInfo", data)
    if "UserProfile" in data:
      message, valueModified, userProfile = {}, {"UserProfile":{}}, UserProfile.objects.get(id=data["UserProfile"]["id"])
      flagModified = cls.__setValues(data["UserProfile"], user, message, valueModified["UserProfile"], userProfile, False)
      if not flagModified:
        message["general"] = "Aucun champ n'a été modifié" 
      if message:
        return {"modifyUser":"Warning", "messages":message, "valueModified": valueModified}
      company = userProfile.Company
      return {"modifyUser":"OK","UserProfile":{userProfile.id:userProfile.computeValues(userProfile.listFields(), user, True)}, "Company":{company.id:company.computeValues(company.listFields(), user, True)}}
    return {"modifyUser":"Warning", "messages":"Pas de valeur à mettre à jour"}
    
  @classmethod
  def __setValues(cls, dictValue, user, message, valueModified, objectInstance, flagModified):
    for fieldName, value in dictValue.items():
      print("setValue", fieldName)
      valueToSave = value
      if fieldName != "id" and fieldName != 'userName':
        fieldObject = None
        try:
          fieldObject = objectInstance._meta.get_field(fieldName)
        except:
          pass
        if fieldObject and isinstance(fieldObject, models.ForeignKey):
          valueModified[fieldName], instance = {}, getattr(objectInstance, fieldName)
          flagModifiedNew = cls.__setValues(value, user, message, valueModified[fieldName], instance, flagModified)
          flagModified = flagModifiedNew if not flagModified else flagModified
        elif fieldName in objectInstance.manyToManyObject:
          valueModified[fieldName] = {}
          flagModifiedNew = cls.__setValuesLabelJob(fieldName, value, valueModified[fieldName], user)
          flagModified = flagModifiedNew if not flagModified else flagModified
        elif getattr(objectInstance, fieldName, "does not exist") != "does not exist":
          print("setValue", fieldObject, fieldName, value)
          # valueToSave = value == "true"
          if fieldObject and isinstance(fieldObject, models.DateField):
            valueToSave = value.strftime("%Y-%m-%d") if value else None
          elif fieldObject and isinstance(fieldObject, models.IntegerField):
            valueToSave = int(value) if value else None
          elif fieldObject and isinstance(fieldObject, models.FloatField):
            valueToSave = float(value) if value else None
          elif fieldObject and isinstance(fieldObject, models.BooleanField):
            print("bool", fieldName, value, objectInstance.getAttr(fieldName))
          if valueToSave != objectInstance.getAttr(fieldName):
            objectInstance.setAttr(fieldName, valueToSave)
            objectInstance.save()
            valueModified[fieldName] = value
            flagModified = True
        else:
          message[fieldName] = "is not a field"
    return flagModified

  @classmethod
  def __setValuesLabelJob(cls, modelName, dictValue, valueModified, user):
    if modelName == "JobForCompany":
      return cls.__setValuesJob(dictValue, valueModified, user)
    else:
      return cls.__setValuesLabel(dictValue, valueModified, user)

  @classmethod
  def __setValuesJob(cls, dictValue, valueModified, user):
    company = UserProfile.objects.get(userNameInternal=user).Company
    jobForCompany = JobForCompany.objects.filter(Company=company)
    if jobForCompany:
      jobForCompany.delete()
    for listValue in dictValue:
      if listValue[1]:
        job = Job.objects.get(id=listValue[0])
        jobForCompany = JobForCompany.objects.create(Job=job, number=listValue[1], Company=company)
        if jobForCompany.number != 0:
          valueModified[jobForCompany.id] = [jobForCompany.Job.id, jobForCompany.number]
    return True

  @classmethod
  def __setValuesLabel(cls, dictValue, valueModified, user):
    company = UserProfile.objects.get(userNameInternal=user).Company
    LabelForCompany.objects.filter(Company=company).delete()
    for listValue in dictValue:
      label = Label.objects.get(id=listValue[0])
      date = datetime.strptime(listValue[1], "%Y-%m-%d") if listValue[1] else None
      labelForCompany = LabelForCompany.objects.create(Label=label, date=date, Company=company)
      date = labelForCompany.date.strftime("%Y-%m-%d") if labelForCompany.date else ""
      valueModified[labelForCompany.id] = [labelForCompany.Label.id, date]
    return True

  @classmethod
  def __modifyDisponibility(cls, listValue, user):
    company, messages = UserProfile.objects.get(userNameInternal=user).Company, {}
    if company.Role.id == 1:
      return {"modifyDisponibility":"Error", "messages":f"User company is not sub contractor {company.name}"}
    Disponibility.objects.all().delete()
    for date, nature in listValue:
      if not nature in ["Disponible", "Disponible Sous Conditions", "Non Disponible"]:
        messages[date] = f"nature incorrect: {nature} replaced by Disponible"
        nature = "Disponible"
      Disponibility.objects.create(Company=company, date=datetime.strptime(date, "%Y-%m-%d"), nature=nature)
    answer = {"modifyDisponibility":"OK"}
    answer.update({disponibility.id:[disponibility.date.strftime("%Y-%m-%d"), disponibility.nature] for disponibility in Disponibility.objects.filter(Company=company)})
    if messages:
      answer["modifyDisponibility"] = "Warning"
      answer["messages"] = messages
    return answer

  @classmethod
  def forgetPassword(cls, email):
    user = User.objects.filter(username=email)
    if user:
      userProfile = UserProfile.objects.get(userNameInternal=user[0])
      userProfile.token = SmtpConnector(cls.portSmtp).forgetPassword(email)
      userProfile.save()
      return {"forgetPassword":"Warning", "messages":"work in progress"}
    return {"forgetPassword":"Warning", "messages":f"L'adressse du couriel {email} n'est pas reconnue"}

  @classmethod
  def newPassword(cls, data):
    for key in ["token", "password"]:
      if not key in data:
        return {"newPassword":"Error", "messages":f"no {key} in post"}
    userProfile = UserProfile.objects.filter(token=data["token"])
    if userProfile:
      userProfile = userProfile[0]
      userProfile.token = None
      userProfile.save()
      user = userProfile.userNameInternal
      user.set_password(data["password"])
      user.save()
      return {"newPassword":"OK"}
    return {"newPassword":"Warning", "messages":"work in progress"}
    