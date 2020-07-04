from flask import Flask, render_template, request, redirect, flash, url_for
import json
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode
import os  
import uuid
import sys
import datetime 

#uploading files ----------------------------------------------------
#UPLOAD_FOLDER = '/path/to/the/uploads'
#ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
#The UPLOAD_FOLDER is where we will store the uploaded files 
#The ALLOWED_EXTENSIONS is the set of allowed file extensions,
#prevent users form uploading HTML files that will mess up website
app =Flask(__name__)


app.config['UPLOAD_FOLDER'] = 'static/Uploads'
app.config['AUTO_UPLOAD_FOLDER'] = 'static/autoUploads'

connection = mysql.connector.connect(host='localhost',
                                    database='actalab',
                                    user='root',
                                    password='12345678')
    #verify if connected

db_Info = connection.get_server_info()
print("Connected to MySQL Server version ", db_Info)
            #cursor object formed by a MySQLConnection object, 
            #instantiates objects that execute operations on database
cursor = connection.cursor(dictionary=True) #create cursor object to execute functions on DB
cursor.execute("select database();")  #call this method on cursor
record = cursor.fetchone()
print("You're connected to database: ", record)

#---------------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------------

#make instrumentDict a variable
with open('static/json/instrumentDict.json') as file:
    instruDict = json.load(file)

@app.route('/')
def index():
    return render_template('index.html')
#---------------------------------------------------------------------------------------------------------
# function to create a list of dictionaries with keys - material_name and source_of_Data
def Display_items_dict(material_table, submission_table):
    items_nestList = []
    no_of_records = len(material_table)
    print ("material tables: ", material_table)
    print ("submisssion table: ", submission_table)

    if (no_of_records > 0) == True: 
        for i in range(0,no_of_records):
            print ("i: ", i)
            keysList = [] #need to flush these list before going through next dictonary
            valuesList = []
            wanted_dict_material = material_table[i]
            material_keys = wanted_dict_material.keys()
            print ("material_keys:", material_keys)
            for j in material_keys:
                keysList.append(j)
            
            material_values = wanted_dict_material.values()
            for m in material_values:
                valuesList.append(m)
                    
            wanted_dict_subm = submission_table[i]
        
            submission_keys = wanted_dict_subm.keys()
            for k in submission_keys:
                keysList.append(k)
            
            submission_values = wanted_dict_subm.values()
            for n in submission_values:
                valuesList.append(n)

            new_dict = {keysList[p]: valuesList[p] for p in range(len(keysList))}
            items_nestList.append(new_dict)
    print ("items_nestList: ", items_nestList)
    return items_nestList
    
#---------------------------------------------------------------------------------------------------------
@app.route('/list-materials')
def listMaterials():
    cursor.execute('SELECT submission_id, material_name FROM material_details')
    materials_data = cursor.fetchall()
    #print ("materials_data:", materials_data) #data: [{'submission_id': 1, 'material_name': 'Carbon'}, {'submission_id': 2, 'material_name': 'Silicon'}, {'submission_id': 3, 'material_name': 'Helium'}, {'submission_id': 4, 'material_name': 'Gold'}]
    #print (type(materials_data)) #dictionaries inside list
    
    cursor.execute('SELECT source_data, curr_time FROM submission_details')
    sources_data = cursor.fetchall()  #data: [{'source_data': ___,}, {'source_data': '____'},
    for i in sources_data:
        dateAndTime = i["curr_time"]
        #type of datetime is <class 'datetime.datetime'>  
        convertedDateTime = dateAndTime.strftime("%d/%m/%Y, %H:%M:%S")
        #converts to dd/mm/yyyy and time in hrs/min/sec
        #converted to string type
        i["curr_time"] = convertedDateTime #replace value in dictionary

    complete_listOfDicts = Display_items_dict(materials_data,sources_data)
    #print (complete_listOfDicts)
    #can change function so that it takes in inputs from material table and usbmission table. 
    # can show one column for material name and one for source of data
    cursor.execute('SELECT submission_id, operator, sample_id, run, composition, heating_rate, max_temp, comment, resolution, lens, curr_time FROM linkam_table')
    materials_data_linkam = cursor.fetchall()
    for i in materials_data_linkam:
        dateAndTime = i["curr_time"]
        convertedDateTime = dateAndTime.strftime("%d/%m/%Y, %H:%M:%S")
        #converts to dd/mm/yyyy
        i["curr_time"] = convertedDateTime
    
    #print ("materials_data_linkam:" : [{'submission_id': 1, 'operator': 'Alyssa', 'sample_id': AJA3, 'run': 2, 'composition': 'Ge2SbTe5'....}, {'submission_id': 2, 'operator': 'Alyssa', 'sample_id': AJA3, 'run': 2, 'composition': 'Ge2SbTe5'....}, {'submission_id': 3, 'operator': 'Alyssa', 'sample_id': AJA3, 'run': 2, 'composition': 'Ge2SbTe5'....}]
    return render_template('list_materials.html', materials_listOfDicts = complete_listOfDicts, materials_data_linkam=materials_data_linkam )
