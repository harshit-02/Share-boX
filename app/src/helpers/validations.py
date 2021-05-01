# from email_validator import validate_email, EmailNotValidError
from app.src.helpers.database import mongo
ALLOWED_EXTENSIONS = ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','mp4']
def validate_user_email(usr_email):
    # try:
    #     # Validate.
    #     is_valid = True
    #     valid = validate_email(usr_email)

    #     # Update with the normalized form.
    #     email = valid.email
        
    # except EmailNotValidError as e:
    #     # email is not valid, exception message is human-readable

    #     is_valid = False
    # return is_valid
    """check if user email already exist"""
    count=mongo.db.Users.count_documents({'email':usr_email})
    return count

def validate_user_token(session):
    db_token=mongo.db.User_Tokens.find_one({
        'sessionHash': session['userToken']
    })
    if db_token is None:
        return False
    return True
    
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS