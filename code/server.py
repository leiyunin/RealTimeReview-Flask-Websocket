from flask import Flask, request, jsonify
from pymongo import MongoClient, ASCENDING,DESCENDING
import re
import string
import json
app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client['La_Veranda']
collection = db['reviews']

@app.route('/') 
def hello_world():
    database = 'Database Name: La_Veranda; \nTable Name: reviews.json'
    instruction = "Support RESTful API Methods: \n 1. PUT \n 2. GET \n 3. POST \n 4. PATCH \n 5.DELETE"
    example = 'This Program Supports Command Line Interface'
    return database+'\n'+instruction+'\n'+example

# Get
@app.route('/reviews.json',methods=['GET'])
def get_request():
    result=[]
    query_params = request.args.to_dict()
    order_by=(query_params['orderBy'] if 'orderBy' in query_params else None)
    start_at=(query_params['startAt'] if 'startAt' in query_params else None)
    end_at=(query_params['endAt'] if 'endAt' in query_params else None)
    equal_to=(query_params['equalTo'] if 'equalTo' in query_params else None)
    limit_first=(query_params['limitToFirst'] if 'limitToFirst' in query_params else None)
    limit_last=(query_params['limitToLast'] if 'limitToLast' in query_params else None)
    if start_at != None and end_at !=None:
        if start_at.strip().isdigit():
            if not end_at.strip().isdigit():
                return f'endAt {end_at} should be integer',400
            if int(start_at)> int(end_at):
                return f'startAt {start_at} should be smaller than end_At {end_at}',400
        else:
            if end_at.strip().isdigit():
                return f'endAT {end_at} shoudl be string',400
            if start_at > end_at:
                return f'startAt characters {start_at} should be smaller than endAt {end_at}', 400
    if order_by is None:
        if start_at!=None or end_at!=None or limit_first!=None or limit_last!=None or equal_to!=None:
            raise ValueError({'error': 'orderBy must be defined when other query parameters are defined'})
        else:
            cursor=collection.find()
            for i in cursor:
                    result.append(i) 
            return jsonify(result)
    if '$key' in order_by or '$value' in order_by: # 3 possiblities: $key,$value,"name"
        #if orderby key, all params should be int(numerical value)
        if start_at: 
            start_at = int(start_at)
        if end_at: 
            end_at = int(end_at)
        if equal_to: 
            if start_at!=None or end_at!=None or limit_first!=None or limit_last!=None:
                print({'error': 'equalTo cannot be specified in addition to startAfter, startAt, endAt, or endBefore'})
                raise ValueError("{'error': 'equalTo cannot be specified in addition to startAfter, startAt, endAt, or endBefore'}")
            equal_to = int(equal_to)
        if limit_first: 
            limit_first = int(limit_first)
        if limit_last:
            limit_last = int(limit_last)
        if start_at is not None and end_at is None: # 3 possibilities: start,end,equal
            if start_at ==0:
                raise ValueError('_id cannot be less than 1')
            if limit_first is not None: # 2 possibilities: first, last
                cursor=collection.find().sort('_id',ASCENDING).limit(limit_first).skip(start_at-1)
            elif limit_last is not None:
                cursor=collection.find().sort('_id',DESCENDING).limit(limit_last)
            else:
                cursor=collection.find().sort('_id',ASCENDING).skip(start_at-1)
            for i in cursor:
                    result.append(i)    
        elif end_at is not None and start_at is None:
            if limit_first is not None: # 2 possibilities: first, last
                cursor=collection.find().sort('_id',ASCENDING).limit(limit_first)
            elif limit_last is not None:
                if end_at-limit_last <0:
                    raise ValueError('limitToLast number cannot exceed endAt one')
                cursor=collection.find({ "_id": { "$lte": end_at } }).sort('_id',DESCENDING).limit(limit_last)
            else:
                cursor=collection.find().sort('_id',ASCENDING).limit(end_at)
            for i in cursor:
                    result.append(i)
        elif start_at is not None and end_at is not None:
            if limit_first is not None: # 2 possibilities: first, last
                cursor=collection.find({"_id":{"$gte":start_at,"$lt":start_at+limit_first}})
            elif limit_last is not None:
                cursor=collection.find({ "_id": { "$lte": end_at } }).sort("_id", DESCENDING).limit(limit_last)
            else:
                cursor=collection.find({"_id":{"$gte":start_at,"$lte":end_at}})
            for i in cursor:
                    result.append(i)
        elif equal_to is not None: # error(start&end )
            if start_at!=None or end_at!=None or limit_first!=None or limit_last!=None:
                print({'error': 'equalTo cannot be specified in addition to startAfter, startAt, endAt, or endBefore'})
                raise ValueError("{'error': 'equalTo cannot be specified in addition to startAfter, startAt, endAt, or endBefore'}")
            cursor = collection.find({"_id":equal_to})
            for i in cursor:
                    result.append(i)
        elif start_at is None and end_at is None and limit_first is None and limit_last is None and equal_to is None:
            cursor = collection.find()
            for i in cursor:
                    result.append(i)
                
    
    elif 'Score' in order_by or 'NumberOfNights' in order_by:
        if 'Score' in order_by:
            keys = 'Score'
        else:
            keys = 'NumberOfNights'
        if start_at: 
            start_at = int(start_at)
        if end_at: 
            end_at = int(end_at)
        if equal_to: 
            if start_at!=None or end_at!=None or limit_first!=None or limit_last!=None:
                print({'error': 'equalTo cannot be specified in addition to startAfter, startAt, endAt, or endBefore'})
                raise ValueError("{'error': 'equalTo cannot be specified in addition to startAfter, startAt, endAt, or endBefore'}")
            equal_to = int(equal_to)
            
        if limit_first: 
            limit_first = int(limit_first)
        if limit_last:
            limit_last = int(limit_last)
        if start_at is not None and end_at is None: # 3 possibilities: start,end,equal
            if start_at ==0:
                raise ValueError('Value cannot be less than 1')
            if limit_first is not None: # 2 possibilities: first, last
                cursor=collection.find({keys:{"$gte":start_at}}).sort(keys ,ASCENDING).limit(limit_first)
            elif limit_last is not None:
                cursor=collection.find({keys:{"$gte":start_at}}).sort(keys,DESCENDING).limit(limit_last)
            else:
                cursor=collection.find({keys:{"$gte":start_at}}).sort(keys,ASCENDING)
            for i in cursor:
                    result.append(i)    
        elif end_at is not None and start_at is None:
            if limit_first is not None: # 2 possibilities: first, last
                cursor=collection.find({keys:{'$lte':end_at}}).sort(keys,ASCENDING).limit(limit_first)
            elif limit_last is not None:
                cursor=collection.find({keys:{'$lte':end_at}}).sort(keys,DESCENDING).limit(limit_last)
            else:
                cursor=collection.find({keys:{'$lte':end_at}}).sort(keys,ASCENDING)
            for i in cursor:
                    result.append(i)
        elif start_at is not None and end_at is not None:
            if limit_first is not None: # 2 possibilities: first, last
                cursor=collection.find({keys:{"$gte":start_at}}).sort(keys,ASCENDING).limit(limit_first)
            elif limit_last is not None:
                cursor=collection.find({keys:{'$lte':end_at}}).sort(keys,DESCENDING).limit(limit_last)
            else:
                cursor=collection.find({keys:{"$gte":start_at,"$lte":end_at}}).sort(keys,ASCENDING)
            for i in cursor:
                    result.append(i)
        elif equal_to is not None: # error(start&end )
            if start_at!=None or end_at!=None:
                print({'error': 'equalTo cannot be specified in addition to startAfter, startAt, endAt, or endBefore'})
                raise ValueError("{'error': 'equalTo cannot be specified in addition to startAfter, startAt, endAt, or endBefore'}")
            if limit_first != None:
                cursor = collection.find({keys:equal_to}).limit(limit_first)
            elif limit_last != None:
                cursor = collection.find({keys:equal_to}).sort(keys,DESCENDING).limit(limit_last)
            else:
                cursor = collection.find({keys:equal_to})
            for i in cursor:
                    result.append(i)
        elif start_at is None and end_at is None and limit_first is None and limit_last is None and equal_to is None:
            cursor = collection.find().sort(keys,ASCENDING)
            for i in cursor:
                    result.append(i)
    else:
        attr = str(order_by[1:-1])
        if start_at:
            if '"' in start_at or "'" in start_at:
                start_at = str(start_at[1:-1])
            else:
                raise ValueError("{'error': 'Constraint index field must be a JSON primitive'}")
        if end_at:
            if '"' in end_at or "'" in end_at:
                end_at = str(end_at[1:-1])
            else:
                raise ValueError("{'error': 'Constraint index field must be a JSON primitive'}")
        #cursor = collection.find().sort(attr, ASCENDING)
        #for i in cursor:
         #           result.append(i)
        if limit_first: 
            limit_first = int(limit_first)
        if limit_last:
            limit_last = int(limit_last)
            
        if start_at is not None and end_at is None: # 3 possibilities: start,end,equal
            if limit_first is not None: # 2 possibilities: first, last
                cursor = collection.find({attr:{"$gte":start_at}}).sort(attr, ASCENDING).limit(limit_first)
            elif limit_last is not None:
                cursor=collection.find({attr:{"$gte":start_at}}).sort(attr,DESCENDING).limit(limit_last)
            else:
                cursor=collection.find({attr:{"$gte":start_at}}).sort(attr,ASCENDING)
            for i in cursor:
                    result.append(i)    
        elif end_at is not None and start_at is None:
            if limit_first is not None: # 2 possibilities: first, last
                cursor=collection.find({attr:{"$lte":end_at}}).sort(attr, ASCENDING).limit(limit_first)
            elif limit_last is not None:
                cursor=collection.find({attr:{"$lte":end_at}}).sort(attr, DESCENDING).limit(limit_last)
            else:
                cursor=collection.find({attr:{"$lte":end_at}}).sort(attr,ASCENDING)
            for i in cursor:
                    result.append(i)
        elif start_at is not None and end_at is not None:
            
            if limit_first is not None: # 2 possibilities: first, last
                cursor=collection.find({attr:{"$gte":start_at, "$lte":end_at}}).sort(attr,ASCENDING).limit(limit_first)
            elif limit_last is not None:
                cursor=collection.find({attr:{"$gte":start_at, "$lte":end_at}}).sort(attr,DESCENDING).limit(limit_last)
            else:
                cursor=collection.find({attr:{"$gte":start_at,"$lte":end_at}}).sort(attr,ASCENDING)
            for i in cursor:
                    result.append(i)
        elif equal_to is not None: # error(start&end )
            if start_at!=None or end_at!=None:
                raise ValueError("{'error': 'equalTo cannot be specified in addition to startAfter, startAt, endAt, or endBefore'}")
            if limit_first != None:
                cursor = collection.find({attr:equal_to}).limit(limit_first)
            elif limit_last != None:
                cursor = collection.find({attr:equal_to}).sort(attr,DESCENDING).limit(limit_last)
            else:
                cursor = collection.find({attr:equal_to})
            for i in cursor:
                    result.append(i)
        elif start_at is None and end_at is None and limit_first is None and limit_last is None and equal_to is None:
            cursor = collection.find().sort(attr,ASCENDING)
            for i in cursor:
                    result.append(i)
    return jsonify(result)


