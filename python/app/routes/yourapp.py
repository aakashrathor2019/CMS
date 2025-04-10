from flask import Flask, render_template, request, redirect, url_for,jsonify
from pymongo import MongoClient
from bson import ObjectId
import json
from datetime import datetime 
from flask import Blueprint

app = Flask(__name__)

# MongoDB connection
client =MongoClient('mongodb://127.0.0.1:27017')
db = client['inventry']         # DB name
collection= db['incoming_comp']  # Table Name
collection2 = db['outgoing_comp']  #Table Name
collection_changed_data=db['changed_data_collection'] #Edit Data Table
collection_indent=db['indent_details']
# Define a custom Jinja2 filter to mimic 'match'

app_bp=Blueprint('app_bp',__name__)
@app_bp.route('/')
def home_page():
    return render_template('home_page.html')    

           
@app.route('/incoming_register')
def incoming_register():
    print('>>>> link clicked incomimg')
    return render_template('incoming_register.html')


@app.route('/outgoing_register')
def outgoing_register():
     return render_template('outgoing_register.html')
    
    
    #INCOMING COMPONENT PART

#Indent Data Form 
@app.route('/indent_form', methods=['GET', 'POST'])
def indent_form():
    if request.method == 'POST':
        # Form fields
        indent_date = datetime.now().strftime('%Y-%m-%d')
        indent_time = datetime.now().strftime('%H:%M:%S')
        indent_vendor = request.form['indent_vendor']

        # Access arrays as lists
        order_codes = request.form.getlist('order_code[]')
        manufacturer_codes = request.form.getlist('manufacturer_code[]')
        qtys = [int(qty) for qty in request.form.getlist('qty[]')]
        rates = [float(rate) for rate in request.form.getlist('rate[]')]

        # Calculate total amount
        total_amount = sum(qty * rate for qty, rate in zip(qtys, rates))

        # Create a document to insert into MongoDB
        indent_data = {
            'indent_date': indent_date,
            'indent_time': indent_time,
            'indent_vendor': indent_vendor,
            'order_codes': order_codes,
            'manufacturer_codes': manufacturer_codes,
            'qtys': qtys,
            'rates': rates,
            'total_amount': total_amount
        }

        # Insert into MongoDB
        result = collection_indent.insert_one(indent_data)
        print("value of result variable:", result)
        return redirect(url_for('home_page'))

    return render_template('indent_form.html')

#Show Indent Data
@app.route('/show_data/', methods=['GET','POST'])
def show_indent_data():
    data = list(collection_indent.find({}))  # Convert the cursor to a list
    print(data)         
    return render_template('show_indent_data.html', data=data)


#Add Incoming Data
def generate_form_html_incoming(form_add_incoming_data):
    form_html_incoming = '<form method="POST" action="/add_data_incoming">'
    for field in form_add_incoming_data['fields']:
        form_html_incoming += f'<label for="{field["name"]}">{field["label"]}</label>'
        form_html_incoming += f'<input type="{field["type"]}" id="{field["name"]}" name="{field["name"]}"  required><br>'
    form_html_incoming+='<div id="extra_fields_container"><button type="button" onclick="addExtraFieldIncoming()">Add Extra Field</button> </div>'
    form_html_incoming +='<button type="submit">Add Data</button>' '</form>'
    return form_html_incoming

f=open('templates/ incoming_data_json_form.json')