#---------------------------------------------------------------
def write_file(data, filename):
    with open(filename, 'wb') as f:
        f.write(data)

#---------------------------------------------------------------
@app.route('/show-material/<sub_id>/<material_name>',  methods=['GET', 'POST'])
def material(sub_id, material_name):
    sub_id = int(sub_id)
    print (sub_id, type(sub_id))
    select_material_query = 'SELECT submission_id, material_name, file_name_in_server, data_format, instrument, datatype FROM material_details WHERE submission_id = %s'
    cursor.execute(select_material_query,(sub_id,))
    material_data = cursor.fetchall() #this is like this [{'submission_id': 5, 'material_name': 'Argon', 'data_format': '.txt', 'instrument': 'Linkam', 'datatype': 'Optical spectra vs Temperature'}]
    #material_data is actually a string! not list object so, need to aprse as JSON object
    
    print("my_material_data: ", material_data)
    print ('hello!')
    #print ('material_data:', material_data)

    select_contributor_query = 'SELECT * FROM contributor_details WHERE submission_id = %s'
    cursor.execute(select_contributor_query, (sub_id,) )
    contributor_data = cursor.fetchall()
    print ("my_contributor_data: " ,contributor_data)
    #contributor_data = listOfTuple_to_List(my_contributor_data)
    #print ('contributor_data:', contributor_data)

    select_submission_query = 'SELECT * FROM submission_details WHERE submission_id = %s'
    cursor.execute(select_submission_query, (sub_id,) )
    submission_data = cursor.fetchall()
    print ("my_subs_data: ", submission_data)

    select_auto_instrument = 'SELECT operator, sample_id, run, composition, heating_rate, max_temp, comment, resolution, lens, file_name_in_server, data_format FROM linkam_table WHERE submission_id = %s'
    cursor.execute(select_auto_instrument, (sub_id,) )
    auto_material_data = cursor.fetchall()
    print ("auto_material_data: ", auto_material_data)
    #submission_data = listOfTuple_to_List(my_submission_data) #submission_data: ['5', 'ActaLab Members Only', '', 'Self-Collected']
    #print ('submission_data:', submission_data)
    #--------------------------------------------------------------------------------------------------------------
    if request.method == "POST":
        if len(material_data) != 0: 
            query = "SELECT data_file, data_format FROM material_details WHERE submission_id=%s" 
        else:
            query = "SELECT data_file, data_format FROM linkam_table WHERE submission_id=%s"
        cursor.execute(query,(sub_id,))
        listOfDataDict = cursor.fetchall() 
        print (listOfDataDict) #[{data_file: "bfjbfj", data_Format: "rubgr"}]
        dataFileBytes = listOfDataDict[0].get('data_file')
        print ("filename: ", "filename")
        #print ("photo: ", photo)
        extension = listOfDataDict[0].get('data_format')  #use fetchone so that not returned in a tuple
        print ("extension: ", extension)
        
        #create a new filename that the data is downloaded as when saved in users computer
        write_file(dataFileBytes, 'User'+str(sub_id)+ extension) 
        print ("i'm here also!")
    #---------------------------------------------------------------
    print ("i'm here!")
    print(material_name)
    return render_template('show_material.html', material_name = material_name, sub_id= sub_id, material_data=material_data,contributor_data=contributor_data, submission_data=submission_data, auto_material_data =auto_material_data )
#---------------------------------------------------------------
#if this url fragment is seen in the browser, then render this html page
#pass InstruDict as 'data'
@app.route('/newInstru')
def select_instru():
    return render_template('select_instru.html', data = instruDict)
#-----------------------------------------------------------------
#app.route for each newInstru selected
#when selected instrument displayed in browser tab, make movie and data variable that can be called in the html
@app.route('/selected-instru/<instru>')
def select_datatype(instru):
    return render_template('select_datatype.html', instru = instru, data = instruDict)

def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData
#---------------------------------------------------------------
#app.route for each datatype selected
#use method GET and POST as a parameter to be passed into the enter_info template
@app.route('/selected-instru&datatype/<instruName>/<chosenDataType>', methods=['GET', 'POST'])
def enter_info(instruName, chosenDataType):
    print ("hello")
    print (instruName, chosenDataType)
    if request.method=='POST':
        nameContributor=request.form['nameContributor']
        researchGroup=request.form['researchGroup']
        labLocation=request.form['labLocation']
        conditions=request.form['conditions']
        uploadedFile = request.files['uploadedFile']
        #split the extension name from the file name to add to new file name later
        extension = os.path.splitext(uploadedFile.filename)[1]
        #create a new unique file name using uuid
        f_name = str(uuid.uuid4()) + extension
        #Create a folder called Uploads in  static folder. 
        #Add the path to the Upload folder in the app configuration (above)
        # upload the file into the static/uploads folder
        uploadedFile.save(os.path.join(app.config['UPLOAD_FOLDER'], f_name))
        #print filename
        print ('filename', f_name) #filename 55166e7d-72df-46dc-b0e0-8d67b3fe35e0.pdf
        print ('bytes:', uuid.uuid4().bytes) #bytes: b'\x8f[\x84\xafr\x1fOF\xa3\xee\xa8\t\xcd\xf5SJ'
        theFile = convertToBinaryData( "static/Uploads/" + f_name)

        # print ("theFileBinary:", theFile )
        # print(type(theFile)) #output: <class 'bytes'>
        
        materialName = request.form['materialName']

        privacyOption = request.form['optradio']

        print (nameContributor, researchGroup, labLocation, conditions)
        print (materialName)
        print ("Privacy Option:")
        print (privacyOption)
        
        insertQueryContributer = "INSERT INTO contributor_details(contributor_name, lab_locn, research_grp, collecn_conditions) VALUES (%s,%s, %s, %s)"
        cursor.execute( insertQueryContributer,(nameContributor,researchGroup,labLocation,conditions))
        
        insertQueryMaterial = "INSERT INTO material_details(material_name, data_format, data_file, file_name_in_server, instrument, datatype) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute( insertQueryMaterial,(materialName, extension ,theFile, f_name, instruName, chosenDataType))
        connection.commit()
        print(cursor.rowcount, "Record inserted successfully into table 2")

        insertQuerySubmission = "INSERT INTO submission_details(privacy_option, file_type, source_data) VALUES (%s, %s, %s)"
        cursor.execute(insertQuerySubmission,(privacyOption,'','Self-Collected'))
        connection.commit() #rememeber to commit the record!
        print(cursor.rowcount, "Record inserted successfully into table 3")
        

        print(cursor.rowcount, "Record inserted successfully into table")
        return redirect('/upload_data') #redirect when submit button clicked
        #has to be above cursor.close otherwise casues problems
        
         #sends user to next page via submit button also.
    return render_template('enter_info.html', chosenInstru = instruName, chosenDataType = chosenDataType)

#---------------------------------------------------------------
def createKeyVals(data_text_list, n):    
            labelSplit =  data_text_list[n].split("=")

            key = labelSplit[0]
            val = labelSplit[1]
            return key, val

