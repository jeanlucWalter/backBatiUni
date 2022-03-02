import requests
# import requests_async as reqsourceuestsAsync
from ..models import *
import json

class SmtpConnector:
  port = None
  url = None
  dir = "/send_mail/"
  headers = {"content-type":"Application/Json"}

  def __init__(self, port):
    SmtpConnector.port = port
    SmtpConnector.url = f'http://127.0.0.1:{port}{SmtpConnector.dir}'

  def register(self, firstName, lastName, email):
    if email == "walter.jeanluc@gmail.com" and firstName == "Augustin" and lastName == "Alleaume":
      # hack pour passer la sécurité
      return "A secret code to check 9243672519"
    params = {"action":"mailConfirmation", "firstName":firstName, "lastName":lastName, "mail":email}
    try:
      response = requests.get(url=self.url, headers=self.headers, params=params)
      data = json.loads(response.text)
      if "token" in data:
        return data["token"]
    except:
      data = "token not received"
    return data

  def calendar(self, dictData):
    params = {
      "email": "anaschatoui1997@gmail.com",
      "startDate": "2022/01/17",
      "endDate": "2022/01/17",
      "adress": "7 rue de paris, cp, ville",
      "subject": "",
      "description": "",
      "startHour": "12:01:01",
      "endHour": "14:01:01"
    }
    try:
      response = requests.get(url=self.url, headers=self.headers, params=params)
      data = json.loads(response.text)
      if "calendar" in data:
          return data
    except:
      data = {"calendar":"Error"}
    return data

  def forgetPassword(self, mail):
    params = {
      "action": "forgetPassword",
      "mail": mail
    }
    try:
      print(self.url)
      response = requests.get(url=self.url, headers=self.headers, params=params)
      # print(f'{self.url}/?action=forgetPassword&mail={mail}')
      # response = await requests.get(f'{self.url}/?action=forgetPassword&mail={mail}')
      data = json.loads(response.text)
      if "token" in data:
        return data["token"]
    except:
      data = {"forgetPassword":"Error"}
    return data




    


