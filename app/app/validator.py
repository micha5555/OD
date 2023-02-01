import re

def validate_register_data(login, password, repeated_password):
    print(login)
    print(password)
    print(repeated_password)
    if password != repeated_password:
        return False
    else:
        return validate_login_and_password(login, password)

def validate_login_and_password(login, password):
    if login is None or password is None:
        return False
    if len(login) == 0 or len(password) == 0:
        return False
    # only letters and numbers
    login_pattern = "^[a-zA-Z0-9]+$"
    # at least 8 characters, at least one uppercase letter, at least one lowercase letter, at least one number and at least one special character
    password_pattern = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$"
    if re.match(login_pattern, login) and re.match(password_pattern, password):
        return True
    else:
        return False
    
# def validate_if_note_is_potential_xss(note):
#     regex = "^ $"