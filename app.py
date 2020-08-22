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
#prevent users form uploading HTML files that will mess up website
app =Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'static/Uploads'
app.config['AUTO_UPLOAD_FOLDER'] = 'static/autoUploads'
app.config['GLOBAL_DATA_UPLOADS'] = 'static/globalDataUploads'


connection = mysql.connector.connect(host='actalab-rds.cwk19lew5lew.ap-southeast-1.rds.amazonaws.com',
                                    database='actalab',
                                    user='admin',
                                    password='Actalab!#%&SUTD') 
#must add inbound rule in RDS--> 0.0.0.0 in security group to allow all ip adresses to enter 

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
#---------------------------------------------------------------------------------------------------------
@app.route('/list-materials')
def listMaterials():
  
    # for i in sources_data:
    #     dateAndTime = i["curr_time"]
    #     #type of datetime is <class 'datetime.datetime'>  
    #     convertedDateTime = dateAndTime.strftime("%d/%m/%Y, %H:%M:%S")
    #     #converts to dd/mm/yyyy and time in hrs/min/sec
    #     #converted to string type
    #     i["curr_time"] = convertedDateTime #replace value in dictionary


    # for i in materials_data_linkam:
    #     dateAndTime = i["curr_time"]
    #     convertedDateTime = dateAndTime.strftime("%d/%m/%Y, %H:%M:%S")
    #     #converts to dd/mm/yyyy
    #     i["curr_time"] = convertedDateTime

    #--for new tables format---------------------------------------------------
    #query for all submitted items in the database 
    cursor.execute('SELECT submission_id, sample_id, instrument_id, instrument_name FROM instrument_details')  #can't take datafile beacuse not string
    instrument_details_dict = cursor.fetchall() #data: [{'submission_id': ___,'instrument_name':___...}, {'submission_id': ___, 'instrument_name':___...},..]      
   
    #remove all duplicated dicts in the obtained list (duplicated because for each header_value, sub id, sample id and instrument is the same)
    instrument_details_dict = [i for n, i in enumerate(instrument_details_dict) if i not in instrument_details_dict[n + 1:]] 
    print ('instrument_details_dict: ',instrument_details_dict)
    
    #query for compostition value of each submission id 
    queryForCompositions = "SELECT submission_id, header_value FROM instrument_details WHERE instrument_header_field = %s"
    compositionString = ("composition", ) #will be used to replace the %s placeholder in the query execute
    cursor.execute(queryForCompositions, compositionString)
    compositions_dict = cursor.fetchall()
    print ('compositions_dict: ', compositions_dict) 

    #for each dict item in instrument_details_dict, add the matching composition key-value to the dict 
    #by adding according to item in list... can be changed by using the matching sub_id?
    for n in range(0,len(instrument_details_dict)):
        instrument_details_dict[n]['composition']=  compositions_dict[n]['header_value']

    return render_template('list_materials.html', instrument_details_dict=instrument_details_dict )
#---------------------------------------------------------------
def write_file(DBdata, filenameInUser):
    with open(filenameInUser, 'wb') as f:
        f.write(DBdata)
        #new data is being written on the 'filename' file
        #so, in the user's download location, the 'filename' file is being replaced by the data file

#---------------------------------------------------------------
@app.route('/show-material/<sub_id>/<material_name>',  methods=['GET', 'POST'])
def material(sub_id, material_name):
    #convert sub_id obtained from page link to an integer type
    sub_id = int(sub_id)
    print (sub_id, type(sub_id))

    #query all details from instrument_details for the wanted submission_id 
    select_sample_details ='SELECT * FROM instrument_details WHERE submission_id = %s'
    cursor.execute(select_sample_details, (sub_id,) )  #sub_id used to replace the %s placeholder ... can't take datafile beacuse not string
    sub_id_instrument_details = cursor.fetchall() #data: [{'submission_id': ___,'instrument_name':___}, {'submission_id': ___, 'instrument_name':___},..]      
   
    #remove all duplicated dicts from the obtained list (in case of any)
    sub_id_instrument_details = [i for n, i in enumerate(sub_id_instrument_details) if i not in sub_id_instrument_details[n + 1:]] 
    print ('sub_id_instrument_details: ',sub_id_instrument_details)
    
    #--------------------------------------------------------------------------------------------------------------
    #get data blob and allow user to write file onto local computer by downloading
    query = "SELECT data_file, data_format FROM instrument_data WHERE submission_id=%s"
    cursor.execute(query,(sub_id,))
    DataDict = cursor.fetchall() 
    print (DataDict) #[{data_file: "someexample", data_Format: ".txt"}]

    #obtain the data file blob as a variable
    dataFileBytes = DataDict[0].get('data_file')
    #obtain the extension as a variable
    extension = DataDict[0].get('data_format')  #use fetchone so that not returned in a tuple
    print ("extension: ", extension)
    #create a new filename that the data is downloaded as when saved in users computer
    write_file(dataFileBytes, 'User'+str(sub_id)+ extension) 
    print ("i'm here also!")

    #----------------------------------------------------
    #query file_name_in_server from instrument_data separately because a blob cannot be passed through JS as string
    queryForFilename = "SELECT file_name_in_server FROM instrument_data WHERE submission_id=%s"
    cursor.execute(queryForFilename,(sub_id,))
    FileNameDict = cursor.fetchall() 

    return render_template('show_material.html', material_name = material_name, sub_id= sub_id, sub_id_instrument_details =sub_id_instrument_details, FileNameDict = FileNameDict )
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
    print (instruName, chosenDataType)
    if request.method=='POST':
        print ("hello")
        #----get new submission id(odd)-----------
        used_id_list_odd = []
        cursor.execute('SELECT submission_id FROM instrument_data')
        used_submissionID = cursor.fetchall() #data: [{'submission_id': ___}, {'submission_id': ___},..]
        if not cursor.rowcount: #specifies number of rows that the last .execute*() outputs
            this_submission_id = 1
            print ("No data yet")
        else:
            for i in used_submissionID:
                if (i['submission_id'])%2 != 0: #id is odd, add to list
                    used_id_list_odd.append(i['submission_id'])
            if len(used_id_list_odd) == 0: #table is not empty BUT no ODD id yet
                this_submission_id = 1
            else: 
                used_id_list_odd = sorted(used_id_list_odd)
                this_submission_id = used_id_list_odd[-1] + 2 #grab last id and add 2 for new odd number
        print ('this_submission_id: ', this_submission_id)

        #----upload details of file into the TABLE instrument details ------------
        operator=request.form['nameOperator'] #comes from NAME parameter of input in the form
        print ("hello2")
        sampleId=request.form['nameSampleID']
        comments=request.form['nameComments']
        composition=request.form['nameComposition']
        curr_time = datetime.datetime.now() #has milliseconds also :(
        curr_time = curr_time.strftime("%Y-%m-%d %H:%M:%S") #only h,m,s
        #output: curr_time: 2020-07-10 07:32:44
        privacyOption = request.form['optradio']
        print (operator, sampleId, comments,composition )
        print ("Privacy Option:")
        print (privacyOption)
        #create a dictionary with key: value as header_name: header_value
        header_dict = {'operator': operator, 'comments':comments, 'composition':composition, 'Upload Time': curr_time}
        for key, value in header_dict.items():
            print ("hello2")
            print (key, value)
            insertFileDetails = "INSERT INTO instrument_details(submission_id, sample_id, instrument_id, instrument_name, instrument_header_field, header_value) VALUES (%s, %s,%s, %s, %s, %s)"
            cursor.execute(insertFileDetails,(this_submission_id, sampleId, 1, instruName, key, value))
            connection.commit()
        #----upload binary datafile and filename in server to TABLE instrument_data ------------
        #get the uploaded file from the form
        uploadedFile = request.files['uploadedFile']
        #split the extension name from the file name (to add it to the new file name later)
        extension = os.path.splitext(uploadedFile.filename)[1]
        #create a new unique file name using uuid
        f_name = str(uuid.uuid4()) + extension
        #Create a folder called Uploads in  static folder. 
        #Using the path to the static/uploads folder (declared in the app configuration above), put data file there with new name 
        uploadedFile.save(os.path.join(app.config['UPLOAD_FOLDER'], f_name))
        #use funciton defined above to convert file into binary data (put into database as longblob)
        theFile = convertToBinaryData("static/Uploads/" + f_name)

        print ('filename', f_name) #filename 55166e7d-72df-46dc-b0e0-8d67b3fe35e0.pdf
        print ('bytes:', uuid.uuid4().bytes) #bytes: b'\x8f[\x84\xafr\x1fOF\xa3\xee\xa8\t\xcd\xf5SJ'
        print(type(theFile)) #output: <class 'bytes'>

        insertDataFile = "INSERT INTO instrument_data(submission_id, sample_id, instrument_id, instrument_name, data_file, file_name_in_server, data_format) VALUES (%s, %s,%s, %s, %s, %s, %s)"
        cursor.execute( insertDataFile,(this_submission_id, sampleId,  1 , instruName, theFile, f_name, extension))
        connection.commit()


        print(cursor.rowcount, "Record inserted successfully into table")
        return redirect('/upload_data') #redirect to this page when submit button clicked
        #has to be above cursor.close otherwise casues problems
        
         #sends user to next page via submit button also.
    return render_template('enter_info.html', chosenInstru = instruName, chosenDataType = chosenDataType)

