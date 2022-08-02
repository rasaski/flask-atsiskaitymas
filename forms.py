from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from flask_login import current_user
import main
from wtforms_sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from main import Authors, Book


class AddForm(FlaskForm):
    my_column = StringField('My Column', [DataRequired()])
    submit = SubmitField('Submit')


class SignUpForm(FlaskForm):
    email_address = StringField('Email Address', [DataRequired()])
    first_name = StringField('First Name', [DataRequired()])
    last_name = StringField('Last name')
    password1 = PasswordField('Password', [DataRequired()])
    password2 = PasswordField('Password confirm', [DataRequired(), EqualTo('password1', 'Passwords must match')])
    submit = SubmitField('Sign Up')

    def validate_email_address(self, email_address):
        user = main.User.query.filter_by(email_address=self.email_address.data).first()
        if user:
            raise ValidationError('Email already exists. Sign in or use another email address.')


class SignInForm(FlaskForm):
    email_address = StringField('Email Address', [DataRequired()])
    password = PasswordField('Password', [DataRequired()])
    submit = SubmitField('Sign In')


class UpdateAccountInformationForm(FlaskForm):
    email_address = StringField('Email Address', [DataRequired()])
    first_name = StringField('First Name', [DataRequired()])
    last_name = StringField('Last Name')
    submit = SubmitField('Update Info')

    def validate_email_address(self, email_address):
        if current_user.email_address != self.email_address.data:
            user = main.User.query.filter_by(email_address=self.email_address.data).first()
            if user:
                raise ValidationError('Email already exists. Sign in or use another email address.')


class AuthorsForm(FlaskForm):
    name = StringField('Name')
    submit = SubmitField('Submit')


class BookForm(FlaskForm):
    title = StringField('Title')
    authors = QuerySelectField(query_factory=Authors.query.all, allow_blank=True, get_label="name",
                               get_pk=lambda obj: str(obj))
    submit = SubmitField('Submit')


class AvailableBookForm(FlaskForm):
    #book_id = QuerySelectMultipleField(query_factory=Book.query.all, allow_blank=True, get_label="title",
    #                           get_pk=lambda obj: str(obj))
    book_id = QuerySelectMultipleField(query_factory=Book.query.all, allow_blank=True, get_label="title")
    book_ids = QuerySelectMultipleField(query_factory=Book.query.all, allow_blank=True, get_label="authors")
    submit = SubmitField('Submit')
