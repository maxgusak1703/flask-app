from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from flask_login import current_user
from models import User

class RegistrationForm(FlaskForm):
    username = StringField("Ім’я", validators=[ DataRequired(message="Будь ласка, введіть ім’я"),
        Length(min=2, max=20, message="Ім’я має бути від 2 до 20 символів")
    ])
    email = StringField('Email', validators=[
        DataRequired(message="Будь ласка, введіть електронну пошту"),
        Email(message="Будь ласка, введіть коректну електронну адресу")
    ])
    category = SelectField('Категорія', choices=[
        ('parents', 'Батьки'),
        ('students', 'Учні'),
        ('graduates', 'Випускники'),
    ], validators=[DataRequired(message="Будь ласка, оберіть категорію")])
    password = PasswordField('Пароль', validators=[
        DataRequired(message="Будь ласка, введіть пароль")
    ])
    confirm_password = PasswordField('Підтвердження пароля', validators=[
        DataRequired(message="Будь ласка, підтвердтвердьте пароль"),
        EqualTo('password', message="Паролі не збігаються")
    ])
    submit = SubmitField('Зареєструватися')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Це ім’я користувача вже зайнято.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Ця електронна пошта вже використовується.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message="Будь ласка, введіть електронну пошту"),
        Email(message="Будь ласка, введіть коректну електронну адресу")
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message="Будь ласка, введіть пароль")
    ])
    remember = BooleanField('Запам’ятати мене')
    submit = SubmitField('Увійти')

class ProfileForm(FlaskForm):
    username = StringField('Ім’я користувача', validators=[
        DataRequired(message="Будь ласка, введіть ім’я користувача"),
        Length(min=2, max=20, message="Ім’я користувача має бути від 2 до 20 символів")
    ])
    email = StringField('Електронна пошта', validators=[
        DataRequired(message="Будь ласка, введіть електронну пошту"),
        Email(message="Будь ласка, введіть коректну електронну адресу")
    ])
    category = SelectField('Категорія', choices=[
        ('admin', 'Адміністратор'),
        ('parents', 'Батьки'),
        ('students', 'Учні'),
        ('graduates', 'Випускники')
    ], validators=[DataRequired(message="Будь ласка, оберіть категорію")])
    password = PasswordField('Новий пароль', validators=[Optional()])
    confirm_password = PasswordField('Підтвердити новий пароль', validators=[
        Optional(),
        EqualTo('password', message='Паролі не збігаються')
    ])
    profile_image = FileField('Фотографія профілю', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], message='Дозволено лише файли формату JPG, PNG або JPEG'),
        Optional()
    ])
    submit = SubmitField('Зберегти зміни')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Це ім’я користувача вже зайнято.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Ця електронна пошта вже використовується.')

class ContactForm(FlaskForm):
    name = StringField('Ім’я', validators=[
        DataRequired(message="Будь ласка, введіть ім’я"),
        Length(min=2, max=100, message="Ім’я має бути від 2 до 100 символів")
    ])
    email = StringField('Електронна пошта', validators=[
        DataRequired(message="Будь ласка, введіть електронну пошту"),
        Email(message="Будь ласка, введіть коректну електронну адресу")
    ])
    subject = StringField('Тема', validators=[
        DataRequired(message="Будь ласка, введіть тему"),
        Length(min=2, max=150, message="Тема має бути від 2 до 150 символів")
    ])
    message = TextAreaField('Повідомлення', validators=[
        DataRequired(message="Будь ласка, введіть повідомлення")
    ])
    submit = SubmitField('Надіслати')

class TestimonialForm(FlaskForm):
    name = StringField('Ім’я', validators=[
        DataRequired(message="Будь ласка, введіть ім’я"),
        Length(min=2, max=100, message="Ім’я має бути від 2 до 100 символів")
    ])
    email = StringField('Електронна пошта', validators=[
        DataRequired(message="Будь ласка, введіть електронну пошту"),
        Email(message="Будь ласка, введіть коректну електронну адресу")
    ])
    category = SelectField('Категорія', choices=[
        ('parents', 'Батьки'),
        ('students', 'Учні'),
        ('graduates', 'Випускники'),
    ], validators=[DataRequired(message="Будь ласка, оберіть категорію")])
    text = TextAreaField('Відгук', validators=[
        DataRequired(message="Будь ласка, введіть відгук")
    ])
    submit = SubmitField('Додати відгук')