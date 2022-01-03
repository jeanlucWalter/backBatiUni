import requests
import json
import sys

userName, password = "jlw", "pwd"
address = 'http://localhost:8000'
query = "token"

arguments = sys.argv
if len(arguments) > 1:
    host = arguments[1]
    if host == "local": address = 'http://localhost:8000'
    elif host == "temp": address = 'https://batiuni.fantasiapp.tech:5004'
    elif host == "work": address = 'https://batiuni.fantasiapp.tech:5001'
    elif host == "current": address = 'https://visio.fantasiapp.tech:3439'
    elif host == "distrib": address = 'https://visio.fantasiapp.tech:3440'
    elif host == "distrib2": address = 'https://visio.fantasiapp.tech:3442'
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
  if query == "register":
    url = f'{address}/register/'
    print("url", url)
    headers = {}
    post = {"company":"BatiUni", "email":"augustin@batiuni.fr", "password":"pwd", "firstName":"Augustin", "lastName":"Alleaume", "jobs":[1, 3, 5, 7], "proposer":"", "role":2}
    response = requests.post(url, headers=headers, json=post)
    data = json.loads(response.text)
    print("data", data)
    return
  token = queryForToken(userName, password)
  if query == "token":
    print("token", token)
  url = f'{address}/data/'
  headers = {'Authorization': f'Token {token}'}
  data, response = None, None
  if query == "get":
    response = requests.get(url, headers=headers, params={"action":"test"})
  elif query == "post":
    post = {"post":"test"}
    response = requests.post(url, headers=headers, json=post)
  elif query == "buildDB":
    url = f'{address}/initialize/'
    print("url", url)
    response = requests.get(url, headers=headers, params={"action":"empty"})
  if response:
    data = json.loads(response.text)
    print("data", data)

executeQuery()

