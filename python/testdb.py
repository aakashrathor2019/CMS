from flask import Flask, render_template, request, redirect, session, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin,current_user
from pymongo import MongoClient
import os 
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# MongoDB configuration
client =MongoClient('DATABASE_URL')
db=client['aakashdb']
collection_coffee=['coffee']

# Login Manager configuration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User model
class User(UserMixin):
    def __init__(self, user_id, username, user_type):
        self.id = user_id
        self.username = username
        self.user_type = user_type

# Load user from MongoDB
@login_manager.user_loader
def load_user(user_id):
    user_data = collection_coffee.find_one({'_id': user_id})
    if user_data:
        return User(user_id=str(user_data['_id']), username=user_data['username'], user_type=user_data['user_type'])
    return None

 

# Route for signup
@app.route('/signup1/', methods=['GET', 'POST'])
def signup1():
    if request.method == 'POST':
        print('inside the signup fn***')
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']

        existing_user = collection_coffee.users.find_one({'username': username})
        if existing_user:
            return render_template('signup1.html', error='Username already exists. Please choose another one.')
        else:
            # Insert new user into the database
            user_id = collection_coffee.insert_one({'username': username, 'password': password, 'user_type': user_type}).inserted_id
            return redirect(url_for('login1'))

    return render_template('signup1.html', error=None)

# Route for login
@app.route('/', methods=['GET', 'POST'])
def login1():
    print('login function called')
    if request.method == 'POST':
        print('inside the login fn')
        username = request.form['username']
        password = request.form['password']

        user_data = collection_coffee.find_one({'username': username, 'password': password})
        if user_data:
            user_obj = User(user_id=str(user_data['_id']), username=user_data['username'], user_type=user_data['user_type'])
            login_user(user_obj)
            return redirect(url_for('dashboard'))

        return render_template('login1.html', error='Invalid credentials. Please try again.')

    return render_template('login1.html', error=None)
#Dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    print('inside the dashboard function')
    user_type = session.get('user_type')
    if user_type == 'student':
        print('inside the student user')
        return redirect(url_for('student'))
    elif user_type == 'teacher':
        return redirect(url_for('teacher'))
    else:
        return redirect(url_for('home'))

# Route for logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# Route for student dashboard
@app.route('/student')
@login_required
def student():
    if current_user.user_type == 'student':
        return render_template('student.html', username=current_user.username)
    else:
        return redirect(url_for('home'))

# Route for teacher dashboard   
@app.route('/teacher')
@login_required
def teacher():
    if current_user.user_type == 'teacher':
        return render_template('teacher.html', username=current_user.username)
    else:
        return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True ,port=5001)

# from flask import Flask, render_template, request, redirect, url_for,jsonify
# from pymongo import MongoClient
# from bson import ObjectId
# import json
# import uuid
# from datetime import datetime 
     

# app = Flask(__name__)

# #MongoDB connection
# client =MongoClient('mongodb://aakash:aakash123@192.168.0.194:27017/aakashdb?authSource=admin')
# db=client['aakashdb']
# collection_coffee=db['coffee']
# @app.route('/',methods=['GET','POST'])
# def ind():
#     if request.method=='POST':
#         coffeeName=request.form['coffee_name']
#         print("value of coffee name is:",coffeeName)
#         collection_coffee.insert_one({'coffee_name':coffeeName})
#         return  "Coffee Name:"+coffeeName    
#     return render_template('ind.html')
 
        
# #client = MongoClient('mongodb://127.0.0.1:27017')
# db = client['aakashdb']         # DB name
# collection_indent= db['indent']  # Table Name
# collection_inward = db['inward']  #Table Name
# collection_outward=db['outward']   #Table Name
# collection_purchaser=db['purchaser']
# #Define a custom Jinja2 filter to mimic 'match'
# @app.route('/')
# def home_page():
#     return render_template('home_page.html')    

           
# @app.route('/inward_data')
# def inwad_data():
#     print('>>>> link clicked incomimg')
#     return render_template('inward_data.html')


# @app.route('/outward_data')
# def outward_data():
#      return render_template('outward_data.html')

# #Indent Code

# #Indent Data Form
# #@app.route('/indent_form', methods =['GET', 'POST'])
# #def indent_form():
# #if request.method == 'POST':
# # #Form fields
# #indent_date = datetime.now().strftime('%y-%m-%d')
# #indent_time = datetime.now().strftime('%H:%M:%S')
# #indent_vendor = request.form['indent_vendor']

