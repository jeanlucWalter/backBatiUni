from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import *
from .modelData.buildDataBase import CreateNewDataBase
from .modelData.dataAccessor import DataAccessor

class DefaultView(APIView):
  permission_classes = (IsAuthenticated,)

  def confirmToken(self, user):
    userProfile = UserProfile.objects.filter(userNameInternal=user)
    if userProfile:
      return not userProfile[0].token
    return False

class Data(DefaultView):
  def get(self, request):
    if 'action' in request.GET and self.confirmToken(request.user):
      currentUser = request.user
      action = request.GET["action"]
      if action == "getUserData":
        return Response(DataAccessor.getData("user", currentUser))
      if action == "downloadFile": return Response(DataAccessor.downloadFile(request.GET["id"], currentUser))
      if action == "getEnterpriseDataFrom": return Response(DataAccessor.getEnterpriseDataFrom(request, currentUser))
      if action == "deletePost": return Response(DataAccessor.deletePost(request.GET["id"]))
      if action == "getPost": return Response(DataAccessor.getPost(currentUser))
      if action == "createMissionFromPost": return Response(DataAccessor.createMissionFromPost(request.GET["id"], currentUser))
      if action == "switchDraft": return Response(DataAccessor.switchDraft(request.GET["id"], currentUser))
      if action == "duplicatePost": return Response(DataAccessor.duplicatePost(request.GET["id"], currentUser))
      return Response({"data GET":"Error", "messages":{"action":action}})
    return Response({"data GET":"Warning", "messages":"La confirmation par mail n'est pas réalisée."})

  def post(self, request):
    if self.confirmToken(request.user):
      currentUser = request.user
      jsonBin = request.body
      jsonString = jsonBin.decode("utf8")
      return Response(DataAccessor().dataPost(jsonString, currentUser))
    return Response ({"data POST":"Warning", "messages":"La confirmation par mail n'est pas réalisée."})

class Initialize(APIView):
  permission_classes = (AllowAny,)
  def get(self, request):
    if 'action' in request.GET:
      action = request.GET["action"]
      if action == "getGeneralData":
        return Response(DataAccessor().getData("general", False))
      if action == "registerConfirm":
        return Response(DataAccessor().registerConfirm(request.GET["token"]))
      if action == "getEnterpriseDataFrom":
        return Response(DataAccessor.getEnterpriseDataFrom(request))
    return Response({"Initialize GET":"OK"})

  def post(self, request):
    jsonBin = request.body
    jsonString = jsonBin.decode("utf8")
    return Response(DataAccessor().register(jsonString))

class CreateBase(DefaultView):
  def get(self, request):
    if 'action' in request.GET:
      action = request.GET["action"]
      if action == "reload":
        return Response(CreateNewDataBase().reloadDataBase())
    return Response({"CreateBase GET":"Error"})
