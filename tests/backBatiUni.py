import requests
import json
import sys
from PIL import Image
import os
import base64
from io import BytesIO

userName, password = "st", "pwd"
# userName, password = "jlw", "pwd"
# userName, password = "jeanluc.walter@fantasiapp.com", "123456Aa"
address = 'http://localhost:8000'
query = "token"

arguments = sys.argv
if len(arguments) > 1:
    host = arguments[1]
    if host == "local": address = 'http://localhost:8000'
    elif host == "temp": address = 'https://batiuni.fantasiapp.tech:5004'
    elif host == "work": address = 'https://batiuni.fantasiapp.tech:5001'
    elif host == "current": address = 'https://batiuni.fantasiapp.tech:5002'
    elif host == "distrib": address = 'https://batiuni.fantasiapp.tech:5003'
    elif host == "distrib2": address = 'https://batiuni.fantasiapp.tech:5005'
if len(arguments) > 2:
  query = arguments[2]

def queryForToken(userName, password):
  tokenUrl = f'{address}/api-token-auth/'
  print(tokenUrl)
  headers = {'Content-Type': 'application/json'}
  data = json.dumps({"username": userName, "password": password})
  print(data)
  response = requests.post(tokenUrl, headers=headers, data=data)
  print("response row", response.text)
  dictResponse = json.loads(response.text)
  return dictResponse['token']

def getDocStr(index = 0):
  file = ["./files/documents/logoFantasiapp.png", "./files/documents/test_1.pdf", "./files/documents/test_2.pdf", "./files/documents/IMG_2465.HEIC", "./files/documents/etex.svg", "./files/documents/batiUni.png"]
  with open(file[index], "rb") as fileData:
    encoded_string = base64.b64encode(fileData.read())
  return encoded_string.decode("utf-8")