form_add_incoming_data= json.load(f)
@app.route('/add_data_incoming/', methods=['POST', 'GET'])
def add_data_incoming():
    if request.method == 'POST':
        # Get data from the form fields
        date = request.form['date']
        item_component = request.form['item_component']
        quantity = request.form['quantity']
        element_part_number = request.form['element_part_number']
        manufacturing_part_number=request.form['manufacturing_part_number']
        # Check if the record already exists
        existing_record = collection.find_one({'date': date, 'item_component': item_component, 'quantity': quantity, 'element_part_number': element_part_number,'manufacturing_part_number':manufacturing_part_number})

        if existing_record:
            if existing_record.get('extra_fields') is None:
                existing_record['extra_fields'] = {}
            for key, value in request.form.items():
                if key.startswith('extra_field_'):
                    extra_field_key = key.replace('extra_field_', '')
                    if 'extra_fields' in existing_record and extra_field_key in existing_record['extra_fields']:
                        existing_record['extra_fields'][extra_field_key] = field_value
            collection.update_one({'_id': existing_record['_id']}, {'$set': existing_record})
        else:
            # Collect data from extra fields
            extra_fields = {}
            for field_name, field_value in request.form.items():
                if field_name.startswith('extra_field_'):
                    extra_field_key = field_name.replace('extra_field_', '')
                    if extra_field_key in collection.find_one({}).get('extra_fields', {}):
                        existing_record['extra_fields'][extra_field_key] = field_value
                    else:
                        extra_fields[extra_field_key] = field_value

            # Insert data into MongoDB
            data_entry = {
                'date': date,
                'item_component': item_component,
                'quantity': quantity,
                'element_part_number': element_part_number,
                'manufacturing_part_number':manufacturing_part_number,
                'extra_fields': extra_fields  # Store extra fields in a dictionary
            }
            collection.insert_one(data_entry)
            print(data_entry)
            print(extra_fields)
        return redirect(url_for('incoming_register'))

    form_html_incoming = generate_form_html_incoming(form_add_incoming_data)
    return render_template('add_data_incoming.html', form_html_incoming=form_html_incoming)

#SHOW DATA INCOMING
@app.route('/show_data_incoming/', methods=['GET'])
def show_data_incoming():
    with open('/home/trumen1/Aakas/python/templates/header_names_incoming.json', 'r') as f:
        headers = json.load(f)

    data = list(collection.find({}))  # Convert the cursor to a list
    print(data)
    for item in data:
        extra_fields = item.get('extra_fields', {})
        for field_name, field_value in extra_fields.items():
            if field_name not in headers:
                headers.append(field_name)
            if field_name not in item:
                collection.update_one({'_id': item['_id']}, {'$set': {field_name: field_value}})
                
    return render_template('show_data_incoming.html', data=data, headers=headers,extra_fields=extra_fields)
    
#EDIT DATA INCOMING
@app.route('/edit_data_incoming/<item_id>', methods=['GET','POST'])
def edit_data_incoming(item_id):
    if request.method == 'POST':
        # Retrieve the existing data by item_id
        existing_data = collection.find_one({'_id': ObjectId(item_id)})
        print("value of request form:",request.form)
        
        print("value of existing data:",existing_data)
        # Get updated data from the form
        updated_data = {
            'date': request.form['date'],
            'item_component': request.form['item_component'],
            'quantity': request.form['quantity'],
            'element_part_number': request.form['element_part_number'],
            'manufacturing_part_number': request.form['manufacturing_part_number'],
            'extra_fields': {}  # Initialize an empty dictionary for extra fields
        }
        #print("value of data changed key:",key)
        #print("value of request form is:",request.form[key])
        print("value of updated data:",updated_data)
        # Update the extra fields from the form data
        for key in request.form:
            if key not in ['date', 'item_component', 'quantity', 'element_part_number', 'manufacturing_part_number', 'item_id']:
                updated_data['extra_fields'][key] = request.form[key]

            

        # Check if the list exists for the current ID, if not create it
        if 'edit_history' not in existing_data:
            print("inside if block of edit_history")
            collection.update_one({'_id': ObjectId(item_id)}, {'$set': {'edit_history': []}})
            
            
        #Iterate the  field and find the actual edited field
        edited_field=None
        for key in request.form:
            print("inside the for loop",key)
            if key != 'item_id':
                print("inside for loop", key)
                if existing_data.get(key) != request.form[key]:
                    edited_field = key
                    print("value of key inside 2nd if:",key)
                    print("inside if of edited field:", edited_field)
                    break
        
        if edited_field:
             edit_object = {
                'field_name':edited_field,
                'date_of_change': datetime.now().strftime("%d-%m-%y"),
                'time_of_change': datetime.now().time().strftime("%H:%M:%S"),
                'user_name': '',  # Replace with actual user name
                'old_value': existing_data.get(key),
                'new_value': request.form[edited_field]
             }
             print("value of edit object is:",edit_object)
             collection.update_one({'_id': ObjectId(item_id)}, {'$push': {'edit_history': edit_object}})
        collection.update_one({'_id': ObjectId(item_id)}, {'$set': updated_data})

        return redirect(url_for('show_data_incoming'))

    # Handle the GET request to render the edit form
    data = collection.find_one({'_id': ObjectId(item_id)})
    return render_template('edit_data_incoming.html',  data=data, item_id=item_id)

    
    
    
