import requests
import json
import sys
from PIL import Image
import os
import base64
from io import BytesIO

userName, password = "walter.jeanluc@gmail.com", "pwd"
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
  dictResponse = json.loads(response.text)
  return dictResponse['token']

def getDocStr():
  file = "./files/documents/test.png"
  with open(file, "rb") as fileData:
    encoded_string = base64.b64encode(fileData.read())
  return encoded_string.decode("utf-8")

def executeQuery():
  print("execute", query)
  now, data, response, url , headers = "2022/01/12", None, None, f'{address}/initialize/', {"content-type":"Application/Json"}
  if query == "register":
    print("query", query, url)
    headers = {}
    post = {"firstname":"Jean-Luc","lastname":"Walter","email":"walter.jeanluc@gmail.com","password":"pwd","company":"Fantasiapp","role":1,"proposer":"","jobs":[1,2,3]}
    response = requests.post(url, headers=headers, json=post)
  elif query == "getGeneralData":
    response = requests.get(url, headers=headers, params={"action":"getGeneralData"})
  else:
    token = queryForToken("jlw", "pwd") if query == "buildDB" else queryForToken(userName, password)
    if query == "token":
      print("token", token)
    url = f'{address}/data/'
    headers = {'Authorization': f'Token {token}'}
    if query == "getUserData":
      response = requests.get(url, headers=headers, params={"action":"getUserData"})
    elif query == "loadImage":
      response = requests.get(url, headers=headers, params={"action":"loadImage", "id":1})
    elif query == "postModifyPwd":
      print("postModifyPwd")
      post = {"action":"modifyPwd", "oldPwd":"pwd", "newPwd":"pwd"}
      response = requests.post(url, headers=headers, json=post)
    elif query == "modifyUser":
      print("modifyUser")
      now = "2022-01-12"
      # post = {'action': 'modifyUser', 'Userprofile': {'id': 1, 'userName': 'walter.jeanluc@gmail.com', 'cellPhone': '0634090695'}, 'Company': {'id': 1, 'webSite': 'https://fantasiapp.com', "companyPhone":"01 23 45 67 89"}, 'JobForCompany':[[4,2], [5,3]], 'LabelForCompany':[[1,now], [2,now]]}
      post = {'action': 'modifyUser', 'Userprofile': {'id': 1, 'cellPhone': '0634090694', 'Company': {'capital': '12345', 'companyPhone': '01 23 45 67 88', 'JobForCompany':[[4,2], [5,3]], 'LabelForCompany':[[1,now], [2,now]]}}}
      # post = {'action': 'modifyUser', 'Userprofile': {'id': 1, 'cellPhone': '0634090695', 'Company': {'JobForCompany': [[6, 0], [18, 3], [2, 1], [3, 2]], 'capital': '123456', 'webSite': 'Https', 'companyPhone': '01234567890', 'LabelForCompany': [[1, '2022/01/19'], [3, '2022/01/19']]}}}
      response = requests.post(url, headers=headers, json=post)
    elif query == "changeUserImage":
      post = {'action':"changeUserImage", "ext":"png", "name":"Fantasiapp_1", "imageBase64":getDocStr()}
      response = requests.post(url, headers=headers, json=post)
    elif query == "buildDB":
      url = f'{address}/createBase/'
      response = requests.get(url, headers=headers, params={"action":"reload"})
  if response:
    data = json.loads(response.text)
    print("data", data)

if query == "all":
    for key in ["buildDB", "register", "modifyUser", "changeUserImage", "getUserData"]:
      query = key
      executeQuery()
else:
  executeQuery()