# # #Access arrays as lists
# #item_descrs = request.form.getlist('item_descr[]')
# #order_codes = request.form.getlist('order_code[]')
# #manufacturer_codes = request.form.getlist('manufacturer_code[]')
# #qtys = [int(qty) for qty in request.form.getlist('qty[]')]
# #rates = [float(rate) for rate in request.form.getlist('rate[]')]

# # #Calculate total amount
# #total_amount = sum(qty * rate for qty, rate in zip(qtys, rates))

# # #Create a document to insert into MongoDB
# #indent_data = {
# #'indent_date' : indent_date,
# #'indent_time' : indent_time,
# #'indent_vendor' : indent_vendor,
# #'item_descrs' : item_descrs,
# #'order_codes' : order_codes,
# #'manufacturer_codes' : manufacturer_codes,
# #'qtys' : qtys,
# #'rates' : rates,
# #'total_amount' : total_amount
# #}

# # #Insert into MongoDB
# #result = collection_indent.insert_one(indent_data)
# #print("value of result variable:", result)
# #return redirect(url_for('home_page'))

# #return render_template('indent_form.html')

# # #Show Indent Data
# #@app.route('/show_indent_data/', methods =['GET', 'POST'])
# #def show_indent_data():
# #data = list(collection_indent.find({})) #Convert the cursor to a list
# #print(data)
# #return render_template('show_indent_data.html', data = data)

# #if __name__ == '__main__':
# #app.run(debug = True, port = 5000)

# #from flask import Flask, render_template, request, redirect, url_for, jsonify
# #from pymongo import MongoClient
# #from bson import ObjectId
# #import json
# #from datetime import datetime

# #app = Flask(__name__)

# #MongoDB connection
# #client = MongoClient('mongodb://127.0.0.1:27017')
# #db = client['inventry'] #DB name
# #collection = db['incoming_comp'] #Table Name
# #collection2 = db['outgoing_comp'] #Table Name
# #collection_changed_data = db['changed_data_collection'] #Edit Data Table
# #collection_indent = db['indent_details']
# # #Define a custom Jinja2 filter to mimic 'match'
# #@app.route('/')
# #def home_page():
# #return render_template('home_page.html')

# #@app.route('/incoming_register')
# #def incoming_register():
# #print('>>>> link clicked incomimg')
# #return render_template('incoming_register.html')

# #@app.route('/outgoing_register')
# #def outgoing_register():
# #return render_template('outgoing_register.html')

# #INCOMING COMPONENT PART

# #Indent Data Form
# #@app.route('/indent_form', methods =['GET', 'POST'])
# #def indent_form():
# #if request.method == 'POST':
# # #Form fields
# #indent_date = datetime.now().strftime('%Y-%m-%d')
# #indent_time = datetime.now().strftime('%H:%M:%S')
# #indent_vendor = request.form['indent_vendor']

# # #Access arrays as lists
# #order_codes = request.form.getlist('order_code[]')
# #manufacturer_codes = request.form.getlist('manufacturer_code[]')
# #qtys = [int(qty) for qty in request.form.getlist('qty[]')]
# #rates = [float(rate) for rate in request.form.getlist('rate[]')]

# # #Calculate total amount
# #total_amount = sum(qty * rate for qty, rate in zip(qtys, rates))

# # #Create a document to insert into MongoDB
# #indent_data = {
# #'indent_date' : indent_date,
# #'indent_time' : indent_time,
# #'indent_vendor' : indent_vendor,
# #'order_codes' : order_codes,
# #'manufacturer_codes' : manufacturer_codes,
# #'qtys' : qtys,
# #'rates' : rates,
# #'total_amount' : total_amount
# #}

# # #Insert into MongoDB
# #result = collection_indent.insert_one(indent_data)
# #print("value of result variable:", result)
# #return redirect(url_for('home_page'))

# #return render_template('indent_form.html')

# #Show Indent Data
# #@app.route('/show_indent_data/', methods =['GET', 'POST'])
# #def show_indent_data():
# #data = list(collection_indent.find({})) #Convert the cursor to a list
# #print(data)
# #return render_template('show_indent_data.html', data = data)

