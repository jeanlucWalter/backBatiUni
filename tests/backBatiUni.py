import requests
import json

userName, password = "jlw", "pwd"
address = 'http://localhost:8000'

def queryForToken(userName, password):
  tokenUrl = f'{address}/api-token-auth/'
  print(tokenUrl)
  headers = {'Content-Type': 'application/json'}
  data = json.dumps({"username": userName, "password": password})
  print(data)
  response = requests.post(tokenUrl, headers=headers, data=data)
  dictResponse = json.loads(response.text)
  print(dictResponse)

queryForToken(userName, password)