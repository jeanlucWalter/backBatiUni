import requests
import json
import sys
from PIL import Image
import os
import base64
from io import BytesIO

userName, password = "walter.jeanluc@gmail.com", "pwd"
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
  file = ["./files/documents/logoFantasiapp.png", "./files/documents/test_1.pdf", "./files/documents/test_2.pdf"]
  with open(file[index], "rb") as fileData:
    encoded_string = base64.b64encode(fileData.read())
  return encoded_string.decode("utf-8")

def executeQuery():
  print("execute", query)
  now, data, response, url , headers = "2022/01/12", None, None, f'{address}/initialize/', {"content-type":"Application/Json"}
  if query == "register":
    print("query", query, url)
    headers = {}
    post = {"firstname":"Jean-Luc","lastname":"Walter","email":"walter.jeanluc@gmail.com","password":"pwd","company":{'id': 0, 'name': 'CARREFOUR', 'address': 'QUARTIER PEROU, 97230 SAINTE-MARIE', 'activitePrincipale': 'Activité inconnue', 'siret': '40422352100018', 'NTVAI': 'FR49404223521'},"role":2,"proposer":"","jobs":[1,2,3]}
    response = requests.post(url, headers=headers, json=post)
  elif query == "registerConfirm":
      print("registerConfirm", url)
      response = requests.get(f'{address}/initialize/', headers=headers, params={"action":"registerConfirm", "token":"token not received"})
  elif query == "getGeneralData":
    response = requests.get(url, headers=headers, params={"action":"getGeneralData"})
  elif query == "forgetPassword":
      response = requests.get(url, headers=headers, params={"action":"forgetPassword", "email":"walter.jeanluc@gmail.com"})
  else:
    token = queryForToken("jlw", "pwd") if query == "buildDB" else queryForToken(userName, password)
    if query == "token":
      print("token", token)
    url = f'{address}/data/'
    headers = {'Authorization': f'Token {token}'}
    if query == "getUserData":
      response = requests.get(url, headers=headers, params={"action":"getUserData"})
    elif query == "downloadFile":
      response = requests.get(url, headers=headers, params={"action":"downloadFile", "id":1})
    elif query == "postModifyPwd":
      print("postModifyPwd")
      post = {"action":"modifyPwd", "oldPwd":"pwd", "newPwd":"pwd"}
      response = requests.post(url, headers=headers, json=post)
    elif query == "modifyUser":
      print("modifyUser")
      now = "2022-01-12"
      post = {'action': 'modifyUser', 'Userprofile': {'id': 1, 'cellPhone': '0634090694', 'Company': {'capital': '12345', 'companyPhone': '01 23 45 67 88', 'JobForCompany':[[4,2], [5,3]], 'LabelForCompany':[[1,now], [2,now]]}}}
      response = requests.post(url, headers=headers, json=post)
    elif query == "changeUserImage":
      post = {'action':"changeUserImage", "ext":"png", "name":"Fantasiapp_1", "imageBase64":getDocStr(0)}
      response = requests.post(url, headers=headers, json=post)
    elif query == "uploadPost":
      post1 = {'action':"uploadPost", "address":"128 rue de Paris 92100 Boulogne", "Job":9, "numberOfPeople":3, "dueDate":"2022-02-15", "startDate":"2022-02-16", "endDate":"2022-02-28", "manPower":True, "counterOffer":True, "hourlyStart":"7:30", "hourlyEnd":"17:30", "currency":"€", "description":"Première description d'un chantier", "amount":65243.10, "DetailedPost":["lavabo", "baignoire"]}
      post2 = {'action':"uploadPost", "address":"156 rue du Cherche-Midi 75006 Paris", "Job":5, "numberOfPeople":1, "dueDate":"2022-03-15", "startDate":"2022-03-16", "endDate":"2022-04-28", "manPower":False, "counterOffer":False, "hourlyStart":"7:00", "hourlyEnd":"17:00", "currency":"€", "description":"Deuxième description d'un chantier", "amount":23456.10, "DetailedPost":["radiateur", "cloison"]}
      requests.post(url, headers=headers, json=post2)
      response = requests.post(url, headers=headers, json=post1)
    elif query == "modifyPost":
      print("modifyPost")
      post = {'action':"modifyPost", "id":1, "address":"156 rue du Cherche-Midi 75006 Paris", "Job":6, "numberOfPeople":2, "dueDate":"2022-03-15", "startDate":"2022-03-16", "endDate":"2022-04-28", "manPower":False, "counterOffer":False, "hourlyStart":"7:00", "hourlyEnd":"17:00", "currency":"€", "description":"Deuxième description d'un chantier", "amount":24456.10, "DetailedPost":["radiateur", "cloison", "doublage"]}
      response = requests.post(url, headers=headers, json=post)
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
      post1 = {'action':"uploadFile", "ext":"png", "name":"NF", "fileBase64":getDocStr(1), "nature":"labels", "expirationDate":"2022-01-12"}
      post2 = {'action':"uploadFile", "ext":"png", "name":"Kbis", "fileBase64":getDocStr(1), "nature":"admin", "expirationDate":"2022-01-12"}
      requests.post(url, headers=headers, json=post2)
      response = requests.post(url, headers=headers, json=post1)
    elif query == "switchDraft":
      print("switchDraft")
      response = requests.get(url, headers=headers, params={"action":"switchDraft", "id":1})
    elif query == "duplicatePost":
      print("duplicatePost")
      response = requests.get(url, headers=headers, params={"action":"duplicatePost", "id":1})
    elif query == "createMissionFromPost":
      response = requests.get(url, headers=headers, params={"action":"createMissionFromPost", "id":1})
    elif query == "getPost":
      response = requests.get(url, headers=headers, params={"action":"getPost"})
    elif query == "buildDB":
      url = f'{address}/createBase/'
      response = requests.get(url, headers=headers, params={"action":"reload"})
  if response:
    data = json.loads(response.text)
    print("data", data)
  else:
    print("no answer")

if query == "all":
    for key in ["buildDB", "register", "registerConfirm", "modifyUser", "changeUserImage", "getUserData", "uploadPost", "modifyPost", "getPost", "uploadFile", "modifyDisponibility"]:
      query = key
      executeQuery()
else:
  executeQuery()

