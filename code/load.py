#Kerun Quan, Yuning Lei
#DSCI551 Project: Emulating Firebase
#2023/3/23
#FILE: Load.py

'''
This file reads the username of MongoDB in EC2 of the command line input, and store the JSON data
"La_Veranda_Reviews.json" into the MongoDB database called "La_Veranda" as the Collection "reviews"

Example: python3 load.py La_Veranda_Reviews.json mongodb://localhost:27017/
'''

'''How to know the port:
1.  sudo service mongod start 	--- start your service
2.  sudo service mongod status  --- check your status if you start yout service successfully
3.  cat /etc/mongod.conf		--- you will see mongoDB config including your port
'''

#Please run in EC2 instance with proper MongoDB installed and identified MongoDB username plus (optional) password
import sys
import json
from pymongo import MongoClient #if not installed, try $ pip install pymongo
import ijson

if len(sys.argv) !=3:
	raise ValueError("Command Incorrect!")

mongoHost = sys.argv[2]
mongoDB = "La_Veranda"
mongoCollection = "reviews"

if len(sys.argv) !=3:
	raise ValueError("Command Incorrect!")
json_file = sys.argv[1]
mongoHost = sys.argv[2]
mongoDB = "La_Veranda"
mongoCollection = "reviews"

print("Input Json data:",json_file)
print("Input MongoDB Host:", mongoHost)

client = MongoClient(mongoHost)
db = client[mongoDB]
collection = db[mongoCollection]
collection.drop() #ensure, if it already exist, drop the current one and perform loading data

with open (json_file,'r') as file:
	raw_data = file.read()
	# the pre-processed data has no line splitter. Add the \n split for non-bug structure of json.load
	formatted_data = raw_data.replace("}{", "}\n{")
	json_data = [json.loads(line) for line in formatted_data.split('\n')]
	
result = collection.insert_many(json_data)
print(f"Inserted {json_file} into MongoDB database '{mongoDB}' in table '{mongoCollection}'")

client.close()
print('Client Closed. Execution Completed.')

