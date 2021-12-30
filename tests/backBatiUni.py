import requests
import json
import sys

userName, password = "jlw", "pwd"
address = 'http://localhost:8000'
query = "token"

arguments = sys.argv
if len(arguments) > 0:
    host = arguments[0]
    if host == "local": address = 'http://localhost:8000'
    elif host == "temp": address = 'https://batiuni.fantasiapp.tech:5004'
    elif host == "work": address = 'https://batiuni.fantasiapp.tech:5001'
    elif host == "current": address = 'https://visio.fantasiapp.tech:3439'
    elif host == "distrib": address = 'https://visio.fantasiapp.tech:3440'
    elif host == "distrib2": address = 'https://visio.fantasiapp.tech:3442'
if len(arguments) > 1:
  query = arguments[1]

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
  token = queryForToken(userName, password)
  print("query", query)
  if query == "token":
    print("token", token)
  url = f'{address}/data/'
  headers = {'Authorization': f'Token {token}'}
  if query == "get":
    response = requests.get(url, headers=headers, params={"action":"test"})
    print(response.headers)
    data = json.loads(response.text)
    print("data", data)
  if query == "post":
    post = {"post":"test"}
    response = requests.post(url, headers=headers, json=post)
    data = json.loads(response.text)
    print(data)

executeQuery()