# # #Add Incoming Data
# #def generate_form_indent(form_indent_data):
# #form_indent = '<form method="POST" action="/indent_form">'
# #for field in form_indent_data['fields']:
# #form_indent += f '<label for="{field["name"]}">{field["label"]}</label>'
# #form_indent += f '<input type="{field["type"]}" id="{field["name"]}" name="{field["name"]}"  required><br>'
# #form_indent += '<div id="extra_fields_container"><button type="button" onclick="addExtraFieldIndent()">Add Extra Field</button> </div>'
# #form_indent += '<button type="submit">Add Data</button>' '</form>'
# #return form_indent

# #f = open('templates/ incoming_data_json_form.json')

# #form_indent_data = json.load(f)

# #INDENT DATA INFORMATION
# #ADD INDENT DATA
# @app.route('/indent_form/',methods=['GET','POST'])
# def indent_form():
#     if request.method=='POST':

# #Get data from the form fields
# #Form fields

# #indentId = request.form['indentId']
# #dateTime = request.form['dateTime']

#         #Access arrays as lists
#         indentId=request.form['indentId']
#         dateTime=request.form['dateTime']
#         item_id_list = request.form.getlist('itemId[]')
#         item_name_list=request.form.getlist('itemName[]')
#         manufacturer_codes_list = request.form.getlist('mfrCode[]')
#         item_descr_list=request.form.getlist('itemDesc[]')
#         qtys_list = [int(qty) for qty in request.form.getlist('qty[]')]
#         rates_list = [float(rate) for rate in request.form.getlist('rate[]')]
#         print("values of requset.form is:",request.form)
         
#         print("values  of request.form.items() is:",request.form.items()) 
        
#         print("value of item_descr_list:",item_descr_list)
#         print("value of qtys list is:",qtys_list)

#         #Create documents for each indent
#         indent_data_list = []
#         for i in range(len(item_descr_list)):
#             print("inside the for loop of indent data")
#             total_amount = qtys_list[i] * rates_list[i]

#             #Create an indent_data dictionary
#             indent_data = {
#                 'indentId':indentId,
#                 'dateTime':dateTime,
#                 'itemId':item_id_list[i],
#                 'itemName':item_name_list[i],
#                 'mfrCode': manufacturer_codes_list[i],
#                 'itemDesc': item_descr_list[i],
#                 'qty': qtys_list[i],
#                 'rate': rates_list[i],
#                 'total_amount': total_amount,
#                 'status':'Indent Created'
#                 #'extra_fields' : extra_fields      #Directly assign the extra_fields dictionary
#             }
#             print("data type of qty is:",type(qtys_list[i]))
#             print("data type of rate is:",type(rates_list[i]))
#             print("data type of total_amount is:",type(total_amount))
#             indent_data_list.append(indent_data)
#             collection_indent.insert_one(indent_data)

#         #Print the values of indent data and extra fields
#         print("values of indent data list:", indent_data_list)
#         return jsonify({'data received and stored successfully'})
          
#     return render_template('indent_form.html',uuid=uuid,datetime=datetime )

# #STORE INDENT DATA
# @app.route('/store_indent_data', methods=['GET','POST'])
# def store_indent_data():
#     if request.method=='POST':
        
#         data = request.get_json()
#         #Access data elements as needed
#         #Modify this part based on your actual data structure
#         indentId = data.get('indentId')
#         dateTime = data.get('dateTime')
#         indentDataArray = data.get('indentData')

#         print("value of indentId is:",indentId)
#         print("value of datatime is:",dateTime)
#         print('value of indentdataarray is:',indentDataArray)
#         #Insert data into the collection_indent collection
#         for indentData in indentDataArray:
#             collection_indent.insert_one(indentData)
#             print("value of indent Data is:",indentData)

#         return list(['data received and stored successfully'])
#     return render_template('indent_form.html')

# #DRAFT DATA
# @app.route('/draft_data', methods=['GET','POST'])
# def draft_data():
#     if request.method=='POST':
        
#         data = request.get_json()
#         #Access data elements as needed
#         #Modify this part based on your actual data structure
         
#         draftDataArray = data.get('draftData')

        
#         print('value of draftdataarray is:',draftDataArray)
#         #Insert data into the collection_indent collection
#         for draftData in draftDataArray:
#             item_id=draftData['itemId']
#         #update status in collection_indent for the specific item
#             collection_indent.update_one({'itemId': item_id},{'$set': {'status': draftData['status']}})
#             collection_purchaser.update_one({'itemId': item_id},{'$set': {'status': draftData['status']}})

