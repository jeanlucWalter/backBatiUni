import requests
from ..models import *
import json

class SmtpConnector:
  port = None
  url = None
  dir = "/send_mail/"
  header = {"content-type":"Application/Json"}

  def __init__(self, port):
    SmtpConnector.port = port
    SmtpConnector.url = f'127.0.0.1:{port}{SmtpConnector.dir}'

  def register(self, firstName, lastName, email):
    params = {"action":"mailConfirmation", "firstName":firstName, "lastName":lastName, "mail":email}
    print(params)
    response = requests.get(url=self.url, header=self.header, params=params)
    data = json.loads(response.text)
    print(data)


    


