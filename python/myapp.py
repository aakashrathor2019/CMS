from flask import Flask, render_template, request, redirect, url_for,jsonify,send_from_directory,session
from pymongo import MongoClient
from bson import ObjectId
import json
import pymongo
import math
from flask_session import Session
from uuid import uuid4
from datetime import datetime 
from flask import make_response
from functools import wraps
from flask import send_file
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required,current_user
import secrets
from bson import json_util
import pdb 
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
 
app.secret_key  =   os.genenv('SECERT_KEY')
 
# API key: BSWKGKLS12NHQMLY
# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['aakashdb']         # DB name
collection_indent= db['indent']  # Table Name
collection_inward = db['inward']  #Table Name
collection_outward=db['outward']   #Table Name
collection_purchaser=db['purchaser']
collection_last_ids=db['ids']
collection_user=db['user']
collection_bill=db['billInfo']
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 

# Flask-Login Configuration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User model
class User(UserMixin):
    def __init__(self,user_id, user_type, password):
        self.id=user_id
        self.user_type = user_type
        self.password = password
        
        
    def get_id(self):
        return str(self.id)  # Convert to string if necessary

@login_manager.user_loader
def load_user(user_id):
    print('value of user_type  is-->>',user_id)
    user_data =collection_user.find_one({'user_type': user_id})
    if user_data:
        print('value of user id find_out from database-->>',user_data['user_type'])
        return User(user_id=user_data['user_type'],user_type=user_data['user_type'], password=user_data['password'])
    return None
 
 
            #LOGIN MODULE         
# Route for user login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print('inside the login')
        user_type = request.form.get('user_type')
        email = request.form.get('email')
        password = request.form.get('password')
        
        print('value of user type->>>', user_type)
        print('value of email->>>', email)
        print('value of password->>>', password)

        user=collection_user.find_one({'user_type':user_type,'email':email,'password':password})
        print('value of user is->>>',user)
        if user:
                user_obj=load_user(user_type)
                print('value of user_obj is-->>',user_obj)
                session['user_email'] =email
                login_user(user_obj)
                return redirect(url_for('dashboard'))
 
        return render_template('login.html', error='Invalid credentials,plz enter valid id or password')
    print('direct out of the if condition')
    users=collection_user.distinct('user_type')    
    
    print('value of all users is-->>',users)
    return render_template('login.html', users=users)

#Dashboard Route
@app.route('/dashboard')
@login_required
def dashboard():    
    if current_user.is_authenticated:
        user_type=current_user.user_type
        print('value user_type is-->>',user_type)
        if user_type:
            print('inside the if condition of user_type')
            if user_type == 'admin':
                print('inside the admin user')
                return redirect(url_for('home_page'))
            elif user_type == 'indenter':
                print('inside the indenter user')
                return redirect(url_for('indenter_dashboard'))
            elif user_type == 'purchaser':
                print('inside the purchaser user')
                return redirect(url_for('purchaser_dashboard'))
            elif user_type == 'store':
                print('inside the store user')
                return redirect(url_for('store_dashboard'))
            else:
                print('module not found')
                return redirect(url_for('login'))
         
        #Handle if user not found
        return redirect(url_for('login'))
 

#Registration/SignUp Page
@app.route('/signup_page',methods=['GET','POST'])
def signup_page():
   print('inside the signup function')
   if request.method=='POST':
        user_type=request.form['user_type']
        user_name=request.form['email']
        password=request.form['password']
        print('value of email->>',user_name)
        print('value of password->>>',password)
        data={
                'user_type':user_type,
                'email':user_name,
                'password':password
            }
        print('value of user name after data json->>',request.form['email'])
        find_data=collection_user.find_one({'email':request.form['email']})
        print('value of find data is->>>',find_data)
        
        if find_data:
            return render_template('signup_page.html',error='email already exists,try another email')
        else:
            print('value of data:',data)
            collection_user.insert_one(data)
            return redirect(url_for('login'))
                 
   return render_template('signup_page.html')


# Logout Session
@app.route("/logout")
@login_required
def logout():
    #Clear session data for current user 
    session.clear()
    logout_user()
    response = make_response(redirect(url_for("login")))
    #For History Remove 
    # response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    # response.headers['Pragma'] = 'no-cache'
    # response.headers['Expires'] = '-1'
    return response


#Forget Password
@app.route('/forget_password',methods=['GET','POST'])
def forget_password():
    if request.method=='POST':
        email=request.form['email']
        password=request.form['password']
        
        #Find email id in the database
        user=collection_user.find_one({'email':email})
        
        print('value of eamil inside the forget password->>',email)
        print('value of password is->>',password)
        print('value of user ->>',user)
        if user:
            collection_user.update_one({'email':email},{'$set':{'password':password}})
            return redirect(url_for('login'))
        else:
            return  render_template('forget_password.html',error='Email not exists')
        
    return render_template('forget_password.html')

 
#Route for home page/admin page
@app.route('/home_page')
@login_required
def home_page():
    print('inside the home function')
    if current_user.is_authenticated and current_user.user_type== 'admin':
        user_data =collection_user.find_one({'user_type':'admin'}) 
        print('inside the home function')
        response = make_response(render_template('home_page.html', user_email=session['user_email'],user_data=user_data ))
        return response
    return redirect(url_for('login')) 


# Route for indenter dashboard           
@app.route('/indenter_dashboard')
@login_required
def indenter_dashboard():
    print('inside the indenter_dashboard function')
    if current_user.is_authenticated and current_user.user_type== 'indenter':
        user_data =collection_user.find_one({'user_type':'indenter'}) 
        print('inside the indenter dashboard function')
        response = make_response(render_template('indenter_dashboard.html', user_email=session['user_email'],user_data=user_data))
        return response
    return redirect(url_for('login')) 


# Route for purchaser dashboard
@app.route('/purchaser_dashboard')
@login_required
def purchaser_dashboard():
    print('inside the purchaser_dashboard function')
    if current_user.is_authenticated and current_user.user_type== 'purchaser':
        user_data =collection_user.find_one({'user_type':'purchaser'}) 
        print('inside the if condition of purchaser dashboard function')
        response = make_response(render_template('purchaser_dashboard.html', user_email=session['user_email'],user_data=user_data))
        return response
    return redirect(url_for('login')) 

# Route for store dashboard
@app.route('/store_dashboard')
@login_required
def store_dashboard():
    print('inside the  store_dashboard function')
    if current_user.is_authenticated and current_user.user_type== 'store':
        user_data =collection_user.find_one({'user_type':'store'}) 
        print('inside the store_dashboard function')
        response = make_response(render_template('store_dashboard.html', user_email=session['user_email'],user_data=user_data))
        return response
    return redirect(url_for('login')) 
    
                            #INDENT DATA INFORMATION

