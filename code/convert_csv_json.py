# 2023/3/23

'''
This file reads the csv file, "La_Veranda_Reviews-2023-01-16.csv" and convert to the json format. 
Note: Instances may contain multiple NULL values in different attributes. 
In storing the json file, if the attribute of the instance is None, don't store.

Execution format: python3 convert_csv_Json.py <.csv filename> <output JSON filename>
'''
import pandas as pd
import sys
import json
from datetime import datetime


if len(sys.argv) !=3:
	print("Sample Format: python convert_csv_Json.py input.csv output.json")
	raise ValueError("Incorrect Commands")


csv_file = sys.argv[1]
json_file = sys.argv[2]
if '.csv' not in csv_file:
	raise NameError('Invalid CSV Filename')
if '.json' not in json_file:
	raise NameError('Invalid Json Filename')

df = pd.read_csv(csv_file)
df = df.applymap(lambda x: None if pd.isnull(x) or x=='' else x) # to have a consistent Null value
df['NumberOfNights'] = df['NumberOfNights'].str.extract(r'(\d+)')
df['NumberOfNights'] = df['NumberOfNights'].astype('Int64')
df['VisitDate'] = pd.to_datetime(df['VisitDate'], format='%B %Y').dt.strftime('%Y-%m')

l=[]
for i in range(1,len(df)+1):
    l.append(i)
df.insert(0, '_id', l)
json_data = df.to_dict(orient='records')
# This will clean the dictionary to rule out the null value 
json_data_cleaned = [{k: v for k, v in item.items() if pd.notna(v)} for item in json_data]

with open (json_file, 'w') as file:
	for item in json_data_cleaned:
		json.dump(item, file)
print(f'Convertion Completed: \ninput file: {csv_file}; \noutput file: {json_file};')
		

	