#         #update status in collection_purchaser for the specific item
#             collection_indent.update_one({'itemId': item_id},{'$set': {'remark': draftData['remark']}})
#             collection_purchaser.update_one({'itemId': item_id},{'$set': {'remark': draftData['remark']}})
#             print("value of indent Data is:",draftData)

#         return list(['data received and stored successfully'])
#     return render_template('purchaser_data.html')

# #PURCHASER DATA
# @app.route('/purchaser_data/', methods=['POST', 'GET'])
# def purchaser_data():
#     if request.method == 'POST':
#         #Get form data
#         indent_id = request.form['indentId']
#         date_time = request.form['dateTime']
         
      
#         print("value of indent id is:",indent_id)
#         print("value of datatime is :",date_time)

#         #Get table data from JSON string in form data
#         purchaser_data_array = request.form.get('purchaserData')
#         purchaser_data_array = json.loads(purchaser_data_array) if purchaser_data_array else []
        
        
#         print("value of purchaser data array is:",purchaser_data_array)

#         #Iterate through the array and update only the items with edited status
#         for purchaser_data in purchaser_data_array:
#             print("inside for loop values of purhcaser data:",purchaser_data)
#             #status = purchaser_data['status']
#             #if status != 'Indent Created' : #Check if the status is edited
#             print("inside the if block of status!=In....")
#             item_id = purchaser_data['itemId']
#             print("value of item id is:",item_id)
#             print("value of status is inside if block:",purchaser_data['status'])
#             print("value of remark is:",purchaser_data['remark'])
#             #update status in collection_indent for the specific item
#             collection_indent.update_one({'itemId': item_id},{'$set': {'status':  purchaser_data['status']}})
#             #update remark in collection_indent for the specific item
#             collection_indent.update_one({'itemId': item_id},{'$set': {'remark':  purchaser_data['remark']}})

#         #Insert data into collection_purchaser
#         for purchaser_data in purchaser_data_array:
#             collection_purchaser.insert_one(purchaser_data)

#         #Return a JSON response indicating success
#         return list(['Status:','data received and stored successfully'])

#     data = collection_indent.find({'status': 'Indent Created'})
#     data_purchaser=collection_purchaser.find({'status':''}) 
#     print("value of purchaser_data is:",data_purchaser)
#     return render_template('purchaser_data.html', data=data,data_purchaser=data_purchaser, uuid=uuid, datetime=datetime)

# #SHOW DATA INCOMING
# @app.route('/show_indent_data/', methods=['GET','POST'])
# def show_indent_data():
#     with open('/home/trumen1/Aakas/python/templates/header_names_incoming.json', 'r') as f:
#         headers = json.load(f)

#     data = list(collection_indent.find({}))  # Convert the cursor to a list
#     print(data)
#     for item in data:
        
#         extra_fields = item.get('extra_fields', {})
#         print("values of extra fields are:",extra_fields)
#         for field_name, field_value in extra_fields.items():
#             print("inside the for loop of extra fields")
#             if field_name not in headers:
#                 print("inside the if block if name not in headers:",field_name,"field value is:",field_value)
#                 headers.append(field_name)
#             if field_name not in item:
#                 print("inside the if block  if field name not in item")
#                 collection_indent.update_one({'_id': item['_id']}, {'$set': {field_name: field_value}})
     
#     print("values of all data is:",data)
#     return render_template('show_indent_data.html', data=data, headers=headers ,extra_fields=extra_fields)

# #EDIT DATA Indent 
# @app.route('/edit_data_indent/<itemId>', methods=['GET','POST'])
# def edit_data_indent(itemId):
#     if request.method == 'POST':
#         #Retrieve the existing data by itemId
#         existing_data = collection_indent.find_one({'_id': ObjectId(itemId)})
#         print("value of request form:",request.form)
        
#         print("value of existing data:",existing_data)
#         #Get updated data from the form
        

#         updated_data = {
#             'itemId': request.form['itemId'],
#             'mfrCode': request.form['mfrCode'],
#             'itemDesc':request.form['itemDesc'],
#             'qty':request.form['qty'],
#             'rate':request.form['rate'],
#             'amount':request.form['amount']             
#         }