#---------------------------------------------------------------
def createKeyVals(data_text_list, n):    
            labelSplit =  data_text_list[n].split("=")

            key = labelSplit[0]
            val = labelSplit[1]
            return key, val

#create submissionID list for even numbers


@app.route('/auto-add', methods=['GET', 'POST'])
def auto_add_DB():
    if request.method =='POST':
        #---get list of all used submission ids
        used_id_list_even = []
        cursor.execute('SELECT submission_id FROM instrument_data')
        used_submissionID = cursor.fetchall() #data: [{'submission_id': ___}, {'submission_id': ___},..]
        if not cursor.rowcount: #specifies number of rows that the last .execute*() outputs
            this_submission_id = 2
            print ("No data yet")
        else:
            for i in used_submissionID:
                if (i['submission_id']%2) == 0 : #is even, add to list
                    used_id_list_even.append(i['submission_id']) 
            if len(used_id_list_even) == 0: #table not empty BUT no even id yet
                this_submission_id = 2
            else: 
                used_id_list_even = sorted(used_id_list_even)
                this_submission_id = used_id_list_even[-1] + 2 #grab last id and add 2
        print ('this_submission_id: ', this_submission_id)
        
        #-------save file to database---
        autoUploadFile = request.files['autoUploadFile']
        #split the extension name from the file name to add to new file name later
        extension = os.path.splitext(autoUploadFile.filename)[1]
        #create a new unique file name using uuid
        f_name = str(uuid.uuid4()) + extension
        #add the autouploadedfile into the autoUpload folder (Declared in app confign above) 
        autoUploadFile.save(os.path.join(app.config['AUTO_UPLOAD_FOLDER'], f_name))
        fullFilePathServer = "static/autoUploads/" +f_name #get path name of file in server back
        theFile = convertToBinaryData( fullFilePathServer )
        print ('filename', f_name) #filename 55166e7d-72df-46dc-b0e0-8d67b3fe35e0.pdf
        print ('bytes:', uuid.uuid4().bytes) #bytes: b'\x8f[\x84\xafr\x1fOF\xa3\xee\xa8\t\xcd\xf5SJ'
        
        #---Read file and create dictionary of key-values in header---
        f = open(fullFilePathServer,"r") #open submitted file and read file
        data_text_list =[] #init empty list
        for line in f:
            l = line.strip()
            data_text_list.append(l)
        f.close
        print ('data_text_list: ', data_text_list)
        recordDict = {} #create empty dict
        for n in range (0, 9):
            key, val = createKeyVals(data_text_list, n) #use function defined above
            print ('key: ', key, 'val: ', val)
            # Adding a new key value pair
            recordDict[key] = val 
        print ('recordDict: ', recordDict)

        #--get sample id and insert keyvals into mysql
        sample_id = recordDict['SampleID']
        for header, headerValue in recordDict.items():
            print ('header: ', header, ' headerValue: ', headerValue)
            if header != 'SampleID':
                insertQueryInstrument = "INSERT INTO instrument_details(submission_id, sample_id, instrument_id, instrument_name, instrument_header_field, header_value) VALUES (%s, %s, %s, %s, %s, %s)"
                cursor.execute( insertQueryInstrument, (this_submission_id, sample_id, 1, 'instruName', header, headerValue))
                print("header inserted")
                connection.commit()
            else:
                continue

        #--insert datafile & file name in server into mysql
        insertQueryInstrument = "INSERT INTO instrument_data(submission_id, sample_id, instrument_id, instrument_name, data_file, file_name_in_server, data_format) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute( insertQueryInstrument, (this_submission_id, sample_id, 1, 'instruName', theFile, f_name, extension))
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


@app.route('/global-data',  methods=['GET', 'POST'])
def upload_data_global():
    warningMessage = ""
    cursor.execute('SELECT property FROM global_published_data')  #get all avail properties to show in dropdown
    global_published_property_dict = cursor.fetchall()
    global_published_property_dict = [i for n, i in enumerate(global_published_property_dict) if i not in global_published_property_dict[n + 1:]] #remove duplicates
    #first import json module!!
    #store uploaded json file
    if request.method =='POST':
        if request.form['submit_button'] == 'upload_file':
            #-------save file to database---
            globalDataFile = request.files['UploadGlobalFile'] #call file from the HTML form
            #split the extension name from the file name to add to new file name later
            global_data_extension = os.path.splitext(globalDataFile.filename)[1]
            #create a new unique file name using uuid
            global_data_f_name = str(uuid.uuid4()) + global_data_extension
            #add the autouploadedfile into the autoUpload folder (Declared in app confign above) 
            globalDataFile.save(os.path.join(app.config['GLOBAL_DATA_UPLOADS'], global_data_f_name))
            globalFullFilePathServer = "static/globalDataUploads/" + global_data_f_name #get path name of file in server back
            theGlobalDataFile = convertToBinaryData( globalFullFilePathServer )
            print ('globalfilename', global_data_f_name) #filename 55166e7d-72df-46dc-b0e0-8d67b3fe35e0.pdf
            print ('bytes:', uuid.uuid4().bytes) #bytes: b'\x8f[\x84\xafr\x1fOF\xa3\xee\xa8\t\xcd\xf5SJ'

            #---Read file and create dictionary of key-values in header---
            with open(globalFullFilePathServer) as f: #open submitted json file and read file
                global_data_listOfDicts = json.load(f)
                print("type of data: ", type(global_data_listOfDicts)) #list

            for aDict in global_data_listOfDicts:
                #extract data from each dict
                newMaterial = aDict['material']
                newProperty = aDict['property']
                newPropertyValue = aDict['propertyVal']
                newSentence = aDict['sentence']
                newYear = aDict['year']
                newDoi = aDict['DOI']

            #---create new increment submission id because auto_increment feature in MySQL not account for deleted rows"""
                used_subid_list = [] #get list of all used submission ids to automatically set new sub_id 
                cursor.execute('SELECT global_sub_id FROM global_published_data')
                used_submissionID = cursor.fetchall() #data: [{'submission_id': ___}, {'submission_id': ___},..]
                if not cursor.rowcount: #specifies number of rows that the last .execute*() outputs. If not means if the nu of rows == 0
                    this_submission_id = 1
                    print ("No data yet")
                else:
                    for i in used_submissionID:
                        used_subid_list.append(i['global_sub_id']) 
                        used_subid_list = sorted(used_subid_list)
                        this_submission_id = used_subid_list[-1] + 1 #grab last id and add 1
            #---now insert all data into table (within the for loop for each dict)-----
                insertQueryGlobalData = "INSERT INTO global_published_data(global_sub_id, material, property, property_value, sentence, year, doi) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                cursor.execute( insertQueryGlobalData, (this_submission_id, newMaterial, newProperty, newPropertyValue, newSentence, newYear, newDoi))
                print("data from globally published sources inserted")
                connection.commit()

            #--insert datafile into globalExtractedFiles table 
            used_fileid_list = [] #get list of all used submission ids to automatically set new sub_id 
            cursor.execute('SELECT global_file_id FROM global_extracted_files')
            used_fileIDs = cursor.fetchall() #data: [{'submission_id': ___}, {'submission_id': ___},..]
            if not cursor.rowcount: #specifies number of rows that the last .execute*() outputs. If not means if the nu of rows == 0                this_submission_id = 1
                print ("No data yet")
                this_file_id = 1
            else:
                for i in used_fileIDs:
                    used_fileid_list.append(i['global_file_id']) 
                    used_fileid_list = sorted(used_fileid_list) #sort the list in ascending order
                    this_file_id = used_fileid_list[-1] + 1 #grab last id and add 1
            insertGlobalExtractedFile = "INSERT INTO global_extracted_files(global_file_id, global_data_file, global_file_name_in_server, global_data_format) VALUES (%s, %s, %s, %s)"
            cursor.execute( insertGlobalExtractedFile, (this_file_id, theGlobalDataFile, globalFullFilePathServer, global_data_extension))
            connection.commit()
            global_published_searched_data = {}

        elif request.form['submit_button'] == "search_data":
            print("the search button has been pressed.")

            firstValue=request.form['firstValue'] #labelled by the 'name': in form
            secondValue=request.form['secondValue']
            selectedProperty = request.form['selectedProperty'] 
            print ('firstValue: ', firstValue)
            print('secondValue: ', secondValue)
            print('selectedProperty: ', selectedProperty)
    
            #--for new tables format---------------------------------------------------
            #query for all submitted items in the database 
            queryForSearchedData = "SELECT * FROM global_published_data WHERE property = %s and property_value between %s and %s"
            searchPlaceholderStrings = (selectedProperty,firstValue, secondValue,) #will be used to replace the %s placeholder in the query execute
            cursor.execute(queryForSearchedData, searchPlaceholderStrings)
            global_published_searched_data = cursor.fetchall() #data: [{'submission_id': ___,'instrument_name':___...}, {'submission_id': ___, 'instrument_name':___...},..]  
            if cursor.rowcount > 80:
                warningMessage = "Warning: More than 80 results found. Limit your range further."
                print (warningMessage)
                global_published_searched_data = {}

            print ('global_published_searched_data: ',global_published_searched_data)
    
    else:
        global_published_searched_data = {}

    return render_template('upload_global_data.html', global_published_property_dict = global_published_property_dict, global_published_searched_data = global_published_searched_data, warningMessage = warningMessage)


