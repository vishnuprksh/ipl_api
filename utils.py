import re

# Function to check email is correct or not
def check_correct_email_format(email):
    regex_expression_for_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if re.fullmatch(regex_expression_for_email,email):
        return True
    else:
        return False
