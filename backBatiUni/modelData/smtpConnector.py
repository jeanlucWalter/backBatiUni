import requests
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
    params = {"action":"mailConfirmation", "firstName":firstName, "lastName":lastName, "mail":email}
    try:
      response = requests.get(url=self.url, headers=self.headers, params=params)
      data = json.loads(response.text)
      if "token" in data:
        return data["token"]
    except:
      data = "token not received"
    return data


    


