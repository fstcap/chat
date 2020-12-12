import re
from wtforms import Form, StringField, validators, PasswordField, DateField, RadioField, BooleanField, ValidationError
from wtforms.fields.html5 import EmailField

username_regex = r'^\w{2,20}$'
email_regex = r'^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$'
password_regex = r'^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{8,20}'

username_message = '请输入正确用户名'
email_message = '请输入正确邮箱'
password_message = '请输入正确密码'
confirm_message = '密码不匹配'

class RegistrationForm(Form):
    username = StringField(
        validators=[
            validators.Regexp(regex=username_regex, message=username_message)],
        render_kw={'placeholder':'用户名'},
        description='2~20字母数字及下划线',
        id='inputUsername')
    email = EmailField(
        validators=[validators.Regexp(regex=email_regex, message=email_message)],
        render_kw={'placeholder':'you@example.com'},
        description='电子邮箱',
        id='inputEmail')
    password = PasswordField(
        validators=[
            validators.Regexp(regex=password_regex, message=password_message),
            validators.EqualTo('confirm', message=confirm_message)
        ],
        render_kw={'placeholder':'密码'},
        description='8~16字母数字',
        id='inputPassword')
    confirm = PasswordField(
        render_kw={'placeholder':'确认密码'},
        description='再次输入密码',
        id='inputConfirm')

class LoginForm(Form):
    username = StringField(
        validators=[
            validators.Regexp(regex=username_regex, message=username_message)], 
        render_kw={'placeholder': '用户名'},
        id='inputUsername')
    password = PasswordField(
        validators=[
            validators.Regexp(regex=password_regex, message=password_message),
        ],
        render_kw={'placeholder': '密码'},
        id='inputPassword')

class InformationForm(Form):
    username = StringField(
        label='用户名',
        validators=[
            validators.Regexp(regex=username_regex, message=username_message)],
        render_kw={'placeholder':'Bruce'},
        description='2~20字母数字及下划线',
        id='inputUsername')
    sex = RadioField(
        label='性别',
        validators=[
            validators.Regexp(regex=r"^(male|female)$", message='Input error')],
        choices=[
        ('male', '男'), ('female', '女')],
        id='inputSex')
    email = EmailField(
        label='电子邮箱',
        validators=[validators.Regexp(regex=email_regex, message=email_message)],
        render_kw={'placeholder':'you@example.com'},
        description='电子邮箱',
        id='inputEmail')
    birthdate = DateField(
        label='生日',
        validators=[validators.DataRequired(message='请输入正确时间格式')],
        render_kw={'placeholder': '2020-01-01'},
        description='出生年月日')
    check_password = BooleanField(
        label='是否修改密码',
        id="inputCheckbox")
    password = PasswordField(
        label='新密码',
        validators=[
            validators.EqualTo('confirm', message=confirm_message)
        ],
        description='8~16字母数字',
        id='inputPassword')
    confirm = PasswordField(
        label='确认密码',
        description='再次输入密码',
        id='inputConfirm')
    def validate_password(self, field):
        if 'checked' in  str(self.check_password) and re.match(password_regex, field.data) is None:
            raise ValidationError(password_message)
