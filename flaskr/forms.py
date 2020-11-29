from wtforms import Form, StringField, validators, PasswordField, DateField, RadioField, BooleanField
from wtforms.fields.html5 import EmailField

class RegistrationForm(Form):
    username = StringField(
        validators=[
            validators.Regexp(regex=r'\w{2,20}', message='请输入正确用户名')],
        render_kw={'placeholder':'用户名'},
        description='2~20字母数字及下划线',
        id='inputUsername')
    email = EmailField(
        validators=[validators.Regexp(regex=r'.+@.+\.com$', message='请输入正确邮箱')],
        render_kw={'placeholder':'you@example.com'},
        description='电子邮箱',
        id='inputEmail')
    password = PasswordField(
        validators=[
            validators.Regexp(regex=r'^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{8,20}', message='请输入正确密码'),
            validators.EqualTo('confirm', message='密码不匹配')
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
            validators.Regexp(regex=r'\w{2,20}', message='2~20字母数字及下划线')], 
        render_kw={'placeholder': '用户名'},
        id='inputUsername')
    password = PasswordField(
        validators=[
            validators.Regexp(regex=r'^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{8,20}', message='8~16字母数字'),
        ],
        render_kw={'placeholder': '密码'},
        id='inputPassword')

class InformationForm(Form):
    username = StringField(
        label='用户名',
        validators=[
            validators.Regexp(regex=r'\w{2,20}', message='请输入正确用户名')],
        render_kw={'placeholder':'Bruce'},
        description='2~20字母数字及下划线',
        id='inputUsername')
    sex = RadioField(
        label='性别',
        choices=[
        ('male', '男'), ('female', '女')],
        id='inputSex')
    email = EmailField(
        label='电子邮箱',
        validators=[validators.Regexp(regex=r'.+@.+\.com$', message='请输入正确邮箱')],
        render_kw={'placeholder':'you@example.com'},
        description='电子邮箱',
        id='inputEmail')
    birthdate = DateField(
        label='生日',
        render_kw={'placeholder': '2020-01-01'},
        description='出生年月日')
    
class PWInformationForm(InformationForm):
    whether_password = BooleanField(
        label='是否修改密码',
        id="inputCheckbox")
    password = PasswordField(
        label='新密码',
        validators=[
            validators.Regexp(regex=r'^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{8,20}', message='请输入正确密码'),
            validators.EqualTo('confirm', message='密码不匹配')
        ],
        description='8~16字母数字',
        id='inputPassword')
    confirm = PasswordField(
        label='确认密码',
        description='再次输入密码',
        id='inputConfirm')