@app.route('/view-global-data/<theProperty>', methods=['GET', 'POST'])
def view_global_data(theProperty):
    print ('theProperty: ', theProperty)
    #query for compostition value of each submission id 
    queryForSingleProperty = "SELECT * FROM global_published_data WHERE property = %s"
    PropertyString = (theProperty, ) #will be used to replace the %s placeholder in the query execute
    cursor.execute(queryForSingleProperty, PropertyString)
    global_published_data_dict = cursor.fetchall() #data: [{'submission_id': ___,'instrument_name':___...}, {'submission_id': ___, 'instrument_name':___...},..] 
    print ('global_published_data_dict: ', global_published_data_dict)
    return render_template('view_global_data.html', global_published_data_dict=global_published_data_dict)

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


        #nsertQueryContributer = "INSERT INTO contributor_details(contributor_name, lab_locn, research_grp, collecn_conditions) VALUES (%s,%s, %s, %s)"
        # cursor.execute( insertQueryContributer,(nameContributor,researchGroup,labLocation,conditions))
        
        # insertQueryMaterial = "INSERT INTO material_details(material_name, data_format, data_file, file_name_in_server, instrument, datatype) VALUES (%s, %s, %s, %s, %s, %s)"
        # cursor.execute( insertQueryMaterial,(materialName, extension ,theFile, f_name, instruName, chosenDataType))
        # connection.commit()
        # print(cursor.rowcount, "Record inserted successfully into table 2")

        # insertQuerySubmission = "INSERT INTO submission_details(privacy_option, file_type, source_data) VALUES (%s, %s, %s)"
        # cursor.execute(insertQuerySubmission,(privacyOption,'','Self-Collected'))
        # connection.commit() #rememeber to commit the record!
        # print(cursor.rowcount, "Record inserted successfully into table 3")