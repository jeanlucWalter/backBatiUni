import requests
import json
import sys

userName, password = "jlw@gmail.com", "pwd"
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

def executeQuery():
  print("query", query)
  data, response, url , headers = None, None, f'{address}/initialize/', {"content-type":"Application/Json"}
  if query == "register":
    print("query", query, url)
    headers = {}
    post = {"firstname":"Jean-Luc","lastname":"Walter","email":"jlw@gmail.com","password":"pwd","company":"Fantasiapp","role":1,"proposer":"","jobs":[1,2,3]}
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
    elif query == "postModifyPwd":
      print("postModifyPwd")
      post = {"action":"modifyPwd", "oldPwd":"pwd", "newPwd":"pwd"}
      response = requests.post(url, headers=headers, json=post)
    elif query == "updateUserInfo":
      print("updateUserInfo")
      post = {"action":"updateUserInfo", "UserprofileValues":{"firstName":"Anass", "jobs":[1,4,5,6]}, "CompanyValues":{"capital":100, "labels":[1,4,5,6]}}
      response = requests.post(url, headers=headers, json=post)
    elif query == "buildDB":
      url = f'{address}/createBase/'
      response = requests.get(url, headers=headers, params={"action":"reload"})
  if response:
    data = json.loads(response.text)
    print("data", data)

executeQuery()

