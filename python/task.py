from flask import Flask, render_template, request, redirect, url_for, jsonify
from pymongo import MongoClient
import json
from bson import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__)

# MongoDB connection
client = MongoClient('DATABASE_URL')
db = client['aakashdb']  # DB name
collection = db['tasks']

#Route
@app.route('/',)
def index():
    # Fetch existing tasks from MongoDB
    tasks = collection.find({})
    package_values =  set()
    media_values = set()
    print('values of tasks is in index fn:',tasks)
    for task in tasks:
        print('value of task is:',task)
        package_values.add(task['package'])
        media_values.add(task['media'])
        
    return render_template('submit_task.html',media_values=media_values,package_values=package_values)
    
@app.route('/load_initial_data')
def load_initial_data():
    all_data = []
    data=collection.find({})
    for task in data:
        task['_id'] = str(task['_id'])  # Convert ObjectId to string
        all_data.append(task)
    print('value of all_Data inside the load_initial_data->>>>>>:',all_data)
    # Fetch existing tasks from MongoDB
    tasks = collection.find({})
    package_values =  set()
    media_values = set()
    print('values of tasks is in index fn:',tasks)
    for task in tasks:
        print('value of task is:',task)
        package_values.add(task['package'])
        media_values.add(task['media'])
    
    return jsonify({'data': all_data, 'package_values': list(package_values), 'media_values': list(media_values)})



#Submit Task File
@app.route('/submit_task', methods=['POST'])
def submit_task():
    print('inside the submit_task function ')
    if request.method == 'POST':
        data = {
            'value': request.form['value'],
            'package': request.form['package'] if request.form['package'] != 'other' else request.form['otherPackage'],
            'media': request.form['media'] if request.form['media'] != 'other' else request.form['otherMedia'],
            'height': request.form['height']
        }

        print('value of data is:',data)
        # Insert submitted data into MongoDB
        collection.insert_one(data)

        # Fetch the tasks after insertion
        tasks = collection.find()
        print('value of tasks after data inserting:',tasks)

        # Convert tasks to a list of dictionaries
        all_data = []
        for task in tasks:
            task['_id'] = str(task['_id'])  # Convert ObjectId to string
            all_data.append(task)
        print('value of all_Data is:',all_data)

        return jsonify({'data':all_data})

#Delete Data Route
@app.route('/delete_data',methods=['GET','POST'])
def delete_data():
    print('inside the delete_Data fn')
    if request.method=='POST': 
        data=request.get_json()
        value=data.get('taskId')
        print('value of data is :',data)
        print('value of data inside the del function:',value)
        if value:
            result=collection.delete_one({'_id':ObjectId(value)})
            print('value of result is :',result)
            
            # Fetch the tasks after  deletion
            tasks = collection.find()
            print('value of tasks after data deleting:',tasks)

            # Convert tasks to a list of dictionaries
            all_data = []
            for task in tasks:
                task['_id'] = str(task['_id'])  # Convert ObjectId to string
                all_data.append(task)
            print('value of all_Data is:',all_data)
            
            return jsonify({'data':all_data})
        else:
            return jsonify({'error':'Invalid value'})

# Update Data Route
@app.route('/update_data', methods=['POST'])
def update_data():
    print('inside the update data function')
    if request.method == 'POST':
        # Extract data from the JSON request
        data = request.get_json()
        print('values of data inside the upadte data fn:',data)
        # Extract taskId from the data
        row_id = data.get('_id')

        edited_data = {
            'value': data.get('value'),
            'package': data.get('package'),
            'media': data.get('media'),
            'height': data.get('height')
        }
        print('values of edited data inside the update data fn:',edited_data)
        # Update data in the MongoDB collection
        collection.update_one({'_id': ObjectId(row_id)}, {'$set': edited_data})

        # Fetch the tasks after updating
        tasks = collection.find()

        # Convert tasks to a list of dictionaries
        all_data = []
        for task in tasks:
            task['_id'] = str(task['_id'])  # Convert ObjectId to string
            all_data.append(task)

        return jsonify({'data': all_data})

             
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)