@app.route('/reviews/<key>.json',methods=['GET'])
def get_request_key(key):
    result=[]
    query_params = request.args.to_dict()
    order_by=(query_params['orderBy'] if 'orderBy' in query_params else None)
    start_at=(query_params['startAt'] if 'startAt' in query_params else None)
    end_at=(query_params['endAt'] if 'endAt' in query_params else None)
    equal_to=(query_params['equalTo'] if 'equalTo' in query_params else None)
    limit_first=(query_params['limitToFirst'] if 'limitToFirst' in query_params else None)
    limit_last=(query_params['limitToLast'] if 'limitToLast' in query_params else None)
    if start_at != None and end_at !=None:
        if start_at.strip().isdigit():
            if not end_at.strip().isdigit():
                return f'endAt {end_at} should be integer',400
            if int(start_at)> int(end_at):
                return f'startAt {start_at} should be smaller than end_At {end_at}',400
        else:
            if end_at.strip().isdigit():
                return f'endAT {end_at} shoudl be string',400
            if start_at > end_at:
                return f'startAt characters {start_at} should be smaller than endAt {end_at}', 400
    if order_by is None:
        if start_at!=None or end_at!=None or limit_first!=None or limit_last!=None or equal_to!=None:
            raise ValueError({'error': 'orderBy must be defined when other query parameters are defined'})
        else:
            if key.strip().isdigit(): # if input is a _id
                cursor = collection.find({'_id':int(key)})
            else:
                cursor=collection.find({},{key:1,'_id':1})
            for i in cursor:
                    result.append(i)    
            return jsonify(result)
    if '$key' in order_by or '$value' in order_by: # 3 possiblities: $key,$value,"name"
        #if orderby key, all params should be int(numerical value)
        if 'Score' not in key and 'NumberOfNights' not in key:
            if start_at:
                if '"' in start_at or "'" in start_at:
                    start_at = str(start_at[1:-1])
                else:
                    raise ValueError("{'error': 'Constraint index field must be a JSON primitive'}")
            if end_at:
                if '"' in end_at or "'" in end_at:
                    end_at = str(end_at[1:-1])
                else:
                    raise ValueError("{'error': 'Constraint index field must be a JSON primitive'}")
            
            if limit_first: 
                limit_first = int(limit_first)
            if limit_last:
                limit_last = int(limit_last)
            if start_at is not None and end_at is None: # 3 possibilities: start,end,equal
                if limit_first is not None: # 2 possibilities: first, last
                    cursor = collection.find({key:{"$gte":start_at}},{key:1,'_id':1}).sort(key, ASCENDING).limit(limit_first)
                elif limit_last is not None:
                    cursor=collection.find({key:{"$gte":start_at}},{key:1,'_id':1}).sort(key,DESCENDING).limit(limit_last)
                else:
                    cursor=collection.find({key:{"$gte":start_at}},{key:1,'_id':1}).sort(key,ASCENDING)
                for i in cursor:
                        result.append(i)    
            elif end_at is not None and start_at is None:
                if limit_first is not None: # 2 possibilities: first, last
                    cursor=collection.find({key:{"$lte":end_at}},{key:1,'_id':1}).sort(key, ASCENDING).limit(limit_first)
                elif limit_last is not None:
                    cursor=collection.find({key:{"$lte":end_at}},{key:1,'_id':1}).sort(key, DESCENDING).limit(limit_last)
                else:
                    cursor=collection.find({key:{"$lte":end_at}},{key:1,'_id':1}).sort(attr,ASCENDING)
                for i in cursor:
                        result.append(i)
            elif start_at is not None and end_at is not None:
                if limit_first is not None: # 2 possibilities: first, last
                    cursor=collection.find({key:{"$gte":start_at, "$lte":end_at}},{key:1,'_id':1}).sort(key,ASCENDING).limit(limit_first)
                elif limit_last is not None:
                    cursor=collection.find({key:{"$lte":end_at}},{key:1,'_id':1}).sort(key,DESCENDING).limit(limit_last)
                else:
                    cursor=collection.find({key:{"$gte":start_at,"$lte":end_at}},{key:1,'_id':1})
                for i in cursor:
                        result.append(i)
            elif equal_to is not None: # error(start&end )
                if start_at!=None or end_at!=None or limit_first!=None or limit_last!=None:
                    raise ValueError("{'error': 'equalTo cannot be specified in addition to startAfter, startAt, endAt, or endBefore'}")
                cursor = collection.find({key:equal_to},{key:1,'_id':1})
                for i in cursor:
                        result.append(i)
            elif start_at is None and end_at is None and limit_first is None and limit_last is None and equal_to is None:
                cursor = collection.find({},{key:1,'_id':1})
                for i in cursor:
                        result.append(i)
                
    
        elif 'Score' in key or 'NumberOfNights' in key:
            if 'Score' in key:
                x = 'Score'
            else:
                x = 'NumberOfNights'
            if start_at: 
                start_at = int(start_at)
            if end_at: 
                end_at = int(end_at)
            if equal_to: 
                if start_at!=None or end_at!=None or limit_first!=None or limit_last!=None:
                    raise ValueError("{'error': 'equalTo cannot be specified in addition to startAfter, startAt, endAt, or endBefore'}")
                equal_to = int(equal_to)
            
            if limit_first: 
                limit_first = int(limit_first)
            if limit_last:
                limit_last = int(limit_last)
            if start_at is not None and end_at is None: # 3 possibilities: start,end,equal
                if start_at ==0:
                    raise ValueError('Score cannot be less than 1')
                if limit_first is not None: # 2 possibilities: first, last
                    cursor=collection.find({x:{"$gte":start_at}},{x:1,'_id':1}).sort(x,ASCENDING).limit(limit_first)
                elif limit_last is not None:
                    cursor=collection.find({x:{"$gte":start_at}},{x:1,'_id':1}).sort(x,DESCENDING).limit(limit_last)
                else:
                    cursor=collection.find({x:{"$gte":start_at}},{x:1,'_id':1}).sort(x,ASCENDING)
                for i in cursor:
                        result.append(i)    
            elif end_at is not None and start_at is None:
                if limit_first is not None: # 2 possibilities: first, last
                    cursor=collection.find({x:{'$lte':end_at}},{x:1,'_id':1}).sort(x,ASCENDING).limit(limit_first)
                elif limit_last is not None:
                    cursor=collection.find({x:{'$lte':end_at}},{x:1,'_id':1}).sort(x,DESCENDING).limit(limit_last)
                else:
                    cursor=collection.find({x:{'$lte':end_at}},{x:1,'_id':1}).sort(x,ASCENDING)
                for i in cursor:
                        result.append(i)
            elif start_at is not None and end_at is not None:
                if limit_first is not None: # 2 possibilities: first, last
                    cursor=collection.find({x:{"$gte":start_at}},{x:1,'_id':1}).sort(x,ASCENDING).limit(limit_first)
                elif limit_last is not None:
                    cursor=collection.find({x:{'$lte':end_at}},{x:1,'_id':1}).sort(x,DESCENDING).limit(limit_last)
                else:
                    cursor=collection.find({x:{"$gte":start_at,"$lte":end_at}},{x:1,'_id':1})
                for i in cursor:
                        result.append(i)
            elif equal_to is not None: # error(start&end )
                if start_at!=None or end_at!=None or limit_first!=None or limit_last!=None:
                    raise ValueError("{'error': 'equalTo cannot be specified in addition to startAfter, startAt, endAt, or endBefore'}")
                cursor = collection.find({x:equal_to},{x:1,'_id':1})
                for i in cursor:
                        result.append(i)
            elif start_at is None and end_at is None and limit_first is None and limit_last is None and equal_to is None:
                cursor = collection.find({},{x:1,'_id':1})
                for i in cursor:
                        result.append(i)
            
    return jsonify(result)