#DELETE DATA INCOMING   
@app.route('/delete_data_incoming/<item_id>', methods=['GET','POST'])
def delete_data_incoming(item_id):
    print('>>>>', item_id)
    if request.method == 'GET':
        print('>>>>', item_id)
    # Delete data from MongoDB
        collection.delete_one({'_id': ObjectId(item_id)})
        print('>>>>', item_id)
        #return render_template('show_data_incoming.html',data=data)
    
    return redirect(url_for('show_data_incoming'))
    
    
    #OUTGOING COMPONENTS PART
    
#ADD OUTGOING DATA
def generate_form_html_outgoing(form_add_outgoing_data):
    form_html_outgoing = '<form method="POST" action="/add_data_outgoing">'
    for field in form_add_outgoing_data['fields']:
        form_html_outgoing += f'<label for="{field["name"]}">{field["label"]}</label>'
        form_html_outgoing += f'<input type="{field["type"]}" id="{field["name"]}" name="{field["name"]}"  required><br>'
    form_html_outgoing+='<div id="extra_fields_container"><button type="button" onclick="addExtraFieldOutgoing()">Add Extra Field</button> </div>'
    form_html_outgoing +='<button type="submit">Add Data</button>' '</form>'
    return form_html_outgoing

f=open('/home/trumen1/Aakas/python/templates/outgoing_data_json_form.json')

form_add_outgoing_data= json.load(f)
@app.route('/add_data_outgoing/', methods=['POST', 'GET'])
def add_data_outgoing():
    if request.method == 'POST':
        # Collect data from extra fields
        extra_fields = {}
        for field_name, field_value in request.form.items():
            if field_name.startswith('extra_field_'):
                extra_fields[field_name.replace('extra_field_', '')] = field_value
        # Get data from the form fields
        date = request.form['date']
        item_component = request.form['item_component']
        quantity = request.form['quantity']
        element_part_number = request.form['element_part_number']
        manufacturing_part_number=request.form['manufacturing_part_number']

        # Check if the record already exists
        existing_record = collection2.find_one({'date': date, 'item_component': item_component, 'quantity': quantity,'element_part_number': element_part_number,'manufacturing_part_number':manufacturing_part_number})

        if existing_record:
            # Update existing record with new extra fields data                                             
            for key, value in extra_fields.items():
                existing_record[key] = value
            collection2.update_one({'_id': existing_record['_id']}, {'$set': existing_record})
        else:
            # Insert data into MongoDB
            data_entry = {
                'date': date,
                'item_component': item_component,
                'quantity': quantity,
                'element_part_number': element_part_number,
                'manufacturing_part_number':manufacturing_part_number,
                'extra_fields': extra_fields  # Store extra fields in a dictionary
            }
            collection2.insert_one(data_entry)
            print(data_entry)
            print(extra_fields)
        return redirect(url_for('outgoing_register'))

    form_html_outgoing = generate_form_html_outgoing(form_add_outgoing_data)
    return render_template('add_data_outgoing.html', form_html_outgoing=form_html_outgoing)