#ADD INDENT DATA
@app.route('/indent_form/',methods=['GET','POST'])
@login_required
def indent_form():
    print('inside the indent form')
    if request.method=='POST':
        # Access arrays as lists
        indentId=request.form['indentId']
        dateTime=request.form['dateTime']
        item_id_list = request.form.getlist('itemId[]')
        item_name_list=request.form.getlist('itemName[]')
        manufacturer_codes_list = request.form.getlist('mfrCode[]')
        item_descr_list=request.form.getlist('itemDesc[]')
        qtys_list = [int(qty) for qty in request.form.getlist('qty[]')]
        rates_list = [float(rate) for rate in request.form.getlist('rate[]')]
    
    
        print("values of requset.form is:",request.form)
         
        print("values  of request.form.items() is:",request.form.items()) 
        
        print("value of item_descr_list:",item_descr_list)
        print("value of qtys list is:",qtys_list)
         
        # Create documents for each indent
        indent_data_list = []
        for i in range(len(item_descr_list)):
            print("inside the for loop of indent data")
            total_amount = qtys_list[i] * rates_list[i]

            # Create an indent_data dictionary
            indent_data = {
                'indentId':indentId,
                'dateTime':dateTime,
                'itemId':item_id_list[i],
                'itemName':item_name_list[i],
                'mfrCode': manufacturer_codes_list[i],
                'itemDesc': item_descr_list[i],
                'qty': qtys_list[i],
                'rate': rates_list[i],
                'total_amount': total_amount,
                'status':'Indent Created'
                # 'extra_fields': extra_fields # Directly assign the extra_fields dictionary
            }
            itemId=item_descr_list[i]
            print("value of itemId is:",itemId)
            print("data type of qty is:",type(qtys_list[i]))
            print("data type of rate is:",type(rates_list[i]))
            print("data type of total_amount is:",type(total_amount))
            indent_data_list.append(indent_data)
            collection_indent.insert_one(indent_data)
        
        return redirect(url_for('indenter_dashboard'))
 
 
    # Retrieve last indent and item IDs from the database
    indent_id_doc= collection_last_ids.find_one({'INDCTRVAL':{'$exists':True}})
    item_id_doc= collection_last_ids.find_one({'ITEMCTRVAL':{'$exists':True}})
    print('values of indent_id_doc are:',indent_id_doc)
    print('values of item_id_doc is:->>',item_id_doc)
    
    #CONDITION FOR INDENT ID DOC
    if indent_id_doc:
        indent_id=int(indent_id_doc.get('INDCTRVAL',0))
        indent_id +=1
      
    else:
        indent_id=1
        
    #CONDITION FOR ITEM ID DOC
    if item_id_doc:
        item_id=int(item_id_doc.get('ITEMCTRVAL',0))
        
    else:
        item_id=1
    print('value of indent_id is->>>',indent_id)
    print('value of item_id->>>',item_id)
     
    indCtrVal='IND'+str(indent_id).zfill(8) 
    itemCtrVal='ITEM'+str(item_id).zfill(8) 
    
    print('value of indCtrVal is->>>',indCtrVal)
    print('value opf itemCtrVal is->>>',itemCtrVal)
    return render_template('indent_form.html',indCtrVal=indCtrVal,itemCtrVal=itemCtrVal,datetime=datetime,itemCounter=item_id)


#STORE INDENT DATA IN DB
@app.route('/store_indent_data', methods=['GET','POST'])
def store_indent_data():
          #Assume the cons is global value
    if request.method=='POST':
        data = request.get_json()   
        # Access data elements as needed
        # Modify this part based on your actual data structure
        indentId = data.get('indentId')
        dateTime = data.get('dateTime')
        indentDataArray = data.get('indentData')
         
        print("value of indentId is:",indentId)
        print("value of datatime is:",dateTime)
        print('value of indentdataarray is:',indentDataArray)
        # Split the string by '/' and get the last part
        indent_integer_part = indentId.split('IND')[-1]
        # Remove leading zeros
        indentId_without_zeros = str(int(indent_integer_part))
        print('value of indent_integer_part->>',indent_integer_part)
        print('value of integer part zeroes is:',indentId_without_zeros)
        # Update the last used INDCTRVAL in the MongoDB collection
        collection_last_ids.update_one({'INDCTRVAL': {'$exists': True}}, {'$set': {'INDCTRVAL': str(indentId_without_zeros)}}, upsert=True)
        
        # Insert data into the collection_indent collection
        for indentData in indentDataArray:
            item_id=indentData['itemId']
            collection_indent.insert_one(indentData)
            print("value of indent Data is:",indentData)
            item_integer_part=item_id.split('ITEM')[-1]
            print('value of item_integer_part->>',item_integer_part)
            itemId_without_zeros = str(int(item_integer_part))       
            print('value of item  part without zeroes:',itemId_without_zeros)
            # Update the last used ITEMCTRVAL in the MongoDB collection
            collection_last_ids.update_one({'ITEMCTRVAL': {'$exists': True}}, {'$set': {'ITEMCTRVAL': str(itemId_without_zeros)}}, upsert=True)

        return  redirect(url_for('indenter_dashboard'))
    return render_template('indent_form.html')
 
 
#DRAFT DATA
@app.route('/draft_data', methods=['GET','POST'])
def draft_data():
    if request.method=='POST':
        
        data = request.get_json()   
        # Access data elements as needed
        # Modify this part based on your actual data structure
         
        draftDataArray = data.get('draftData')

        
        print('value of draftdataarray is:',draftDataArray)
        # Insert data into the collection_indent collection
        for draftData in draftDataArray:
            item_id=draftData['itemId']
            #update status in collection_indent and collection_purchaser for the specific item
            collection_indent.update_one(
                {'itemId': item_id},
                {
                    '$set': {
                        'status': draftData['status'],
                        'remark': draftData['remark'],
                        'lastUpdate':draftData['lastUpdate']
                    }
                },
                upsert=False
            )
            collection_purchaser.update_one(
                {'itemId': item_id},
                {
                    '$set': {
                        'status': draftData['status'],
                        'remark': draftData['remark'],
                        'lastUpdate':draftData['lastUpdate']
                    }
                },
                upsert=False
            )
            
            
            print("value of indent Data is:",draftData)

        return redirect(url_for('purchaser_dashboard'))
    return render_template('purchaser_data.html')