#         #print("value of data changed key:", key)
#         #print("value of request form is:", request.form[key])
#         print("value of updated data:",updated_data)
#         # #Update the extra fields from the form data
#         #for key in request.form:
#         #if key not in['mfrCode', 'itemDesc', 'qty', 'rate', 'amount', 'itemId']:
#         #updated_data['extra_fields'][key] = request.form[key]

#         #Check if the list exists for the current ID, if not create it
#         if 'edit_history' not in existing_data:
#             print("inside if block of edit_history")
#             collection_indent.update_one({'_id': ObjectId(itemId)}, {'$set': {'edit_history': []}})

#         #Iterate the field and find the actual edited field
#         edited_field=None
#         for key in request.form:
#             print("inside the for loop",key)
#             if key != 'itemId':
#                 print("value of itemId is:",itemId)
#                 print("inside for loop", key)
#                 if existing_data.get(key) != request.form[key]:
#                     edited_field = key
#                     print("value of key inside 2nd if:",key)
#                     print("inside if of edited field:", edited_field)
#                     break
        
#         if edited_field:
#              edit_object = {
#                 'field_name':edited_field,
#                 'date_of_change': datetime.now().strftime("%d-%m-%y"),
#                 'time_of_change': datetime.now().time().strftime("%H:%M:%S"),
#                 'user_name': '',  # Replace with actual user name
#                 'old_value': existing_data.get(key),
#                 'new_value': request.form[edited_field]
#              }
#              print("value of edit object is:",edit_object)
#              collection_indent.update_one({'_id': ObjectId(itemId)}, {'$push': {'edit_history': edit_object}})
#         collection_indent.update_one({'_id': ObjectId(itemId)}, {'$set': updated_data})

#         return redirect(url_for('show_indent_data'))

#     #Handle the GET request to render the edit form
#     data = collection_indent.find_one({'_id': ObjectId(itemId)})
#     return render_template('edit_data_indent.html',  data=data, itemId=itemId)

# #DELETE DATA Indent  
# @app.route('/delete_indent_data/<itemId>', methods=['GET','POST'])
# def delete_indent_data(itemId):
#     print('>>>>', itemId)
#     if request.method == 'GET':
#         print('>>>>', itemId)
#         #Delete data from MongoDB
#         collection_indent.delete_one({'_id': ObjectId(itemId)})
#         print('>>>>', itemId)
#     return redirect(url_for('show_indent_data'))

# #STORE DATA 
# @app.route('/store_data/',methods=['GET','POST'])
# def store_data():
#     if request.method=='POST':
#         #Access arrays as lists
#         inward_Id=request.form['inwardId']
#         date_time=request.form['dateTime']
#         indent_Id=request.form['indentId']
#         poNumber_list=[int(poNumber) for poNumber in request.form.getlist('poNumber[]')]
#         itemNumber_list=[int(itemNumber) for itemNumber in request.form.getlist('itemNumber[]')]
#         qtys_list = [int(qty) for qty in request.form.getlist('qty[]')]
#         rates_list = [float(rate) for rate in request.form.getlist('rate[]')]
#         total_amount=request.form['amount']
#         status=[int(status) for status in request.form.getlist('status[]')]
        
#         print("values of requset.form is:",request.form) 
#         print("values  of request.form.items() is:",request.form.items()) 
#         print("value of qtys list is:",qtys_list)

#         #Create documents for each indent
#         indent_data_list = []
#         for i in range(len(qtys_list)):
#             print("inside the for loop of indent data")
#             total_amount = qtys_list[i] * rates_list[i]

#             #Create an indent_data dictionary
#             indent_data = {
#                 'inwardId':inward_Id,
#                 'dateTime':date_time,
#                  'indentId':indent_Id,
#                  'poNumber':poNumber_list[i],
#                  'itemNumber':itemNumber_list[i],                
#                  'qty': qtys_list[i],
#                  'rate': rates_list[i],
#                  'amount': total_amount,
#                  'status':status[i]
#                 #'extra_fields' : extra_fields #Directly assign the extra_fields dictionary
#             }
#             print("data type of qty is:",type(qtys_list[i]))
#             print("data type of rate is:",type(rates_list[i]))
#             print("data type of total_amount is:",type(total_amount))
#             indent_data_list.append(indent_data)
#             collection_inward.insert_one(indent_data)

