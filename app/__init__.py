from flask import Flask,render_template,request,session,redirect,flash,url_for,abort,send_file
from app.src.helpers.database import mongo
from app.src.helpers.config import config
from app.src.helpers.validations import validate_user_email,validate_user_token,allowed_file
from passlib.hash import pbkdf2_sha256
from datetime import datetime
from app.src.helpers.utils import get_random_string,get_user_documets,get_user_info,get_del_documets
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
import os



app = Flask(__name__)
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

mongo.init_app(app, uri=config['mongo_uri']) 

app.secret_key = '\xcfdg\xcd\xed\xea\x9bF\xadBf/\x00y\x9f\xc9'
app.config['UPLOAD_FOLDER']=config['UPLOAD_FOLDER']

""" routes """
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/home')
def home():
    fileerror=None
    uploadSuccess=None
    if not 'userToken' in session:
        return redirect('/login')

    # validate user token
    if not validate_user_token(session):
        session.pop('userToken',None)
        session['SignInSuccess']='You must Login'
        return redirect('/login')


    
    if 'file_error' in session:
        
        fileerror=session['file_error']
        
        session.pop('file_error',None)
        
    user_files=get_user_documets(session)
    # print(user_files)
    user=get_user_info(session)
    
    if 'upload_success' in session:
        uploadSuccess=session['upload_success']
        session.pop('upload_success',None)
    
    return render_template('dashboard.html',user_files=user_files,user=user,error=fileerror,success=uploadSuccess)

@app.route('/login/')
def user_login():
    SignUpSuccess=None
    SignInSuccess=None
    if 'SignUpSuccess' in session:
        SignUpSuccess=session['SignUpSuccess']
        session.pop('SignUpSuccess',None)
        return render_template('login.html',s1=SignUpSuccess)
    if 'SignInSuccess' in session:
        SignInSuccess=session['SignInSuccess']
        session.pop('SignInSuccess',None)
        return render_template('login.html',s2=SignInSuccess)
    '''validating user token for login session'''
    if  'userToken' in session:
        if validate_user_token(session):
            return redirect('/home')
    
    return render_template('login.html',s1=SignUpSuccess,s2=SignInSuccess)

@app.route('/check_login', methods=['Post'])
def check_login():
    
    usr_email=request.form['email5']
    usr_passwd=request.form['password5']
    user = mongo.db.Users.find_one({
      "email": usr_email
    })
    
    if not (user and pbkdf2_sha256.verify(usr_passwd, user['password'])):
        session['SignInSuccess']='Incorrect Login Credentials'
        return redirect('/login')

    random_string=get_random_string()
    randomSessionHash=pbkdf2_sha256.encrypt(random_string)

    # generate token 
    _ =mongo.db.User_Tokens.insert_one(
        {
            'userId':user['_id'],
            'sessionHash':randomSessionHash,
            'createdAt':datetime.utcnow()
        }
    )
    session['userToken']=randomSessionHash

    return redirect('/home')

# this route will render the signup page
@app.route('/signup/')
def user_signup():
    error=None
    if 'error' in session:
        error=session['error']
        session.pop('error',None)
    return render_template('signup.html',error=error)

    

# this route will handle the signup
@app.route('/handle_signup',methods=['POST'])
def handle_signup():
    usr_email=request.form['email5']
    usr_passwd=request.form['password5']
    usr_passwd=pbkdf2_sha256.encrypt(usr_passwd)
    
    # check if email already exist 
    
    
    if  validate_user_email(usr_email)>0:
        session['error']='Email already exist'
        return redirect('/signup')
    
    # create a user record in the database
    user_record={
        'email':usr_email,
        'password':usr_passwd,
        'name':'',
        'lastlogindate':None,
        'created_at': datetime.utcnow(),
        'updated_at':datetime.utcnow(),
    }
    mongo.db.Users.insert_one(user_record)

    # Redirect to the login page
    session['SignUpSuccess']='Account Created Successfully'
    return redirect('/login')
   

@app.route('/logout/')
def logout_user():
    session.pop('userToken',None )
    session['SignUpSuccess']='SuccessFully Logged out.'
    return redirect('/login')

@app.route('/handle_file_upload/', methods=['GET','POST'])
def upload_file():
    if request.method == 'POST':
        if 'UploadedFile' not in request.files:
            
            session['file_error']='no file'
            return redirect('/')
        print(request.files)
        file = request.files['UploadedFile']
        if file.filename == '':
            session['file_error']='No File Selected'
            return redirect('/')
        if not allowed_file(file.filename):
            print('invalid')
            session['file_error']='Invalid file'
            return redirect('/')
        
        filename=secure_filename(file.filename)
        filePath=os.path.join(app.config['UPLOAD_FOLDER'],filename)
        file.save(filePath)
        file_size = os.path.getsize(filePath)
        file_size=file_size//1000
        extension=filename.rsplit('.', 1)[1].lower()    
        user=get_user_info(session)
        timestamp= str(datetime.utcnow())
        print(timestamp)
        user_file_uploads={
            
        
                "userId" : user['_id'],
                "originalFileName" : file.filename,
                "fileName":filename,
                "fileType" : extension,
                "fileHash" : "",
                "fileSize" : str(file_size) +'Kb',
                "filePath" : filePath,
                "isActive" : True,
                "createdAt" : timestamp

        }
        mongo.db.Files.insert_one(user_file_uploads)
        session['upload_success']='File Uploaded Successfully'    
        
        return redirect('/home')


@app.route('/download/<fileId>',methods=['GET'])  
def download(fileId):
    print("file id is:",fileId)
    file_object=None
    try:
        file_object=mongo.db.Files.find_one({
            '_id':ObjectId(fileId)
        })   
    except:  
        print('code has reached except')
        
    
    if file_object is None:
        return abort(404)

    return render_template('download.html',file=file_object)


@app.route('/download/file',methods=['GET'])
def download_file():
    if 'id' in request.args:
        fileId=request.args['id']
    else:
        return abort(404)
    file_object=None
    fileId=ObjectId(fileId)
    print(type(fileId))
    try:
        file_object=mongo.db.Files.find_one({
            '_id':fileId
        })   
    except:  
        print('code has reached except')
    if file_object is None:
        return abort(404)
    print(file_object)
    file_path=file_object['filePath']
    return send_file(file_path,as_attachment=True)

@app.route('/delete/<fileId>')
def delete(fileId):
    if 'del' in request.args:        
        
        try:
            fileId=ObjectId(fileId)
            mongo.db.Files.delete_one({'_id':fileId})
        except:
            return abort(404)
        return redirect(url_for('trash_bin'))
    fileId=ObjectId(fileId)
    mongo.db.Files.update_one({'_id': fileId},{"$set":{'isActive':False}})
    return redirect(url_for('home'))

@app.route('/bin')
def trash_bin():
    deleted=get_del_documets(session)
    
   
    return render_template('recyclebin.html',user_files=deleted)




@app.route('/restore/<fileid>')
def restore(fileid):
    fileId=ObjectId(fileid)
    mongo.db.Files.update_one({'_id': fileId},{"$set":{'isActive':True}})
    return redirect(url_for('trash_bin'))
