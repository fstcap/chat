from flask_wtf import FlaskForm
from wtforms import Form, StringField, validators, PasswordField
from wtforms.fields.html5 import TelField

class RegistrationForm(Form):
    username = StringField(
        label='用户名', 
        validators=[
            validators.Regexp(regex=r'\w{2,20}', message='2~20字母数字及下划线')], 
        id='inputUsername')
    mobile_number = TelField(
        label='手机', 
        validators=[validators.Length(min=11, max=11, message='请输入正确的手机号码')], 
        id='inputTelNum')
    password = PasswordField(
        label='密码', 
        validators=[
            validators.Regexp(regex=r'^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{8,20}', message='8~16字母数字'),
            validators.EqualTo('confirm', message='密码不匹配')
        ],
        id='inputPassword')
    confirm = PasswordField(
        label='确认密码',
        id='inputConfirm')