#         #Print the values of indent data and extra fields
#         print("values of indent data list:", indent_data_list)
#         return  list(['data received and stored successfully'])
#     data=collection_purchaser.find()       
#     return render_template('store_data.html',uuid=uuid,datetime=datetime ,data=data)

# #SEND DATA TO REQUESTED QUERY  
# @app.route('/get_indent_data', methods=['POST'])
# def get_indent_data():
#     selected_po_number = request.form.get('po_number')

#     #Fetch data from the database based on the selected PO number
#     data = collection_purchaser.find({'poNumber': int(selected_po_number)})

#     #Convert data to a list of dictionaries
#     indent_data = list(data)

#     #Return the data as JSON
#     return jsonify(indent_data)




# #INWARD DATA INFORMATION

# #ADD INWARD DATA
# @app.route('/inward_form/', methods=['GET', 'POST'])
# def inward_form():
#     if request.method == 'POST':
#         print("inside the if of form.request")
#         inward_vendor = request.form['inward_vendor']
#         order_codes = request.form.getlist('order_code[]')
#         qtys = request.form.getlist('qty[]')
#         item_descrs = request.form.getlist('item_descr[]')

#         print("value of reques.form is:",request.form)

# #Find the corresponding indent data
#         indent_data = collection_indent.find_one({'order_codes': order_codes})
#         print("value of indent data:",indent_data)
#         status=None
#         if indent_data:
#             indent_qty = indent_data.get('qtys', [])
#             indent_item_descr = indent_data.get('item_descrs', [])
            
#             print("Length of qtys:", len(qtys))
#             print("Length of indent_qty:", len(indent_qty))
#             print("Length of item_descrs:", len(item_descrs))
#             print("Length of indent_item_descr:", len(indent_item_descr))
#             print("value of indent_qtys:",indent_qty)
#             print("value of indent_item_descr:",indent_item_descr)
#             print("value of qtys:",qtys)
#             print("value of item_descr:",item_descrs)
# #Ensure both lists have the same length
#             if  len(qtys) == len(indent_qty) and len(item_descrs) == len(indent_item_descr):
#                 print("inside the if block")
#                 print("value of list qtys:",list(map(int,qtys)))
#                 print("value of list item_descrs:",list(map(str, item_descrs)))
#                 if list(map(int, qtys)) == indent_qty and list(map(str, item_descrs)) == indent_item_descr:
#                    print("fully satisfied")
#                    status = 'fully satisfied'
#                 elif all(int(qty) <= indent_qty[i] for i, qty in enumerate(qtys)) and all(item in       indent_item_descr for item in map(str, item_descrs)):
#                     print("partially satisfied")
#                     status = 'partially satisfied'
#                 elif all(int(qty) >= indent_qty[i] for i, qty in enumerate(qtys)) and all(item in indent_item_descr for item in map(str, item_descrs)):
#                     print("greater than indent")
#                     status = 'quantity is greater than indent'
#                 else:
#                     print("pending")
#                     status = 'pending'

#             else:
#                 print("Lists have different lengths")
#                 status = 'lists have different lengths'
#         else:
#             status = 'components out of indent'
# #Store in the inward collection
#         inward_data = {
#             'inward_vendor': inward_vendor,
#             'inward_date': datetime.now().strftime('%Y-%m-%d'),
#             'inward_time': datetime.now().strftime('%H:%M:%S'),
#             'item_descr': item_descrs,
#             'order_code': order_codes,
#             'qty': qtys,
#             'status': status
#         }
#         print("value  of inward data is:",inward_data)
#         inward_result = collection_inward.insert_one(inward_data)
#         print("value of inward_result is:",inward_result)
#         return render_template('home_page.html')
        
        
#     return  render_template('inward_form.html')

# #SHOW INWARD DATA
# @app.route('/ /', methods=['GET'])
# def show_inward_data():
#     with open('/home/trumen1/Aakas/python/templates/inward_showData_headers.json', 'r') as f:
#         headers = json.load(f)

#     data = list(collection_inward.find({}))  # Convert the cursor to a list
#     print(data)         
#     return render_template('show_inward_data.html', data=data, headers=headers)