#Update Indenter Status with remark by Purchaser 
@app.route('/update_indenter', methods=['GET','POST'])
def update_indenter():
    if request.method=='POST':   
        # Get table data from JSON string in form data
        purchaser_data_array = request.form.get('purchaserData')
        purchaser_data_array = json.loads(purchaser_data_array) if purchaser_data_array else []       
        print('value of purchaser data is:',purchaser_data_array)
        for purchaserData in purchaser_data_array:
            item_id=purchaserData['itemId']
            collection_indent.update_one(
            {'itemId': item_id},
            {
                '$set': {
                    'status': purchaserData['status'],
                    'remark': purchaserData['remark'],
                    'lastUpdate':datetime
                }
            },
            upsert=False
            )
            collection_purchaser.insert_one(purchaserData)
            print('value of purchaser data is:',purchaserData)
         
        return redirect(url_for('purchaser_data'))
 
#PURCHASER DATA
@app.route('/purchaser_data/', methods=['POST', 'GET'])
@login_required
def purchaser_data():
 
    if request.method == 'POST':
        print('inside the purchaser data fn')
        po_number = request.form['poNumber']
        date_time = request.form['dateTime']

        print("value of po number is:", po_number)
        print("value of datetime is:", date_time)
        # Split the string by '/' and get the last part
        integer_part = po_number.split('/')[-1]

        # Remove leading zeros
        integer_part_without_zeros = str(int(integer_part))
        print('value of integer part zeroes is:',integer_part_without_zeros)
        purchaser_data_array = request.form.get('purchaserData')
        purchaser_data_array = json.loads(purchaser_data_array) if purchaser_data_array else []

        print("value of purchaser data array is:", purchaser_data_array)

        for purchaser_data in purchaser_data_array:
            item_id = purchaser_data['itemId']
            po_number = purchaser_data['poNumber']
            print("value of item id is:", item_id)
            print("value of status is inside if block:", purchaser_data['status'])
            print("value of remark is:", purchaser_data['remark'])
            print('value of po number is:', po_number)

            collection_indent.update_one({'itemId': item_id}, {'$set': {'status': purchaser_data['status'], 'remark': purchaser_data['remark']}})
            
            #Update PO_NUMBER In DB
            collection_purchaser.update_one({'itemId': item_id}, {'$set': {'poNumber':po_number}})

        # Update the last used POCTR in the MongoDB collection
        collection_last_ids.update_one({'POCTRVAL': {'$exists': True}}, {'$set': {'POCTRVAL': str(integer_part_without_zeros)}}, upsert=True)
        return redirect(url_for('purchaser_dashboard'))
    print('direct out from purchaser data fn')
    data = collection_indent.find({'status': 'Indent Created'})
    data_purchaser = collection_purchaser.find({'status':{'$ne':'Fully Satisfied'}})
     
    print('value of indent data is:', data)
    print("value of purchaser_data is:", data_purchaser)
    
    # Get the last used POCTR from the MongoDB collection
    po_number_doc = collection_last_ids.find_one({'POCTRVAL': {'$exists': True}})
    print('value of po_number_doc is->>',po_number_doc)
    if po_number_doc:
        po_number = int(po_number_doc.get('POCTRVAL', 0))
        po_number += 1
    else:
        po_number = 1  # Set a default value if there is no document
        
    

    print('value of po_number->>',po_number)

    poCtrVal = 'PO/TTPL/' + str(po_number).zfill(8)
    print('value of poCtrVal is->>',poCtrVal)
    return render_template('purchaser_data.html', data=data, data_purchaser=data_purchaser, poCtrVal=poCtrVal, datetime=datetime)


#SHOW DATA INDENT
@app.route('/show_indent_data/', methods=['GET', 'POST'])
@login_required
def show_indent_data():
    json_path = os.path.join(BASE_DIR, 'templates','header_names_indenter.json')
    with open(json_path, 'r') as f:
        headers = json.load(f)
    data= list(collection_indent.find({}))
    # Handle GET request (initial page load)
    return render_template('show_indent_data.html', data=data ,headers=headers)

#SHOW DATA  PURCHASER
@app.route('/show_purchaser_data/', methods=['GET', 'POST'])
@login_required
def show_purchaser_data():
    json_path = os.path.join(BASE_DIR, 'templates','header_names_purchaser.json')
    with open(json_path, 'r') as f:
        headers = json.load(f)
    data =list(collection_purchaser.find({}))
    # Handle GET request (initial page load)
    return render_template('show_purchaser_data.html', data=data,headers=headers)

#SHOW DATA  INWARD(STORE)
@app.route('/show_store_data/', methods=['GET', 'POST'])
@login_required
def show_store_data():
    json_path = os.path.join(BASE_DIR, 'templates', 'header_names_store.json',)
    with open(json_path, 'r') as f:
        headers = json.load(f)
    data=list(collection_inward.find({}))
    # Handle GET request (initial page load)
    return render_template('show_store_data.html',data=data,headers=headers)

#Show all data inside the table
@app.route('/show_bill_data/',methods=['GET','POST'])
@login_required
def show_bill_data():
    json_path = os.path.join(BASE_DIR, 'templates', 'header_names_billData.json')
    with open(json_path, 'r') as f:
        headers = json.load(f)
    data= list(collection_bill.find({}))
    print('value of all data send to show_bill_data-->',data)
    return render_template('show_bill_data.html',data=data ,headers=headers)


#INDENT DATA SHOW to Purchaser Users
@app.route('/indent_data_readPur/', methods=['GET', 'POST'])
@login_required
def indent_data_readPur():
    json_path = os.path.join(BASE_DIR, 'templates', 'header_names_indOther.json',)
    with open(json_path,  'r') as f:
        headers = json.load(f)
    data =list(collection_indent.find({}))
    return render_template('indent_data_readPur.html', data=data, headers=headers)

#INDENT DATA SHOW to Inward Users
@app.route('/indent_data_readStr/', methods=['GET', 'POST'])
@login_required
def indent_data_readStr():
    json_path = os.path.join(BASE_DIR, 'templates', 'header_names_indOther.json',)
    with open(json_path,  'r') as f:
        headers = json.load(f)
    data =list(collection_indent.find({}))
    return render_template('indent_data_readStr.html', data=data, headers=headers)
 

#PURCHASER DATA SHOW to Indenter
@app.route('/purchaser_data_readInd/', methods=['GET', 'POST'])
@login_required
def purchaser_data_readInd():
    json_path = os.path.join(BASE_DIR, 'templates', 'header_names_purOther.json',)
    with open(json_path,  'r') as f:
        headers = json.load(f)
    #Fetch data from database and send to client
    data = list(collection_purchaser.find({}))
    print('value of data is-->>',data)
    return render_template('purchaser_data_readInd.html', data=data, headers=headers)

#PURCHASER DATA SHOW to Inward
@app.route('/purchaser_data_readStr/', methods=['GET', 'POST'])
@login_required
def purchaser_data_readStr():
    json_path = os.path.join(BASE_DIR, 'templates', 'header_names_purOther.json',)
    with open(json_path,  'r') as f:
        headers = json.load(f)
    #Fetch data from database and send to client
    data = list(collection_purchaser.find({}))
    print('value of data is-->>',data)
    return render_template('purchaser_data_readStr.html', data=data, headers=headers)