def executeQuery():
  now, data, response, url , headers = "2022/01/12", None, None, f'{address}/initialize/', {"content-type":"Application/Json"}
  if query == "register":
    headers = {}
    post1 = {"firstname":"Augustin","lastname":"Alleaume","email":"walter.jeanluc@gmail.com","password":"pwd","company":{'id': 2, 'name': 'BATIUNI', 'address': '9 rue Vintimille Paris 75009', 'activity': 'Activité inconnue', 'siret': '40422352100018', 'ntva': 'FR49404223521'},"Role":3,"proposer":"","jobs":[1,2,80]}
    post2 = {"firstname":"a","lastname":"a","email":"st","password":"pwd","company":{'id': 3, 'name': 'Sous-traitant', 'address': '74 ave des Sous-traitants Paris 75008', 'activity': 'Activité inconnue', 'siret': '40422352100021', 'ntva': 'FR49404223522'},"Role":2,"proposer":"","jobs":[1,2,80]}
    post3 = {"firstname":"a","lastname":"a","email":"pme","password":"pwd","company":{'id': 4, 'name': 'PME', 'address': '74 ave des PME Paris 75008', 'activity': 'Activité inconnue', 'siret': '40422352100019', 'ntva': 'FR49404223523'},"Role":1,"proposer":"","jobs":[1,2,80]}
    post4 = {"firstname":"a","lastname":"a","email":"both","password":"pwd","company":{'id': 5, 'name': 'both', 'address': '74 ave des deux Paris 75008', 'activity': 'Activité inconnue', 'siret': '40422352100020', 'ntva': 'FR4940422352'},"Role":3,"proposer":"","jobs":[1,2,80]}
    for post in [post1, post2, post3, post4]:
      response = requests.post(url, headers=headers, json=post)
  elif query == "registerConfirm":
      print("registerConfirm", url)
      requests.get(f'{address}/initialize/', headers=headers, params={"action":"registerConfirm", "token":"A secret code to check 9243672519"})
      requests.get(f'{address}/initialize/', headers=headers, params={"action":"registerConfirm", "token":"A secret code to check 9243672519"})
      requests.get(f'{address}/initialize/', headers=headers, params={"action":"registerConfirm", "token":"A secret code to check 9243672519"})
      response = requests.get(f'{address}/initialize/', headers=headers, params={"action":"registerConfirm", "token":"A secret code to check 9243672519"})
  elif query == "getGeneralData":
    response = requests.get(url, headers=headers, params={"action":"getGeneralData"})
  elif query == "forgetPassword":
      response = requests.get(url, headers=headers, params={"action":"forgetPassword", "email":"walter.jeanluc@gmail.com"})
  else:
    token = queryForToken("jlw", "pwd") if query in ["emptyDB", "buildDB","uploadPost", "modifyPost", "switchDraft"] else queryForToken(userName, password)
    if query == "token":
      print("token", token)
    url = f'{address}/data/'
    headers = {'Authorization': f'Token {token}'}
    if query == "getUserData":
      response = requests.get(url, headers=headers, params={"action":"getUserData"})
    elif query == "postModifyPwd":
      print("postModifyPwd")
      post = {"action":"modifyPwd", "oldPwd":"pwd", "newPwd":"pwd"}
      response = requests.post(url, headers=headers, json=post)
    elif query == "modifyUser":
      print("modifyUser")
      now = "2022-01-12"
      post = {'action': 'modifyUser', 'UserProfile': {'id': 2, 'cellPhone': '06 29 35 04 18', 'Company': {'capital': '307130', 'companyPhone': '08 92 97 64 15', 'JobForCompany':[[4,2], [5,3], [77,4]], 'LabelForCompany':[[1,now], [2,now]]}}}
      response = requests.post(url, headers=headers, json=post)
    elif query == "changeUserImage":
      post = {'action':"changeUserImage", "ext":"png", "name":"Fantasiapp_1", "imageBase64":getDocStr(5)}
      response = requests.post(url, headers=headers, json=post)
    elif query == "uploadPost":
      post1 = {'action':"uploadPost", "longitude":2.237779 , "latitude":48.848776, "address":"128 rue de Paris 92100 Boulogne", "Job":6, "numberOfPeople":3, "dueDate":"2022-02-15", "startDate":"2022-02-16", "endDate":"2022-02-28", "DatePost":["2022-03-16", "2022-03-17", "2022-02-18"], "manPower":True, "counterOffer":True, "hourlyStart":"7:30", "hourlyEnd":"17:30", "currency":"€", "description":"Première description d'un chantier", "amount":65243.10, "DetailedPost":["lavabo", "baignoire"]}
      post2 = {'action':"uploadPost", "longitude":2.324877 , "latitude":48.841625, "address":"106 rue du Cherche-Midi 75006 Paris", "Job":5, "numberOfPeople":1, "dueDate":"2022-03-15", "startDate":"2022-03-16", "endDate":"2022-04-28", "manPower":False, "counterOffer":False, "hourlyStart":"7:00", "hourlyEnd":"17:00", "currency":"€", "description":"Deuxième description d'un chantier", "amount":23456.10, "DetailedPost":["radiateur", "Chaudière"]}
      post3 = {'action':"uploadPost", "longitude":2.324877 , "latitude":48.841625, "address":"36 rue Dauphine 75006 Paris", "Job":9, "numberOfPeople":1, "dueDate":"2022-03-15", "startDate":"2022-03-16", "endDate":"2022-04-28", "manPower":True, "counterOffer":False, "hourlyStart":"7:00", "hourlyEnd":"17:00", "currency":"€", "description":"troisième description d'un chantier", "amount":12345.10, "DetailedPost":["doublage", "cloison"]}
      for post in [post1, post2, post3]:
        response = requests.post(url, headers=headers, json=post)
    elif query == "modifyPost":
      print("modifyPost")
      post = {'action':"modifyPost", "id":1, "address":"126 rue de Paris 92100 Boulogne", "Job":5, "numberOfPeople":2, "dueDate":"2022-03-15", "startDate":"2022-03-16", "endDate":"2022-04-28", "manPower":False, "counterOffer":False, "hourlyStart":"7:00", "hourlyEnd":"17:00", "currency":"€", "description":"Deuxième description d'un chantier", "amount":24456.10, "DetailedPost":["salle de bain", "douche", "lavabo"], "DatePost":["2022-03-15", "2022-03-16", "2022-03-17"]}
      response = requests.post(url, headers=headers, json=post)
    elif query == "setFavorite":
      print("setFavorite")
      requests.get(url, headers=headers, params={'action':"setFavorite", "value":"true", "Post":2})
      response = requests.get(url, headers=headers, params={'action':"setFavorite", "value":"true", "Post":3})
    elif query == "removeFavorite":
      print("removeFavorite")
      response = requests.get(url, headers=headers, params={'action':"removeFavorite", "value":"false", "Post":3})
    elif query == "isViewed":
      print("isViewed")
      response = requests.get(url, headers=headers, params={'action':"isViewed", "Post":1})
      print("response", response)
    # elif query == "deletePost":
    #   print("deletePost")
    #   post = {'action':"uploadPost", "address":"129 rue de Paris 92100 Boulogne", "Job":9, "numberOfPeople":3, "dueDate":"2022-02-15", "startDate":"2022-02-16", "endDate":"2022-02-28", "manPower":True, "counterOffer":True, "hourlyStart":"7:30", "hourlyEnd":"17:30", "currency":"€", "description":"Première description d'un chantier", "amount":65243.10, "DetailedPost":["lavabo", "baignoire"]}
    #   response = requests.post(url, headers=headers, json=post)
    #   id = None
    #   for key, value in json.loads(response.text).items():
    #     if key != "action":
    #       id = key
    #     response = requests.get(url, headers=headers, params={"action":"deletePost", "id":id})
    elif query == "modifyDisponibility":
      print("modifyDisponibility")
      post = {'action':"modifyDisponibility", "disponibility":[["2022-02-13", "Disponible"], ["2022-02-14", "Disponible Sous Conditions"], ["2022-02-15", "Non Disponible"]]}
      response = requests.post(url, headers=headers, json=post)
    elif query == "uploadFile":
      file1 = {'action':"uploadFile", "ext":"png", "name":"NF", "fileBase64":getDocStr(0), "nature":"labels", "expirationDate":"2022-02-12"}
      file2 = {'action':"uploadFile", "ext":"png", "name":"Kbis", "fileBase64":getDocStr(1), "nature":"admin", "expirationDate":"2022-02-12"}
      file3 = {'action':"uploadFile", "ext":"HEIC", "name":"URSSAF", "fileBase64":getDocStr(3), "nature":"admin", "expirationDate":"2022-02-12"}
      file4 = {'action':"uploadFile", "ext":"svg", "name":"Document technique", "fileBase64":getDocStr(4), "nature":"post", "Post":2}
      file5 = {'action':"uploadFile", "ext":"pdf", "name":"Plan", "fileBase64":getDocStr(2), "nature":"post", "Post":2}
      for file in [file1, file2, file3, file4, file5]:
        response = requests.post(url, headers=headers, json=file)
        data = json.loads(response.text)
        print("uploadFile", data.keys())
    elif query == "downloadFile":
      requests.get(url, headers=headers, params={"action":"downloadFile", "id":1})
      response = None
    elif query == "deleteFile":
      response = requests.get(url, headers=headers, params={"action":"deleteFile", "id":3})
    elif query == "applyPost":
      response = requests.get(url, headers=headers, params={'action':"applyPost", "Post":1, "amount":1000, "devis":"Par Jour"})
    elif query == "handleCandidateForPost":
      response = requests.get(url, headers=headers, params={'action':"handleCandidateForPost", "Candidate":1, "response":True})
    elif query == "signContract":
      response = requests.get(url, headers=headers, params={"action":"signContract", "missionId":1, "view":"PME"})
    elif query == "uploadSupervision":
      post = {'action':"uploadSupervision", "detailedPost":7, "comment":"Le travail est fini, Youpi."}
      response = requests.post(url, headers=headers, json=post)
      print("uploadSupervision", response)
    elif query == "switchDraft":
      response = requests.get(url, headers=headers, params={"action":"switchDraft", "id":2})
    elif query == "duplicatePost":
      print("duplicatePost")
      response = requests.get(url, headers=headers, params={"action":"duplicatePost", "id":1})
    elif query == "getPost":
      response = requests.get(url, headers=headers, params={"action":"getPost"})
    elif query == "buildDB":
      url = f'{address}/createBase/'
      response = requests.get(url, headers=headers, params={"action":"reload"})
    elif query == "emptyDB":
      url = f'{address}/createBase/'
      response = requests.get(url, headers=headers, params={"action":"emptyDB"})
    elif query == "createDetailedPost":
      print("createDetailedPost")
      post = {"action":"createDetailedPost", "missionId":1, "content":"Réparer le lavabo une nouvelle fois", "date":"2022-03-17"}
      response = requests.post(url, headers=headers, json=post)
    elif query == "modifyDetailedPost":
      print("modifyDetailedPost")
      post1 = {"action":"modifyDetailedPost", "detailedPostId":9, "content":"Finir de réparer le lavabo"}
      post2 = {"action":"modifyDetailedPost", "detailedPostId":9, "date":"2022-03-17"}
      response = requests.post(url, headers=headers, json=post1)
      data = json.loads(response.text)
      print("data", data)
      response = requests.post(url, headers=headers, json=post2)
    elif query == "deleteDetailedPost":
      print("deleteDetailedPost")
      post = {"action":"deleteDetailedPost", "detailedPostId":9}
      response = requests.post(url, headers=headers, json=post)
  if response and query != "downloadFile":
    data = json.loads(response.text)
    print("data", data)
  elif query == "downloadFile":
    print("downloadFile: not checked")
  else:
    print("no answer")
if query == "all":
    # for key in ["buildDB", "register", "registerConfirm", "modifyUser", "changeUserImage", "getUserData", "uploadPost", "modifyPost", "getPost", "switchDraft", "uploadFile", "downloadFile", "deleteFile", "modifyDisponibility", "setFavorite", "isviewed", "applyPost", "handleCandidateForPost"]: #, "uploadSupervision", "createDetailedPost", "modifyDetailedPost" , "deleteDetailedPost"
    for key in ["buildDB", "register", "registerConfirm", "modifyUser", "changeUserImage", "getUserData", "uploadPost", "modifyPost", "getPost", "switchDraft", "uploadFile", "downloadFile", "deleteFile", "modifyDisponibility"]:
      query = key
      executeQuery()
else:
  executeQuery()