# #OUTWARD DATA INFORMATION
# #ADD OUTWARD DATA
# @app.route('/outward_form/',methods=['GET','POST'])
# def outward_form():
#     print("inside the outward_form function")
#     if request.method=='POST':
#         recipient_name=request.form['recipient_name']
#         item_descrs=request.form.getlist('item_descr[]')
#         qtys=request.form.getlist('qty[]')
#         print("value of request.form",request.form)
#         inward_data=collection_inward.find_one({'item_descr':item_descrs})
#         print("value of inward data is:",inward_data)
#         if inward_data:
#             inward_data_descrs=inward_data.get('item_descr',[])
#             print("value of outward form item__descrs:",item_descrs)
#             print("value of indent data for item_descrs:",inward_data_descrs)
#             print("value of  inward_data_descrs is:",list(map(str,inward_data_descrs))) 
#             if list(map(str,inward_data_descrs)) == item_descrs:
# #Store in the outward collection
#                     outward_data={
#                         'person_id':'',
#                         'recipient_name':recipient_name,
#                         'date':datetime.now().strftime('%Y-%m-%d'),
#                         'time':datetime.now().strftime('%H:%M:%S'),
#                         'item_descr':item_descrs,
#                         'qty':qtys
                        
#                     }
#                     print("value of outword_data  is:",outward_data)
#             out_data=collection_outward.insert_one(outward_data)
#             print("values of outword data:",out_data)
#         else:
#             print("Item does not exists in the store.....please wait")
#         return redirect(url_for('home_page'))
        
#     return render_template('outward_form.html')

# #SHOW OUTWARD DATA 
# @app.route('/ /', methods=['GET'])
# def show_outword_data():
#     with open('/home/trumen1/Aakas/python/templates/outward_showData_headers.json', 'r') as f:
#         headers = json.load(f)

#     data = list(collection_outward.find({}))  # Convert the cursor to a list
#     print(data)
#     print("values of headers is:",headers)  
#     return render_template('show_outword_data.html', data=data, headers=headers )

# #-- -- -- -- -- -- -- -- -- -- -- -- -- x -- -- -- -- -- -- -- -- -- -- -- -- --

# # #ADD OUTGOING DATA
# #def generate_form_html_outgoing(form_add_outgoing_data):
# #form_html_outgoing = '<form method="POST" action="/add_data_outgoing">'
# #for field in form_add_outgoing_data['fields']:
# #form_html_outgoing += f '<label for="{field["name"]}">{field["label"]}</label>'
# #form_html_outgoing += f '<input type="{field["type"]}" id="{field["name"]}" name="{field["name"]}"  required><br>'
# #form_html_outgoing += '<div id="extra_fields_container"><button type="button" onclick="addExtraFieldOutgoing()">Add Extra Field</button> </div>'
# #form_html_outgoing += '<button type="submit">Add Data</button>' '</form>'
# #return form_html_outgoing

# #f = open('/home/trumen1/Aakas/python/templates/outgoing_data_json_form.json')

# #form_add_outgoing_data = json.load(f)
# #@app.route('/add_data_outgoing/', methods =['POST', 'GET'])
# #def add_data_outgoing():
# #if request.method == 'POST':
# # #Collect data from extra fields
# #extra_fields = {}
# #for field_name, field_value in request.form.items():
# #if field_name.startswith('extra_field_') :
# #extra_fields[field_name.replace('extra_field_', '')] = field_value
# # #Get data from the form fields
# #date = request.form['date']
# #item_component = request.form['item_component']
# #quantity = request.form['quantity']
# #element_part_number = request.form['element_part_number']
# #manufacturing_part_number = request.form['manufacturing_part_number']

# # #Check if the record already exists
# #existing_record = collection_inward.find_one({'date' : date, 'item_component' : item_component, 'quantity' : quantity, 'element_part_number' : element_part_number, 'manufacturing_part_number' : manufacturing_part_number})

# #if existing_record:
# # #Update existing record with new extra fields data
# #for key, value in extra_fields.items():
# #existing_record[key] = value
# #collection_inward.update_one({'_id' : existing_record['_id']}, {'$set' : existing_record})
# #else:
# # #Insert data into MongoDB
# #data_entry = {
# #'date' : date,
# #'item_component' : item_component,
# #'quantity' : quantity,
# #'element_part_number' : element_part_number,
# #'manufacturing_part_number' : manufacturing_part_number,
# #'extra_fields' : extra_fields #Store extra fields in a dictionary
# #}
# #collection_inward.insert_one(data_entry)
# #print(data_entry)
# #print(extra_fields)
# #return redirect(url_for('outgoing_register'))