#SHOW INWARD DATA to Indenter
@app.route('/store_data_readInd/', methods=['GET', 'POST'])
@login_required
def store_data_readInd():
    json_path = os.path.join(BASE_DIR, 'templates', 'header_names_strOther.json',)
    with open(json_path,  'r') as f:
        headers = json.load(f)
        
    data= list(collection_inward.find({}))
    print('value of find data is at the end point -->>',data)
    return render_template('store_data_readInd.html', data=data, headers=headers)

#SHOW INWARD DATA to Purchaser
@app.route('/store_data_readPur/', methods=['GET', 'POST'])
@login_required
def store_data_readPur():
    json_path = os.path.join(BASE_DIR, 'templates', 'header_names_strOther.json',)
    with open(json_path,  'r') as f:
        headers = json.load(f)
        
    data= list(collection_inward.find({}))
    print('value of find data is at the end point -->>',data)
    return render_template('store_data_readPur.html', data=data, headers=headers)

#SHOW BILL INFO to Indenter
@app.route('/bill_data_readInd/', methods=['GET', 'POST'])
@login_required
def bill_data_readInd():
    json_path = os.path.join(BASE_DIR, 'templates', 'header_names_billOther.json',)
    with open(json_path,  'r') as f:
        headers = json.load(f)
        
    data= list(collection_bill.find({}))
    print('value of find data is at the end point -->>',data)
    return render_template('bill_data_readInd.html', data=data, headers=headers)

#SHOW BILL INFO to Purchaser
@app.route('/bill_data_readPur/', methods=['GET', 'POST'])
@login_required
def bill_data_readPur():
    json_path = os.path.join(BASE_DIR, 'templates', 'header_names_billOther.json', )
    with open(json_path, 'r') as f:
        headers = json.load(f)
        
    data= list(collection_bill.find({}))
    print('value of find data is at the end point -->>',data)
    return render_template('bill_data_readPur.html', data=data, headers=headers)
 

#EDIT DATA INDENT 
@app.route('/edit_data_indent/<itemId>', methods=['GET','POST'])
@login_required
def edit_data_indent(itemId):
    if request.method == 'POST':
        # Retrieve the existing data by itemId
        existing_data = collection_indent.find_one({'itemId': itemId})
        print("value of request form:",request.form)
        # Get updated data from the form
       
        updated_data = {
            
            'itemName':request.form['itemName'],
            'itemDesc':request.form['itemDesc'],
            'qty':request.form['qty'],
            'rate': request.form['rate'],
            'amount':request.form['amount'],
            'status':request.form['status'],
            'remark':request.form['remark'],       
        }
        print('value of itemId is---------->>>>>>>>',itemId)
        print('value of status and remark :',updated_data['status'],updated_data['remark'])
       
        
        #print("value of data changed key:",key)
        #print("value of request form is:",request.form[key])
        print("value of updated data:",updated_data)
        # # Update the extra fields from the form data
        # for key in request.form:
        #     if key not in [ 'mfrCode','itemDesc','qty','rate','amount','itemId']:
        #         updated_data['extra_fields'][key] = request.form[key]


        # Check if the list exists for the current ID, if not create it
        if 'edit_history' not in existing_data:
            print("inside if block of edit_history")
            collection_indent.update_one({'itemId':itemId}, {'$set': {'edit_history': []}})
            
            
        # Iterate the fields and find the actual edited fields
        edited_fields = []

        for key in request.form:
            if key != 'itemId':
                print('value of key is->>',key)
                if existing_data.get(key) != request.form[key]:
                    print('value of key is->>',request.form[key])
                    edited_fields.append({
                        'field_name': key,
                        'date_of_change': datetime.today(),
                        'user_name': '',  # Replace with actual user name
                        'old_value': existing_data.get(key),
                        'new_value': request.form[key]
                    })
        print('value of edited fields are:',edited_fields)

        # Check if any field was edited
        if edited_fields:
            # Update the edit history with all edited fields
            collection_indent.update_one({'itemId': itemId}, {'$push': {'edit_history': {'$each': edited_fields}}})
        collection_indent.update_one({'itemId': itemId}, {'$set': updated_data})
        
        return redirect(url_for('show_indent_data'))

    # Handle the GET request to render the edit form
    data = collection_indent.find_one({'itemId': itemId})
    return render_template('edit_data_indent.html',  data=data, itemId=itemId)

#EDIT DATA PURCHASER 
@app.route('/edit_data_purchaser/<itemId>', methods=['GET','POST'])
@login_required
def edit_data_purchaser(itemId):
    if request.method == 'POST':
        # Retrieve the existing data by itemId
        existing_data = collection_purchaser.find_one({'itemId': itemId})
       
        print("value of request form:",request.form)
        print('value of item id is:-->>>>>',itemId)
        print("value of existing data:",existing_data)
        # Get updated data from the form
       
        updated_data = {
            'itemName':request.form['itemName'],
            'itemDesc':request.form['itemDesc'],
            'qty':request.form['qty'],
            'rate': request.form['rate'],
            'status':request.form['status'],
            'remark':request.form['remark'],       
            'amount':request.form['amount']
        }
        print('value of itemId is---------->>>>>>>>',itemId)
        print('value of status and remark :',updated_data['status'],updated_data['remark']) 
        #print("value of data changed key:",key)
        #print("value of request form is:",request.form[key])
        print("value of updated data:",updated_data)
        # # Update the extra fields from the form data
        # for key in request.form:
        #     if key not in [ 'mfrCode','itemDesc','qty','rate','amount','itemId']:
        #         updated_data['extra_fields'][key] = request.form[key]


        # Check if the list exists for the current ID, if not create it
        if 'edit_history' not in existing_data:
            print("inside if block of edit_history")
            collection_purchaser.update_one({'itemId':itemId}, {'$set': {'edit_history': []}})
            
            
        # Iterate the fields and find the actual edited fields
        edited_fields = []

        for key in request.form:
            if key != 'itemId':
                print('value of key is->>',key)
                if existing_data.get(key) != request.form[key]:
                    print('value of key is->>',request.form[key])
                    edited_fields.append({
                        'field_name': key,
                        'date_of_change': datetime.utcnow().strftime('%a %d %b %Y, %I:%M%p'),
                        'user_name': '',  # Replace with actual user name
                        'old_value': existing_data.get(key),
                        'new_value': request.form[key]
                    })
        print('value of edited fields are:',edited_fields)

        # Check if any field was edited
        if edited_fields:
            # Update the edit history with all edited fields
            collection_purchaser.update_one({'itemId': itemId}, {'$push': {'edit_history': {'$each': edited_fields}}})

        collection_purchaser.update_one({'itemId': itemId}, {'$set': updated_data})
        
        return redirect(url_for('show_purchaser_data'))

    # Handle the GET request to render the edit form
    data = collection_purchaser.find_one({'itemId': itemId})
    return render_template('edit_data_purchaser.html',  data=data, itemId=itemId)


