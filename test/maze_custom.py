custom_level=[]
custom_level.append([
[1,1,1,1,0,0,1,1,1,1],
[1,0,0,0,0,0,0,0,0,1],
[1,0,0,0,0,0,0,0,0,1],
[1,0,0,0,0,0,0,0,0,1],
[0,0,0,0,1,1,0,0,0,0],
[0,0,0,0,1,1,0,0,0,0],
[1,0,0,0,0,0,0,0,0,1],
[1,0,0,0,0,0,0,0,0,1],
[1,0,0,0,0,0,0,0,0,1],
[1,1,1,1,0,0,1,1,1,1]
])
custom_level.append([
[1,0,1,1,1,0,1,1,1,0,1],
[0,0,1,0,0,0,0,0,1,0,0],
[1,1,1,0,0,0,0,0,1,1,1],
[1,0,0,0,0,0,0,0,0,0,1],
[1,0,0,0,0,1,0,0,0,0,1],
[0,0,0,0,1,1,1,0,0,0,0],
[1,0,0,0,0,1,0,0,0,0,1],
[1,0,0,0,0,0,0,0,0,0,1],
[1,1,1,0,0,0,0,0,1,1,1],
[0,0,1,0,0,0,0,0,1,0,0],
[1,0,1,1,1,0,1,1,1,0,1]
])
print(custom_level[0])
print(custom_level[1])
print(custom_level[0][0])
print(custom_level[0][0][0])
print('row: '+str(len(custom_level[0]))+' line: '+str(len(custom_level[0][0])))
print('row: '+str(len(custom_level[1]))+' line: '+str(len(custom_level[1][0])))

import pymongo
# to start db server - mongod.exe --dbpath C:\WORK\Docs\python\mongodb\data
# CRUD (creater,read,update,delete)
connection = pymongo.MongoClient('localhost', 27017)
db = connection.test #database
custom_mazes = db.custom_mazes #collection
print ('collection size: ',custom_mazes.count())
if custom_mazes.count()==0:
	custom_mazes.insert_one({'maze':0,'matrix':custom_level[0]}) #insert
	custom_mazes.insert_one({'maze':1,'matrix':custom_level[1]}) #insert
item = custom_mazes.find()
for i in item:
	print(i)
print('count:',item.count())
