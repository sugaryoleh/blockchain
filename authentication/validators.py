from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

from django.core.handlers.wsgi import WSGIRequest

import re


def validate_username(username: str, request: WSGIRequest) -> bool:
    users = User.objects.all()
    for user in users:
        if username == user.username:
            messages.add_message(request, messages.INFO, "User with username {} already exists".format(username))
            return False
    return True


def validate_password(password: str, request: WSGIRequest) -> bool:
    min_len = 3
    if len(password) < min_len:
        messages.add_message(request, messages.INFO, "The password must minimum 8 digits long")
        return False
    elif not any(char.isdigit() for char in password):
        messages.add_message(request, messages.INFO, "The password must contain at least 1 digit")
        return False
    elif not any(char.isalpha() for char in password):
        messages.add_message(request, messages.INFO, "The password must contain at least 1 letter")
        return False
    else:
        return True


def validate_first_and_last_name(name: str, request: WSGIRequest) -> bool:
    max_name_length = 50
    if name == "":
        messages.add_message(request, messages.INFO, "First and last names cannot be blank")
        return False
    if len(name) > 50:
        messages.add_message(request, messages.INFO,
                             "First and last names' length must be less than {}".format(max_name_length))
        return False
    return True


def validate_email(email: str, request: WSGIRequest) -> bool:
    pat = r"^\S+@\S+\.\S+$"
    if re.match(pat, email):
        return True
    messages.add_message(request, messages.INFO, "Email address doesn't meet requirements")
    return False


def validate_phone(phone: str, request: WSGIRequest) -> bool:
    pat = r'^\+?1?\d{11,12}$'
    if re.match(pat, phone):
        return True
    messages.add_message(request, messages.INFO, "Phone doesn't meet requirements")
    return False


def validate_account_data_register(first_name: str, last_name: str, phone: str, username: str, password: str,
                                   confirmed_password: str, request: WSGIRequest) -> bool:
    for u in get_user_model().objects.all():
        if username == u.username:
            messages.add_message(request, messages.INFO, "Such username already exists")
            return False
    if password != confirmed_password:
        messages.add_message(request, messages.INFO, "Passwords do not match")
        return False

    validators = [validate_password(password, request),
                  validate_first_and_last_name(first_name, request),
                  validate_first_and_last_name(last_name, request),
                  validate_username(username, request),
                  validate_phone(phone, request),
                  ]

    if all(validator for validator in validators):
        return True

    return False


def validate_account_data_update(first_name: str, last_name: str, email: str, phone: str, request: WSGIRequest) -> bool:
    validators = [validate_first_and_last_name(first_name, request),
                  validate_first_and_last_name(last_name, request),
                  validate_email(email, request),
                  validate_phone(phone, request),
                  ]

    if all(validator for validator in validators):
        return True

    return False
