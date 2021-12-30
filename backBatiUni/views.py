from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

class DefaultView(APIView):
  permission_classes = (IsAuthenticated,)


class Data(DefaultView):
  def get(self, request):
    return Response({"test GET":"OK"})


  def post(self, request):
    return Response({"test POST":"OK"})

