from .models import *

class CreateNewDataBase:
  listTable = {"Job":Job}

  def emptyDataBase (self):
    print("CreateNewDataBase, emptyDataBase")
    for table in CreateNewDataBase.listTable.values():
      print("table", table)
      table.objects.all().delete()
      print("alive")
      return {"action":"emptyDataBase"}

  def fillupDataBase (self):
    for function, table in CreateNewDataBase.listTable:
      getattr(self, "fillup" + function)(table)

  def fillupJob(table):
    print("fillupJob")



