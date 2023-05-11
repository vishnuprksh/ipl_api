"""
Module: Email Validation

This module provides functionality to validate email addresses using regular expressions.

The module includes a function `check_correct_email_format` which
takes an email address as input and checks if it
matches the expected format. It uses a regular expression pattern to perform the validation.

Example Usage:
--------------
>>> email = 'example@example.com'
>>> is_valid = check_correct_email_format(email)
>>> print(is_valid)
True

>>> email = 'invalid_email@'
>>> is_valid = check_correct_email_format(email)
>>> print(is_valid)
False

Dependencies:
-------------
- re: The regular expression module for pattern matching.

"""

import re

def check_correct_email_format(email):
    """
    Check if the provided email is in the correct format.

    This function uses regular expressions to validate the email format against a regex pattern.
    It checks if the email matches the pattern and returns True if it does, and False otherwise.

    Args:
        email (str): The email address to be checked.

    Returns:
        bool: True if the email is in the correct format, False otherwise.

    Raises:
        None.
    """
    regex_expression_for_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if re.fullmatch(regex_expression_for_email, email):
        return True
    else:
        return False