#EDIT DATA INWARD(STORE) 
@app.route('/edit_data_store/<itemId>', methods=['GET','POST'])
@login_required
def edit_data_store(itemId):
    if request.method == 'POST':
        # Retrieve the existing data by itemId
        existing_data = collection_inward.find_one({'_id':ObjectId(itemId)})
        print("value of request form:",request.form)
        print('value of item id is:-->>>>>',itemId)
        print("value of existing data:",existing_data)
        # Get updated data from the form
       
        updated_data = {
            'itemName':request.form['itemName'],
            'itemDesc':request.form['itemDesc'],
            'qty':request.form['qty'],
            'status':request.form['status'],
            'remark':request.form['remark']                  
        }
        print('value of itemId is---------->>>>>>>>',itemId)
        print('value of status and remark :',updated_data['status'],updated_data['remark']) 
        #print("value of data changed key:",key)
        #print("value of request form is:",request.form[key])
        print("value of updated data:",updated_data)
 
        # Check if the list exists for the current ID, if not create it
        if 'edit_history' not in existing_data:
            print("inside if block of edit_history")
            collection_inward.update_one({'_id':ObjectId(itemId)}, {'$set': {'edit_history': []}})
            
            
# Iterate the fields and find the actual edited fields
        edited_fields = []

        for key in request.form:
            if key != 'itemId':
                print('value of key is->>',key)
                if existing_data.get(key) != request.form[key]:
                    print('value of key is->>',request.form[key])
                    edited_fields.append({
                        'field_name': key,
                        'date_of_change': datetime.utcnow().strftime('%a %d %b %Y, %I:%M%p'),
                        'user_name': '',  # Replace with actual user name
                        'old_value': existing_data.get(key),
                        'new_value': request.form[key]
                    })
        print('value of edited fields are:',edited_fields)

        # Check if any field was edited
        if edited_fields:
            # Update the edit history with all edited fields
            collection_inward.update_one({'_id':ObjectId(itemId)}, {'$push': {'edit_history': {'$each': edited_fields}}})
        collection_inward.update_one({'_id': ObjectId(itemId)}, {'$set': updated_data})
        
        return redirect(url_for('show_store_data'))

    # Handle the GET request to render the edit form
    data = collection_inward.find_one({'_id':ObjectId(itemId)})
    print('value of item id is-->>',itemId)
    return render_template('edit_data_store.html',  data=data, itemId=itemId)

#EDIT DATA  BILL INVOICE
@app.route('/edit_data_bill/<itemId>', methods=['GET','POST'])
@login_required
def edit_data_bill(itemId):
    if request.method == 'POST':
        # Retrieve the existing data by itemId
        existing_data = collection_bill.find_one({'_id': ObjectId(itemId)})
        print("value of request form:",request.form)
        print('value of item id is:-->>>>>',itemId)
        print("value of existing data:",existing_data)
        # Get updated data from the form       
        updated_data = {
            'venderName':request.form['venderName'],
            'itemName':request.form['itemName'],
            'itemDesc':request.form['itemDesc'],
            'qty':request.form['qty'],
            'rate': request.form['rate'],
            'amount':request.form['amount'],
            'status':request.form['status'],
            'remark':request.form['remark']      
           
        }
        print('value of itemId is---------->>>>>>>>',itemId)
        print('value of status and remark :',updated_data['status'],updated_data['remark']) 
        #print("value of data changed key:",key)
        #print("value of request form is:",request.form[key])
        print("value of updated data:",updated_data)
 
        # Check if the list exists for the current ID, if not create it
        if 'edit_history' not in existing_data:
            print("inside if block of edit_history")
            collection_bill.update_one({'_id': ObjectId(itemId)}, {'$set': {'edit_history': []}})
            
            
# Iterate the fields and find the actual edited fields
        edited_fields = []

        for key in request.form:
            if key != 'itemId':
                print('value of key is->>',key)
                if existing_data.get(key) != request.form[key]:
                    print('value of key is->>',request.form[key])
                    edited_fields.append({
                        'field_name': key,
                        'date_of_change': datetime.utcnow().strftime('%a %d %b %Y, %I:%M%p'),
                        'user_name': '',  # Replace with actual user name
                        'old_value': existing_data.get(key),
                        'new_value': request.form[key]
                    })
        print('value of edited fields are:',edited_fields)

        # Check if any field was edited
        if edited_fields:
            # Update the edit history with all edited fields
            collection_bill.update_one({'_id': ObjectId(itemId)}, {'$push': {'edit_history': {'$each': edited_fields}}})
        collection_bill.update_one({'_id': ObjectId(itemId)}, {'$set': updated_data})
        
        return redirect(url_for('show_store_data'))

    # Handle the GET request to render the edit form
    data = collection_bill.find_one({'_id': ObjectId(itemId)})
    return render_template('edit_data_bill.html',  data=data, itemId=itemId)

   
#DELETE DATA INDENT  
@app.route('/delete_indent_data/<itemId>', methods=['GET','POST'])
def delete_indent_data(itemId):
    print('>>>>', itemId)
    if request.method == 'GET':
        print('>>>>', itemId)
    # Delete data from MongoDB
        collection_indent.delete_one({'itemId':  itemId})
        print('>>>>', itemId)
    return redirect(url_for('show_indent_data'))

#DELETE DATA PURCHASER  
@app.route('/delete_purchaser_data/<itemId>', methods=['GET','POST'])
def delete_purchaser_data(itemId):
    print('>>>>', itemId)
    if request.method == 'GET':
        print('>>>>', itemId)
    # Delete data from MongoDB
        collection_purchaser.delete_one({'itemId':  itemId})
        print('>>>>', itemId)
    return redirect(url_for('show_purchaser_data'))

#DELETE DATA INWARD(STORE)  
@app.route('/delete_store_data/<itemId>', methods=['GET','POST'])
def delete_store_data(itemId):
    print('>>>>', itemId)
    print('welcome in delete-store-data')
    if request.method == 'GET':
        print('>>>>', itemId)
    # Delete data from MongoDB
        collection_inward.delete_one({'_id':  ObjectId(itemId)})
        print('>>>>', itemId)
    return redirect(url_for('show_store_data'))

#DELETE DATA BILL INVOICE  
@app.route('/delete_bill_data/<itemId>', methods=['GET','POST'])
def delete_bill_data(itemId):
    print('>>>>', itemId)
    if request.method == 'GET':
        print('>>>>', itemId)
    # Delete data from MongoDB
        collection_bill.delete_one({'_id':  ObjectId(itemId)})
        print('>>>>', itemId)
    return redirect(url_for('show_bill_data'))

