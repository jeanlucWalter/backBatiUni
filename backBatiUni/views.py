from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import *
from .modelData.buildDataBase import CreateNewDataBase
from .modelData.dataAccessor import DataAccessor

class DefaultView(APIView):
  permission_classes = (IsAuthenticated,)


class Data(DefaultView):
  def get(self, request):
    if 'action' in request.GET:
      action = request.GET["action"]
      if action == "initialize":
        return Response(DataAccessor.getInitialData())
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
    return Response(DataAccessor().register(jsonString))

class Initialize(DefaultView):
  def get(self, request):
    if 'action' in request.GET:
      action = request.GET["action"]
      if action == "reload":
        return Response(CreateNewDataBase().reloadDataBase())
    return Response({"Initialize GET":"OK"})
