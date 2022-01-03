from ..models import *

class DataAccessor():
  tablesInitial = {"job":Job}

  @classmethod
  def getInitialData(cls):
    dictAnswer = {}
    for tableName, table in cls.tablesInitial.items():
      dictAnswer[tableName + "Fields"] = table.listFields() if len(table.listFields()) > 1 else table.listFields()[0]
      dictAnswer[tableName + "Values"] = table.dictValues()
    return dictAnswer