@app.route('/reviews/<ID>/<key>.json',methods=['GET'])
def get_request_id_key(ID,key):
    '''display the document _id=id, with attribute=key'''
    
    result=[]
    query_params = request.args.to_dict()
    order_by=(query_params['orderBy'] if 'orderBy' in query_params else None)
    start_at=(query_params['startAt'] if 'startAt' in query_params else None)
    end_at=(query_params['endAt'] if 'endAt' in query_params else None)
    equal_to=(query_params['equalTo'] if 'equalTo' in query_params else None)
    limit_first=(query_params['limitToFirst'] if 'limitToFirst' in query_params else None)
    limit_last=(query_params['limitToLast'] if 'limitToLast' in query_params else None)
    if order_by!=None or start_at!=None or end_at!=None or limit_first!=None or limit_last!=None or equal_to!=None:
        return f'_id={ID} cannot support orderBy method', 400
    else:
        if ID.strip().isdigit():
            cursor = collection.find({'_id':int(ID)},{key:1})
            for i in cursor:
                        result.append(i)
        else:
            return 'Invalid key parameter',400
    return jsonify(result)


'''PUT: /reviews.json'''
'''PUT Note:
1. If _id is not in the database, PUT will not do anything but raise error
2. If_id is in the database:
	PUT will first read data;
	IF data is not valid it will return 400 error with INVALID JSON DATA
	IF data is valid, it will replace the existing one with the currentone
	ATTENTION: NOT update but replace which can better mimic Firebase Results
ANOTHER NOTATION:
	in our database it cannot support command like '/reviews.json' for it will directly erase all documents 
'''
@app.route('/reviews/<key>.json', methods=['PUT'])
def put_request(key):
    if collection.count_documents({'_id': int(key)}) == 0:
        return f'Document with id {key} does not exist.', 400
    data = request.get_data().decode('utf-8')
    if not data:
        return 'Invalid JSON data', 400
    try:
        collection.replace_one({'_id':int(key)}, json.loads(data))
        return f'Document _id={key} updated successfully; input value: {data}',200
    except json.decoder.JSONDecodeError:
        return 'Invalid JSON data', 400