@app.route('/auto-add', methods=['GET', 'POST'])
def auto_add_DB():
    if request.method =='POST':
        #save file to database
        autoUploadFile = request.files['autoUploadFile']
        #split the extension name from the file name to add to new file name later
        extension = os.path.splitext(autoUploadFile.filename)[1]
        #create a new unique file name using uuid
        f_name = str(uuid.uuid4()) + extension
        #Create a folder called Uploads in  static folder. 
        #Add the path to the Upload folder in the app configuration (above)
        # upload the file into the static/autoUploads folder
        #define this autoUploads static folder above!
        autoUploadFile.save(os.path.join(app.config['AUTO_UPLOAD_FOLDER'], f_name))
        #print filename
        print ('filename', f_name) #filename 55166e7d-72df-46dc-b0e0-8d67b3fe35e0.pdf
        print ('bytes:', uuid.uuid4().bytes) #bytes: b'\x8f[\x84\xafr\x1fOF\xa3\xee\xa8\t\xcd\xf5SJ'
        fileToCall = "static/autoUploads/" +f_name
        theFile = convertToBinaryData( "static/autoUploads/" +f_name)
        #Now read file and create  dictionary form of the values ot uploaded in database.
        f = open(fileToCall,"r")
        data_text_list =[]
        for line in f:
            l = line.strip()
            data_text_list.append(l)
        f.close
        print ('data_text_list: ', data_text_list)
        recordDict = {}
        for n in range (0, 9):
            key, val = createKeyVals(data_text_list, n)
            print ('key: ', key, 'val: ', val)
            # Adding a new key value pair
            recordDict[key] = val 
        print ('recordDict: ', recordDict)
        insertQueryInstrument = "INSERT INTO linkam_table(operator, sample_id, run, composition, heating_rate, max_temp, comment, resolution, lens, file_name_in_server, data_format, data_file) VALUES (%s,%s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute( insertQueryInstrument, (recordDict['operator'], recordDict['SampleID'], recordDict['Run'], recordDict['Composition'], recordDict['Heating Rate'], recordDict['Max Temperature'], recordDict['Comment'], recordDict['Resolution'], recordDict['Lens'], f_name, extension, theFile))
        connection.commit()
    return render_template('auto_add.html')



#---------------------------------------------------------------
#need to include the method 'post' in order for the form submit button to work
@app.route('/upload_data',  methods=['GET', 'POST'])
def upload_data():
    return render_template('upload_data.html')

@app.route('/aja-log')
def aja_log():
    return render_template('aja_log.html')

@app.route('/about')
def about():
    return render_template('about.html')


if __name__=='__main__':
    app.run(debug=True)

#--------Establishing MySQL connections--------------------------------------------
#allow using this module’s API to connect MySQL.
# From: https://pynative.com/python-mysql-database-connection/
# import mysql.connector

# #how  an error if failed to connect Databases 
# from mysql.connector import Error
# from mysql.connector import errorcode

# try:
#     #Using .connect method to connect to MySQL Database, and return to a python object
#     # four required parameters: Host, Database, User and Password 
#     connection = mysql.connector.connect(host='localhost',
#                                          database='actalab',
#                                          user='root',
#                                          password='12345678')
#     #verify if connected

#     db_Info = connection.get_server_info()
#     print("Connected to MySQL Server version ", db_Info)
#     #cursor object formed by a MySQLConnection object, 
#     #instantiates objects that execute operations on database
#     cursor = connection.cursor() #create cursor object to execute functions on DB
#     cursor.execute("select database();")  #call this method on cursor
#     record = cursor.fetchone()
#     print("You're connected to database: ", record)
    
#     #---insert table------------------------------------------------------------
#     #---deifine a create table funtion 
#     mySql_Create_Table_Query = """CREATE TABLE contributer_details ( 
#                          submission_id int(11) NOT NULL,
#                          contibutor_name varchar(250) NOT NULL,
#                          lab_locn varchar(250) NOT NULL,
#                          reserach_grp varchar(250) NOT NULL,
#                          collecn_conditns varchar(250) NOT NULL,
#                          PRIMARY KEY (submission_id)) """

#     #result = cursor.execute(mySql_Create_Table_Query) #call table function
#     print("Table:contributer_details created successfully ")

#     #---insert row/record------------------------------------------------------------
#     mySql_insert_query = """INSERT INTO contributer_details (submission_id, contibutor_name, lab_locn, reserach_grp, collecn_conditns) 
#                            VALUES 
#                            (101, 'Anshiqa Agrawal', '4.131', 'Actalab Grp', 'Stable') """
    
#     cursor.execute(mySql_insert_query)
#     connection.commit() #rememeber to commit the record!
#     print(cursor.rowcount, "Record inserted successfully into table")

# except Error as e:
#     print("Error while connecting to MySQL", e)

# #------------------------------------------------------------------------------------


