from ..models import *
import json

class DataAccessor():
  tablesInitial = {"job":Job}

  @classmethod
  def getInitialData(cls):
    dictAnswer = {}
    for tableName, table in cls.tablesInitial.items():
      if len(table.listFields()) > 1:
        dictAnswer[tableName + "Fields"] = table.listFields()
      dictAnswer[tableName + "Values"] = table.dictValues()
    return dictAnswer


  def register(cls, jsonString):
    print("string", jsonString)
    data = json.loads(jsonString)
    print("register", data)
    return {"register":"OK"}

