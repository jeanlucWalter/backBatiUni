from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import *
from .buildDataBase import CreateNewDataBase

class DefaultView(APIView):
  permission_classes = (IsAuthenticated,)


class Data(DefaultView):
  def get(self, request):
    return Response({"test GET":"OK"})


  def post(self, request):
    return Response({"test POST":"OK"})


class Register(APIView):
  permission_classes = (AllowAny,)

  def get(self, request):
    return Response({"register GET":"OK"})

  def post(self, request):
    jsonBin = request.body
    jsonString = jsonBin.decode("utf8")
    print(jsonString)
    return Response({"register POST":"OK"})

class Initialize(DefaultView):
  def get(self, request):
    print("initialize get")
    if 'action' in request.GET:
      action = request.GET["action"]
      print("action", action)
      if action == "empty":
        return Response(self.emptyDb())
    return Response({"Initialize GET":"OK"})


  def emptyDb(self):
    print("empty in views")
    creation = CreateNewDataBase()
    return creation.emptyDataBase()