#SHOW OUTGOING DATA
@app.route('/show_data_outgoing/', methods=['GET'])
def show_data_outgoing():
    with open('/home/trumen1/Aakas/python/templates/header_names_outgoing.json', 'r') as f:
        headers = json.load(f)

    data = list(collection2.find({}))  # Convert the cursor to a list
    print(data)
    for item in data:
        extra_fields = item.get('extra_fields', {})
        for field_name, field_value in extra_fields.items():
            if field_name not in headers:
                headers.append(field_name)
            if field_name not in item:
                collection2.update_one({'_id': item['_id']}, {'$set': {field_name: field_value}})

    return render_template('show_data_outgoing.html', data=data, headers=headers,extra_fields=extra_fields)

#EDIT OUTGOING DATA    
@app.route('/edit_data_outgoing/<item_id>', methods=['GET','POST'])
def edit_data_outgoing(item_id):
    if request.method == 'POST':
        # Retrieve the existing data by item_id
        existing_data = collection2.find_one({'_id': ObjectId(item_id)})
        print("value of request form:",request.form)
        
        print("value of existing data:",existing_data)
        # Get updated data from the form
        updated_data = {
            'date': request.form['date'],
            'item_component': request.form['item_component'],
            'quantity': request.form['quantity'],
            'element_part_number': request.form['element_part_number'],
            'manufacturing_part_number': request.form['manufacturing_part_number'],
            'extra_fields': {}  # Initialize an empty dictionary for extra fields
        }
        #print("value of data changed key:",key)
        #print("value of request form is:",request.form[key])
        print("value of updated data:",updated_data)
        # Update the extra fields from the form data
        for key in request.form:
            if key not in ['date', 'item_component', 'quantity', 'element_part_number', 'manufacturing_part_number', 'item_id']:
                print("edit data of extra fields",request.form[key])
                updated_data['extra_fields'][key] = request.form[key]

            

        # Check if the list exists for the current ID, if not create it
        if 'edit_history' not in existing_data:
            print("inside if block of edit_history")
            collection2.update_one({'_id': ObjectId(item_id)}, {'$set': {'edit_history': []}})
            
            
        #Iterate the  field and find the actual edited field
        edited_field=None
        for key in request.form:
            print("inside the for loop",key)
            if key != 'item_id':
                print("inside for loop", key)
                if existing_data.get(key) != request.form[key]:
                    edited_field = key
                    print("value of key inside 2nd if:",key)
                    print("inside if of edited field:", edited_field)
                    break
        
        if edited_field:
             edit_object = {
                'field_name':edited_field,
                'date_of_change': datetime.now().strftime("%d-%m-%y"),
                'time_of_change': datetime.now().time().strftime("%H:%M:%S"),
                'user_name': '',  # Replace with actual user name
                'old_value': existing_data.get(key),
                'new_value': request.form[edited_field]
             }
             print("value of edit object is:",edit_object)
             collection2.update_one({'_id': ObjectId(item_id)}, {'$push': {'edit_history': edit_object}})

        # Update data in MongoDB
        collection2.update_one({'_id': ObjectId(item_id)}, {'$set': updated_data})

        return redirect(url_for('show_data_outgoing'))

    # Handle the GET request to render the edit form
    data = collection2.find_one({'_id': ObjectId(item_id)})
    return render_template('edit_data_outgoing.html',  data=data, item_id=item_id)


#OUTGOING DELETE COMPONENT
@app.route('/delete_data_outgoing/<item_id>', methods=['GET','POST'])
def delete_data_outgoing(item_id):
    print('>>>>', item_id)
    if request.method == 'GET':
        print('>>>>', item_id)
    # Delete data from MongoDB
        collection2.delete_one({'_id': ObjectId(item_id)})
        print('>>>>', item_id)
        #return render_template('show_data_outgoing.html',data=data)
    return redirect(url_for('show_data_outgoing'))
 
if __name__ == '__main__':
    app.run(debug=True, port=5004)