# #form_html_outgoing = generate_form_html_outgoing(form_add_outgoing_data)
# #return render_template('add_data_outgoing.html', form_html_outgoing = form_html_outgoing)

# # #SHOW OUTGOING DATA
# #@app.route('/show_data_outgoing/', methods =['GET'])
# #def show_data_outgoing():
# #with open('/home/trumen1/Aakas/python/templates/header_names_outgoing.json', 'r') as f:
# #headers = json.load(f)

# #data = list(collection_inward.find({})) #Convert the cursor to a list
# #print(data)
# #for item in data:
# #extra_fields = item.get('extra_fields', {})
# #for field_name, field_value in extra_fields.items():
# #if field_name not in headers:
# #headers.append(field_name)
# #if field_name not in item:
# #collection_inward.update_one({'_id' : item['_id']}, {'$set' : {field_name : field_value}})

# #return render_template('show_data_outgoing.html', data = data, headers = headers, extra_fields = extra_fields)

# # #EDIT OUTGOING DATA
# #@app.route('/edit_data_outgoing/<item_id>', methods =['GET', 'POST'])
# #def edit_data_outgoing(item_id):
# #if request.method == 'POST':
# # #Retrieve the existing data by item_id
# #existing_data = collection_inward.find_one({'_id' : ObjectId(item_id)})
# #print("value of request form:", request.form)

# #print("value of existing data:", existing_data)
# # #Get updated data from the form
# #updated_data = {
# #'date' : request.form['date'],
# #'item_component' : request.form['item_component'],
# #'quantity' : request.form['quantity'],
# #'element_part_number' : request.form['element_part_number'],
# #'manufacturing_part_number' : request.form['manufacturing_part_number'],
# #'extra_fields' : {} #Initialize an empty dictionary for extra fields
# #}
# # #print("value of data changed key:", key)
# # #print("value of request form is:", request.form[key])
# #print("value of updated data:", updated_data)
# # #Update the extra fields from the form data
# #for key in request.form:
# #if key not in['date', 'item_component', 'quantity', 'element_part_number', 'manufacturing_part_number', 'item_id']:
# #print("edit data of extra fields", request.form[key])
# #updated_data['extra_fields'][key] = request.form[key]

# # #Check if the list exists for the current ID, if not create it
# #if 'edit_history' not in existing_data:
# #print("inside if block of edit_history")
# #collection_inward.update_one({'_id' : ObjectId(item_id)}, {'$set' : {'edit_history' : []}})

# # #Iterate the field and find the actual edited field
# #edited_field = None
# #for key in request.form:
# #print("inside the for loop", key)
# #if key != 'item_id':
# #print("inside for loop", key)
# #if existing_data.get(key) != request.form[key]:
# #edited_field = key
# #print("value of key inside 2nd if:", key)
# #print("inside if of edited field:", edited_field)
# #break

# #if edited_field:
# #edit_object = {
# #'field_name' : edited_field,
# #'date_of_change' : datetime.now().strftime("%d-%m-%y"),
# #'time_of_change' : datetime.now().time().strftime("%H:%M:%S"),
# #'user_name' : '', #Replace with actual user name
# #'old_value' : existing_data.get(key),
# #'new_value' : request.form[edited_field]
# #}
# #print("value of edit object is:", edit_object)
# #collection_inward.update_one({'_id' : ObjectId(item_id)}, {'$push' : {'edit_history' : edit_object}})

# # #Update data in MongoDB
# #collection_inward.update_one({'_id' : ObjectId(item_id)}, {'$set' : updated_data})

# #return redirect(url_for('show_data_outgoing'))

# # #Handle the GET request to render the edit form
# #data = collection_inward.find_one({'_id' : ObjectId(item_id)})
# #return render_template('edit_data_outgoing.html', data = data, item_id = item_id)

# # #OUTGOING DELETE COMPONENT
# #@app.route('/delete_data_outgoing/<item_id>', methods =['GET', 'POST'])
# #def delete_data_outgoing(item_id):
# #print('>>>>', item_id)
# #if request.method == 'GET':
# #print('>>>>', item_id)
# # #Delete data from MongoDB
# #collection_inward.delete_one({'_id' : ObjectId(item_id)})
# #print('>>>>', item_id)
# # #return render_template('show_data_outgoing.html', data = data)
# #return redirect(url_for('show_data_outgoing'))
 
if __name__ == '__main__':
    app.run(debug=True, port=5001)