#Search bill data
# @app.route('/search_bill_data/',methods=['GET','POST'])
# def search_bill_data():
# json_path = os.path.join(BASE_DIR, 'templates',)    
# with open(json_path, header_names_billData.json', 'r') as f:
#         headers = json.load(f)
#     if request.method=='POST':
#         search_query=request.form.get('search_query4')
#         print('value of search query is-->>',search_query)
#         if search_query:
#                 page=int(request.args.get('page',1))
#                 per_page=10
#                 search_criteria ={
#                 '$or': [
#                     {'venderName':{'$regex':search_query ,'$options':'i'}},
#                     {'itemName':{'$regex':search_query ,'$options':'i'}},
#                     {'billNo':{'$regex':search_query , '$options' :'i'}},
#                 ]
#                 }
#                 total_count=collection_bill.count_documents(search_criteria)
#                 print('value of total count is-->>',total_count)
#                 total_pages=math.ceil(total_count / per_page)
#                 data=list(collection_bill.find(search_criteria).skip((page-1)*per_page).limit(per_page))
#                 return render_template('show_bill_data.html',data=data, headers=headers,current_page=page ,total_pages=total_pages ,per_page=per_page)


# @app.route('/sort_bill_data/', methods=['POST'])
# def sort_bill_data():
#     if request.method == 'POST':
#         column = request.form.get('column')
#         order = request.form.get('order')
#         print("value of column is-->",column)
#         print('value of order is-->',order)
#         # Determine the sort order
#         orderBy = pymongo.ASCENDING if order == 'asc' else pymongo.DESCENDING
#         print('value of orderBy is-->>',orderBy)
       
#         # Perform MongoDB query for sorting and pagination
#         data = list(collection_bill.find().sort(column, orderBy))
#         print('value of data is-->>',data)
        
#         # Convert ObjectId to string for JSON serialization
#         for item in data:
#             item['_id'] = str(item['_id'])

#         # Send the sorted and paginated data back to the client
#         return json_util.dumps(data)
   

#Change Password
@app.route('/change_password',methods=['GET','POST'])
@login_required
def change_password():
    if request.method=='POST':
        email=request.form['email']
        old_password=request.form['old_password']
        new_password=request.form['new_password']
        user_data=collection_user.find_one({'email':email})
        print('value of email is-->>',email)
        print('value of old password is-->>',old_password)
        print('value of user_Data is-->>',user_data)
        print('value of new password is-->>',new_password)
        if user_data:
            password=user_data['password']
            print('value of password is-->>',password)
            if  password==old_password:
                collection_user.update_one({'email':email},{'$set':{'password':new_password}})
                return  render_template('change_password.html',message='password successfully updated')
            else:
                return  render_template('change_password.html',message='old password is wrong...please enter correct old password')
        else:
            return render_template('change_password.html',message='User not found')
    return  render_template('change_password.html')
     


#STORE DATA 
@app.route('/store_data/',methods=['GET','POST'])
@login_required
def store_data():
    if request.method=='POST':
        # Get table data from JSON string in form data
        data= request.get_json()
        
        store_data_array=data.get('storeData')

        print("value of store data array is:",store_data_array)
        
        for store_data in store_data_array:
            item_id=store_data['itemId']
            item_name=store_data['itemName']            
            inward_id=store_data['inwardId']
            date_time =store_data['dateTime']
            qty=int(store_data['qty'])
            item_desc=store_data['itemDesc']
            status=store_data['status']
            amount =float(store_data['amount'])
            rate = float(store_data['rate'])
            bill_no =store_data['billNo']
            vender_name =store_data['venderName']
            print('value of item id is:',item_id)
            print('value of item Name is->>',item_name)
            print("value of inward id is",inward_id)
            print('value of qty is:',qty)
            print('value of  status-->>:',status)
            print('value of billNo is-->>',bill_no)
            # Split the string by '/' and get the last part
            integer_part = inward_id.split('INW')[-1]
            print('value of integer part->>',integer_part)
            # Remove leading zeros
            integer_part_without_zeros = str(int(integer_part))
            item_data= collection_inward.find_one({'itemName':item_name})
            print('values of item_data list is->>',item_data)
            print('values of integer part without zeroes->>',integer_part_without_zeros)
            
            #Store data inside the billInfo database
            billInfo_data={
                'venderName' :vender_name,
                'billNo':bill_no,
                'dateTime': date_time,
                'itemName':item_name,
                'qty':qty,
                'rate':rate,
                'amount':amount,
                'itemDesc':item_desc,
                'status':status
            }
            # Check if the bill exists in the billInfo database
            existing_bill = collection_bill.find_one({'billNo': bill_no})

            print('existing_bill value->>',existing_bill)
            if existing_bill:
                # Check if the item exists in the billInfo database for the given billNo
                existing_item = collection_bill.find_one({'billNo': bill_no, 'itemName': item_name})

                print('value of existing item value->>',existing_item)
                if existing_item:
                    # Case 1: Update qty, rate, and amount for the existing item in the billInfo database
                    old_qty = int(existing_item['qty'])
                    new_qty = old_qty + qty
                    old_amount=float(existing_item['amount'])
                    new_amount=old_amount+amount
                    
                    # Update qty, rate, and amount
                    collection_bill.update_one(
                        {'billNo': bill_no, 'itemName': item_name},
                        {
                            '$set': {
                                'qty': new_qty,
                                'rate': store_data['rate'],  # Assuming rate is present in direct_data_ary
                                'amount': new_amount  # Assuming amount is present in direct_data_ary
                            }
                        }
                    )

                    # Append historical change to 'edit_history' array
                    historical_change = {
                        'date_of_change':  date_time,
                        'old_value': old_qty,
                        'new_value': new_qty  
                    }
                    print('value of historical changes->>', historical_change)
                    collection_bill.update_one(
                        {'billNo': bill_no, 'itemName': item_name},
                        {'$push': {'edit_history': historical_change}}
                    )

                else:
                    # Case 2: Insert new item with all details into the existing billNo in the billInfo database
                    collection_bill.insert_one(billInfo_data)
            else:
                collection_bill.insert_one(billInfo_data)
                
            #Store the data in inward database
            if item_data:
                avl_qty = int(item_data.get('qty'))
                if avl_qty is not None:
                    total_qty = avl_qty + qty
                    print('value of total_qty is->>',total_qty)
                    collection_inward.update_one({'itemName': item_name}, {'$set': {'qty': total_qty}})

                    # Append historical change to 'edit_history' array
                    historical_change = {
                        'date_of_change': date_time,
                        'old_value': avl_qty,
                        'new_value':total_qty
                                                 
                    }
                    print('value of historical changes->>',historical_change)
                    collection_inward.update_one({'itemName': item_name}, {'$push': {'edit_history': historical_change}})
                    print('value of item id->>',item_id)
                    print('value of status is->>',status)
                
                    collection_purchaser.update_one({'itemId':item_id},{'$set':{'status':store_data['status']}})
            else:
                
                collection_inward.insert_one(
                    {
                     'itemId':item_id,
                     'itemName':item_name,
                     'dateTime':date_time,
                     'qty':qty,
                     'itemDesc':item_desc,
                     'status':status
                    }
                )
                print('value of item id->>',item_id)
                print('value of status is->>',status)
                
                collection_purchaser.update_one({'itemId':item_id},{'$set':{'status':store_data['status']}})
            
            # Update the last used INDWCRVAL in the MongoDB collection
            collection_last_ids.update_one({'INWCTRVAL': {'$exists': True}}, {'$set': {'INWCTRVAL': str(integer_part_without_zeros)}}, upsert=True)
    
        return  redirect(url_for('store_dashboard'))
         
    inward_id_doc=collection_last_ids.find_one({'INWCTRVAL':{'$exists':True}})
    print('value of inward_id_doc is->>>',inward_id_doc)
    
    if inward_id_doc:
        inward_id=int(inward_id_doc.get('INWCTRVAL',0))
        inward_id +=1
    else:
        inward_id=1
        print('value of inward id is->>>',inward_id)
    
  
    inward_Id='INW'+str(inward_id).zfill(8)
    print('inward id is after concatnation->>>',inward_Id)
    return render_template('store_data.html',inward_Id=inward_Id, datetime=datetime)


