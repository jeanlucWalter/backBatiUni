import requests
from ..models import *
import json

class SmtpConnector:
  port = None
  url = None
  dir = "/send_mail/"
  header = {"content-type":"Application/Json"}

  def __init__(self, port, userProfile):
    SmtpConnector.port = port
    SmtpConnector.url = f'127.0.0.1:{port}{SmtpConnector.dir}'

  @classmethod
  def register(cls, userProfile):
    params = {"action":"register", "firstName":userProfile.firstName, "lastName":userProfile.lastName, "mail":userProfile.userNameInternal.username}
    print(params)
    response = requests.get(url=cls.url, header=cls.header, params=params)
    data = json.loads(response.text)
    print(data)
    

    


