
import asyncio
import json
import websockets
import requests
from flask import Flask, request, jsonify
from pymongo import MongoClient, ASCENDING,DESCENDING

client = MongoClient('mongodb://localhost:27017/')
db = client['La_Veranda']
collection = db['reviews']

flask_server_url = "http://127.0.0.1:5001" # replace with your Flask server URL

# GET functions 
async def send_data_to_clients(websocket, path):
	#while True:
	try:
		response = requests.get(f"{flask_server_url}/reviews.json")
		data= response.json()
		await websocket.send(json.dumps(data))
		
	except:
		pass
		
	await asyncio.sleep(1)


#POST Function 
async def receive_data_from_client(websocket, path):
    #while True:
    async for message in websocket:
    	#print('1',message)
    	data1 = json.loads(message)
    	if '_id'  in data1:
    		if collection.count_documents({'_id': int(data1['_id'])}) > 0:
    			await websocket.send(json.dumps({'error': 'Error deleting documents from database'}))
    		else:
    			data1.pop('_id')
    			last_document = collection.find().sort('_id', DESCENDING).limit(1)
    			last_id = last_document[0]['_id']
    			data1['_id'] = last_id + 1
    			data1.pop('_Method')
    			collection.insert_one(data1)
    	else:
    		last_document = collection.find().sort('_id', DESCENDING).limit(1)
    		last_id = last_document[0]['_id']
    		data1['_id'] = last_id + 1
    		data1.pop('_Method')
    		collection.insert_one(data1)

# PATCH 
async def patch_data_from_client(websocket, path):
	async for message in websocket:
		print('2',message)
		data1 = json.loads(message)
		data1.pop('_Method')
		ID = data1['_id']
		data1.pop('_id')
		collection.update_one({'_id': int(ID)}, {'$set':data1},upsert=True)
		
# PUT 
async def put_data_from_client(websocket, path):
	async for message in websocket:
		print(message)
		data1 = json.loads(message)
		data1.pop('_Method')
		ID = data1['_id']
		data1.pop('_id')
		collection.replace_one({'_id':int(ID)}, data1)
		await websocket.send(json.dumps(data1))
	
#Delete By ID function
async def handle_delete_by_id_request(websocket, path):
	async for message in websocket:
		data = json.loads(message)
		key = data["id"]
		result = collection.delete_one({'_id': int(key)})
		if result.deleted_count == 0:
			await websocket.send(json.dumps({'error': f'Document with id {key} does not exist.'}))
		await websocket.send(json.dumps({'sucessful delete': key}))
        

#Filter Get
async def filter_data_from_client(websocket,path):
	async for message in websocket:
		result=[]
		query_params = json.loads(message)
		order_by=(query_params['Orderby'] if 'Orderby' in query_params else None)
		start_at=(query_params['Startat'] if 'Startat' in query_params else None)
		end_at=(query_params['Endat'] if 'Endat' in query_params else None)
		equal_to=(query_params['Equalto'] if 'Equalto' in query_params else None)
		limit_first=(query_params['LimitToFirst'] if 'LimitToFirst' in query_params else None)
		limit_last=(query_params['LimitToLast'] if 'LimitToLast' in query_params else None)
		dic={}
		dic['orderBy=']=order_by
		dic['&startAt=']=start_at
		dic['&endAt=']=end_at
		dic['&limitToFirst=']=limit_first
		dic['&limitToLast=']=limit_last
		dic['&equalTo=']=equal_to
		url1 =''
		#print(start_at.strip().isdigit())
		for k,v in dic.items():
			if v is not None and k =='&equalTo=':
				url1 = url1 + k + str(v)
			elif v is not None and v.strip().isdigit() is True:
				url1 = url1 + k + str(v) 
			elif v is not None and type(v) is str:
				url1 = url1 + k + '"'+str(v)+'"'
		print(url1)
		try:
			res = requests.get(f"{flask_server_url}/reviews.json?" + url1)
			dt= res.json()
			#print(json.dumps(dt))
			await websocket.send(json.dumps(dt))
		except:
			pass


if __name__ == "__main__":
    start_server = websockets.serve(send_data_to_clients, "127.0.0.1", 5678)
    #delete_server = websockets.serve(handle_delete_request, "127.0.0.1", 5679)
    post_server = websockets.serve(receive_data_from_client, "127.0.0.1", 5680)
    delete_id_server = websockets.serve(handle_delete_by_id_request, "127.0.0.1", 5681)
    fi_server = websockets.serve(filter_data_from_client,"127.0.0.1",5682)
    put_server = websockets.serve(put_data_from_client, "127.0.0.1", 5683)
    pat_server = websockets.serve(patch_data_from_client, "127.0.0.1", 5684)


    asyncio.get_event_loop().run_until_complete(start_server)
    #asyncio.get_event_loop().run_until_complete(delete_server)
    asyncio.get_event_loop().run_until_complete(post_server)
    asyncio.get_event_loop().run_until_complete(delete_id_server)
    asyncio.get_event_loop().run_until_complete(fi_server)
    asyncio.get_event_loop().run_until_complete(put_server)
    asyncio.get_event_loop().run_until_complete(pat_server)
    asyncio.get_event_loop().run_forever()