#SEND DATA TO REQUESTED QUERY       
@app.route('/get_indent_data', methods=['POST'])
def get_indent_data():
    print('get_indent_data call')
    selected_po_number = request.form.get('po_number')
    if request.method=='POST':
            print('inside the request.method')
            if selected_po_number:
                print('inside the if condition of selected po number')
                search_criteria = {
                    'poNumber': {'$regex': selected_po_number, '$options': 'i'}
                }

                print('value of search criteria is:',search_criteria)
                # Use aggregation pipeline to filter 'Order Complete' status
                pipeline = [
                    {'$match': search_criteria},
                    {'$match': {'status': {'$ne': 'Order Complete'}}}
                ]
                
                print("value of pipline is->>",pipeline)
                data = list(collection_purchaser.aggregate(pipeline))

                print('value of searched data is:', data)

                # Convert ObjectId to string for JSON serialization
                for entry in data:
                    entry['_id'] = str(entry['_id'])
            else:
                print('fields are empty')
                # Use aggregation pipeline to filter 'Order Complete' status
                pipeline = [
                    {'$match': {'status': {'$ne': 'Order Complete'}}}
                ]
                print("value of pipline is->>",pipeline)
                data = list(collection_purchaser.aggregate(pipeline))

                print("value of indent data is:",data)

            # Return the data as JSON
            return jsonify(data)
    return redirect(url_for('store_data'))

#Find Vender Name in database
@app.route('/check_bill_number/', methods=['POST', 'GET'])
def check_bill_number():
    if request.method == 'POST':
        print('inside the check_bill_number function')
        billNo = request.form.get('billNo')
        print('value of billNo is->>', billNo)
        
        if billNo:
            data = collection_bill.find_one({'billNo': billNo})
            print('value of data is->>', data)
            if data:
                data['_id'] = str(data['_id'])
                return jsonify(data)
            else:
                return jsonify({'error': 'Bill number not found'})
        else:
            return jsonify({'error': 'billNo not provided'})
    
    return jsonify({'error': 'Invalid request method'})


# Direct Data Entry in Store_DB
@app.route('/direct_data/', methods=['POST', 'GET'])
def direct_data():
    if request.method == 'POST':
        data = request.get_json()
        print('value of data ->>', data)
        direct_data_ary = data.get('storeData')
        print('value of direct data ary is:', direct_data_ary)
        item_name = direct_data_ary['itemName']
        item_desc= direct_data_ary['itemDesc']
        date_time=direct_data_ary['dateTime']
        qty = int(direct_data_ary['qty'])
        bill_no = direct_data_ary['billNo']
        item_desc=direct_data_ary['itemDesc']
        status=direct_data_ary['status']
        amount=float(direct_data_ary['amount'])
        print('value of itemname is->>', item_name)
        print('value of qty is->>', qty)
        print('value of bill no is***-->>>', bill_no)

        # Check if the bill exists in the billInfo database
        existing_bill = collection_bill.find_one({'billNo': bill_no})

        print('existing_bill value->>',existing_bill)
        if existing_bill:
            # Check if the item exists in the billInfo database for the given billNo
            existing_item = collection_bill.find_one({'billNo': bill_no, 'itemName': item_name})

            print('value of existing item value->>',existing_item)
            if existing_item:
                # Case 1: Update qty, rate, and amount for the existing item in the billInfo database
                old_qty = int(existing_item['qty'])
                new_qty = old_qty + qty
                old_amount=float(existing_item['amount'])
                new_amount=old_amount+amount
                
                # Update qty, rate, and amount
                collection_bill.update_one(
                    {'billNo': bill_no, 'itemName': item_name},
                    {
                        '$set': {
                            'qty': new_qty,
                            'rate': direct_data_ary['rate'],  # Assuming rate is present in direct_data_ary
                            'amount': new_amount  # Assuming amount is present in direct_data_ary
                        }
                    }
                )

                # Append historical change to 'edit_history' array
                historical_change = {
                    'date_of_change': date_time,
                    'old_value': old_qty,
                    'new_value': new_qty  
                }
                print('value of historical changes->>', historical_change)
                collection_bill.update_one(
                    {'billNo': bill_no, 'itemName': item_name},
                    {'$push': {'edit_history': historical_change}}
                )

            else:
                # Case 2: Insert new item with all details into the existing billNo in the billInfo database
                collection_bill.insert_one(direct_data_ary)

        else:
            # Case 3: Insert new object with new billNo into the billInfo database             
            collection_bill.insert_one(direct_data_ary)

        # Update qty in inward db if item already exists, otherwise insert new object
        item_data = collection_inward.find_one({'itemName': item_name})
        if item_data:
            avl_qty = int(item_data.get('qty'))
            total_qty = avl_qty + qty
            collection_inward.update_one({'itemName': item_name}, {'$set': {'qty': total_qty}})

            # Append historical change to 'edit_history' array
            historical_change = {
                'date_of_change': date_time,
                'old_value': avl_qty,
                'new_value': total_qty
            }
            print('value of historical changes->>', historical_change)
            collection_inward.update_one({'itemName': item_name}, {'$push': {'edit_history': historical_change}})
        else:
            # Insert new object into the inward collection
            data={
                'itemId':'Old Item',
                'itemName':item_name,
                'dateTime': date_time,
                'qty':qty,
                'itemDesc':item_desc,
                'status':status
            }
            collection_inward.insert_one(data)

        return redirect(url_for('store_data'))