@app.route('/reviews.json', methods=['PUT'])
def put_request1():
    # Delete all documents
    result = collection.delete_many({})    
    # Insert new document
    data = request.get_data().decode('utf-8')
    collection.insert_one(json.loads(data))
    return f'All documents deleted and new document inserted: {data}', 200

@app.route('/reviews.json', methods=['POST'])
def post_request():
    data = request.get_data().decode('utf-8')
    json_data = json.loads(data)

    #check if id provided
    if '_id' in json_data:
    	# if _id provided in the input, check whether it's already existed
    	if collection.count_documents({'_id': int(json_data['_id'])}) > 0:
        	return f"Document with id {json_data['_id']} already exists.",400
    	json_data.pop("_id")
    last_document = collection.find().sort('_id', DESCENDING).limit(1)
    last_id = last_document[0]['_id']
    json_data['_id'] = last_id + 1
    collection.insert_one(json_data)
    return f"New document added data: {data}", 200

'''PATCH: 1. If the input key is non-existent, report error
	2. If key valid, it read the user json_data and upsert to the current existing document'''
@app.route('/reviews/<key>.json', methods=['PATCH'])
def patch_request(key):
    if collection.count_documents({'_id': int(key)}) == 0:
        raise ValueError(f'Document id {key} does not exist')
    data = request.get_data().decode('utf-8')
    json_data = json.loads(data)
    collection.update_one({'_id': int(key)}, {'$set':json_data},upsert=True)
    return f'Document _id={key} updated successfully; input value: {data}', 200

@app.route('/reviews.json', methods=['DELETE'])
def delete_all():
    result = collection.delete_many({})
    return f'{result.deleted_count} documents deleted', 200

    
@app.route('/reviews/<key>.json', methods=['DELETE'])
def delete_request(key):
    result = collection.delete_one({'_id': int(key)})
    if result.deleted_count == 0:
        return f'Document with id {key} does not exist.', 400
    return f'Document _id={key} deleted successfully', 200



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
