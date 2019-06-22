from flask import Flask,render_template,request,flash,redirect
import os
import sqlalchemy
from sqlalchemy import create_engine,inspect
from sqlalchemy import Column, Integer, String, Table, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import csv
from database import init_db, db_session, engine, Base
from models import User

import pandas as pd

UPLOAD_FOLDER = './uploads/'
ALLOWED_EXTENSIONS = set(['txt'])
TOTAL_COLUMN=0
return_elements=[]
field_names=[]
app = Flask('Elasticsearch Directory Search')
app.secret_key = b'_5#y2L"F4sdfsdf\n\xec]/'

@app.route('/')
@app.route('/index')
def index():
    init_db()
    return render_template('./index.html')

@app.route('/hello')
def hello():
    #print(User.query.all().toString())
    print(User.query.filter(User.name == 'admin').first())
    return 'Database'

@app.route('/search',methods=['POST','GET'])
def search():
    print("Calling")
    #print(User.query.all().toString())
    if request.method == 'POST':
        uploaded_files = request.files.getlist("file[]")
        single_file=request.files['file']
        print(single_file.filename)
        #sf = secure_filename(single_file.filename)
        #file_open = open(sf, "r")
        #print(file_open.read())
        destpath = os.path.dirname(os.path.realpath(__file__)) + "\\uploads"
        print(destpath)
        single_file.save(destpath,sf)        
        #print(uploaded_files)
        filenames = []
        for file in uploaded_files:
            
            #filename = secure_filename(file.filename)
            print("uploadss = "+file.filename)
            print( os.path.dirname(os.path.realpath(__file__)))
            #file.save(os.path.join(UPLOAD_FOLDER),file.filename)
            print(single_file.filename)
            file.save('D:/uploads/',single_file.filename)
            
    return render_template('./layout.html') 

@app.route('/get_csv',methods=['POST','GET'])
def get_csv():
    print(request)
    if request.method == 'POST':
        filepath=request.form["filepath"]
        print("filepath "+filepath)        

    #with open(os.path.join(UPLOAD_FOLDER)+"sample.csv", newline='') as f:        
        with open(filepath, newline='') as f:
            reader = csv.reader(f)
            row_count=0
            for row in reader:
                row_count=row_count+1
                if row_count==1:
                    TOTAL_COLUMN=len(row)  
                    for r1 in row:
                        field_names.append(r1)
                    first_row=row
                    return_elements.append({'total_column':TOTAL_COLUMN})
                #print(row)
                #print(len(row))
            reader = csv.DictReader(f)
            #print(reader.fieldnames)
            return_elements.append({'total_row':row_count})
            

    return render_template('./index.html',data=return_elements,fieldnames=first_row,create_table_schema=create_table_schema,csvpath=filepath)

@app.route('/create_table_schema',methods=['POST','GET'])
def create_table_schema():
    #dynamic_types = {'ID': sqlalchemy.types.INTEGER(),'Name':  sqlalchemy.types.VARCHAR(length=100), 'Date':  sqlalchemy.types.VARCHAR(length=30), 'Status':  sqlalchemy.types.VARCHAR(length=30)}
    dynamic_types = {}
    #print(field_names)
    import_status="Error in Importing"
    if request.method == 'GET':        
        tname = request.args["table_name_txt"]
        csv_path = request.args["hid_csvpath"] 
        print(request.args)        
        print(csv_path)
        dataframe_data = pd.read_csv(csv_path)
        print(request.args["import_option"])
        if request.args["import_option"] == "YES":
            i=0
            for ele in request.args:
                if ele[:9] == "datatypes":
                    tmp_type = request.args["datatypes"+str(i)]
                    tmp_name = request.args["inputdata"+str(i)]
                    if tmp_type == "string":                    
                        dynamic_types.update({tmp_name : sqlalchemy.types.VARCHAR(length=100)})
                        #dynamic_types[tmp_name] = 'sqlalchemy.types.VARCHAR(length=30)'
                    elif tmp_type == 'integer':
                        dynamic_types.update({tmp_name : sqlalchemy.types.INTEGER()})
                    elif tmp_type == 'boolean':
                        dynamic_types.update({tmp_name : sqlalchemy.types.BOOLEAN()})
                    elif tmp_type == 'float':
                        dynamic_types.update({tmp_name : sqlalchemy.types.FLOAT()})
                    elif tmp_type == 'unicode':
                        dynamic_types.update({tmp_name : sqlalchemy.types.Unicode()})
                    elif tmp_type == 'datetime':
                        dynamic_types.update({tmp_name : sqlalchemy.types.DATETIME()})
                    elif tmp_type == 'numeric':
                        dynamic_types.update({tmp_name : sqlalchemy.types.NUMERIC()})
                        #dynamic_types[tmp_name] = 'sqlalchemy.types.INTEGER()'
                    i=i+1
            print ("dynamic fields="+str(dynamic_types))
            #exit()

                    
            dataframe_data.to_sql(tname,con=engine,if_exists='replace',dtype=dynamic_types, index=False)

            print(dataframe_data)
            print(engine.execute("SELECT * FROM "+tname).fetchall())
            import_status="Successfully Imported"
        else:
            dataframe_data.to_sql(tname,con=engine,if_exists='replace', index=False)
            print("Else Condition")
            print(dataframe_data)
            print(engine.execute("SELECT * FROM "+tname).fetchall())
            import_status="Successfully Imported"
        
        
    return render_template('./index.html',import_status=import_status)

def bulkload_csv_data_to_database(engine, tablename, columns, data, sep=","):
    print("Start ingesting data into postgres ...")
    print("Table name: {table}".format(table=tablename))
    print("CSV schema: {schema}".format(schema=columns))
    conn = engine.connect().connection
    cursor = conn.cursor()
    cursor.copy_from(data, tablename, columns=columns, sep=sep, null='null')
    conn.commit()
    conn.close()
    print("Finish ingesting")

@app.route('/browse',methods=['POST','GET'])
def browse_tables():
    inspector = inspect(engine)
    table_names = {}
    print( request.args.get('tname'))
    column_details=""
    # if request.args.get('sql_query') == 'true':
    #     print(request.args.get("tname"))
    #     print(request.args["tname"])
    #     print(engine.execute("SELECT * FROM "+request.args["tname"]).fetchall())
    #     return render_template('./menu.html')
    if request.args.get('tname') != None:
        print("IF")
        tname=request.args.get('tname')
        for column in inspector.get_columns(tname):
            print(column)
            column_details += str(column) + "\n"
        results=engine.execute("SELECT * FROM "+tname).fetchall()
        return render_template('./menu.html',table_names=inspector.get_table_names(),column_details=column_details,table_results=results)
    else:            
        print("ELSE")
        for table_name in inspector.get_table_names():
            print(table_name)
            for column in inspector.get_columns(table_name):
                #print (column)
                #print("Column: %s" % column['name'])
                table_names.update({table_name:column})
        #print(Base.metadata.tables.keys())
        return render_template('./menu.html',table_names=table_names)
    
if __name__ == 'Elasticsearch Directory Search':
   app.run(debug = True)