#OUTWARD DATA
@app.route('/outward_form/',methods=['GET','POST'])
@login_required
def outward_form():
     
    if request.method=='POST':  
               
        outwardData=request.get_json() 
         
        print('value of outward data array is:',outwardData)
        outward_data=outwardData.get('formData')
        result=[]
        print('value of outward_data->>',outward_data)
          
        item_name=outward_data['itemName']
        date_time=outward_data['dateTime']
        person_name=outward_data['perName']
        batch_no=outward_data['batchNo']
        batch_type=outward_data['batchType']
        qty=outward_data['qty']
        outward_id=outward_data['outwardId']
       
        print('value of outward_id is->>>',outward_id)
        
        print('value of itemName is->>',item_name)
        print('value of qty is->>',qty)

        # Split the string by '/' and get the last part
        integer_part = outward_id.split('OUT')[-1]
        print('value of integer part inside the outward part->>',integer_part)
        # Remove leading zeros
        integer_part_without_zeros = str(int(integer_part))
        
        print('value of integer_part_without_zeroes',integer_part_without_zeros)
        print('inside the for loop data is:',outward_data)
        update_result = update_product_quantity(item_name, qty)
        print('value of update result is:',update_result)
        
        if update_result:
            print('inside the if condition of update result')
            collection_outward.insert_one(outward_data)
            # Update the last used POCTR in the MongoDB collection
            collection_last_ids.update_one({'OUTCTRVAL': {'$exists': True}}, {'$set': {'OUTCTRVAL': str(integer_part_without_zeros)}}, upsert=True)
            result.append('Order Approved')
        else:
            result.append('order not approved')
     
        return jsonify({'message':result})
    data=collection_inward.find()
    outward_id_doc=collection_last_ids.find_one({'OUTCTRVAL':{'$exists':True}})
    print('value of data is :',data)
    print('value of outward_id_doc is:',outward_id_doc)
    if outward_id_doc:
        outward_id=int(outward_id_doc.get('OUTCTRVAL',0))
        outward_id +=1
    else:
        outward_id=1
    print('value of outward_id->>>',outward_id)
    
    outward_Id='OUT'+str(outward_id).zfill(8)
    return render_template('outward_form.html',data=data,outward_Id=outward_Id,datetime=datetime)


#AUTO UPDATION OF PRODUCT QTY
def update_product_quantity(item_name, qty):
    # Find the product in the database
    print("inside the update product function")
    product =collection_inward.find_one({'itemName':item_name})
    print('value of product is :',product)
   
    if product:
        # Check if there is enough quantity in stock
        current_qty = int(product['qty'])
        print('value of qty is:',qty)
        print('value of qty inside update function is:',current_qty)
        print('value of item name is:',item_name)
        qty=int(qty)
        if current_qty >= qty:
            # Deduct the ordered qty
            new_qty = current_qty - qty
            print('value of new qty is:',new_qty)
            # Update the product qty in the database
            collection_inward.update_one({'itemName': item_name},{'$set': {'qty': new_qty}})
            return True
        else:
            return False
    else:
        return  False
    
    
#FIND REQUESTED ITEMS IN DB
@app.route('/find_items/',methods=['GET','POST'])
def find_items():
    req_item = request.form.get('req_item')
    print('value of required item is:',req_item)
    if request.method=='POST':
            print('inside the request.method')
            if req_item:
                print('inside the if condition of selected  item')
                search_criteria = {
                    '$or': [
                        {'itemName': {'$regex': req_item, '$options': 'i'}},
                    ]
                }
                print('value of data inside the if condition:',search_criteria)
                data = list(collection_inward.find(search_criteria))
                print('value of searched data is:',data)
                
                # Convert ObjectId to string for JSON serialization
                for entry in data:
                    print('fields are empty')
                    entry['_id'] = str(entry['_id'])
            else:
                print('fields are empty')
                data = list(collection_inward.find({}))
                # Convert ObjectId to string for JSON serialization
                for entry in data:
                    entry['_id'] = str(entry['_id'])

            print("value of indent data is:",data)

            # Return the data as JSON
            return jsonify(data)
    return redirect(url_for('outward_form'))

#FIND REQUESTED  QTY IN DB
@app.route('/find_qty/', methods=['POST'])
def find_qty():
    req_item = request.form.get('req_item')
    req_qty_str = request.form.get('req_qty')

    if req_qty_str is not None:
        try:
            req_qty = int(req_qty_str)
        except ValueError:
            return jsonify({'status': 'error', 'message': 'Invalid quantity format'})

    print('value of required item is:', req_item)
    print('value of req_qty ', req_qty)

    if req_item:
        print('inside the if condition of selected item')
        search_criteria = {
            '$or': [
                {'itemName': {'$regex': req_item, '$options': 'i'}},
            ]
        }
        print('value of data inside the if condition:', search_criteria)
        data = list(collection_inward.find(search_criteria))
        print('value of searched data is:', data)

        if data:
            # Assuming 'qty' is the field in your data that represents the available quantity
            available_qty = data[0].get('qty', 0)
            return jsonify({'status': 'success', 'availableQty': available_qty})

        else:
            print('Item not found in the inventory.')
            return jsonify({'status': 'error', 'message': 'Item not found'})

    return jsonify({'status': 'error', 'message': 'Invalid request'})

#Show Admin Profile
@app.route('/show_admin_profile',methods=['POST','GET'])
def show_admin_profile():
    user='admin'
    data=collection_user.find({'user_type':user})
    print('value of admin profile data-->>',data)
    return render_template('show_admin_profile.html',data=data)
    
#Show Indenter Profile
@app.route('/show_indenter_profile',methods=['POST','GET'])
def show_indenter_profile():
    user='indenter'
    data=collection_user.find({'user_type':user})
    print('value of data is -->>',data)
    return render_template('show_indenter_profile.html',data=data)

#Show Purchaser Profile
@app.route('/show_purchaser_profile',methods=['POST','GET'])
def show_purchaser_profile():
    user='purchaser'
    data=collection_user.find({'user_type':user})
    print('value of purchaser profile',data)
    return render_template('show_purchaser_profile.html',data=data)

#Show Store Profile
@app.route('/show_store_profile',methods=['POST','GET'])
def show_store_profile():
    user='store'
    data=collection_user.find({'user_type':user})
    print('value of store profile data is-->>',data)
    return render_template('show_store_profile.html',data=data)



if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True , port=5000)