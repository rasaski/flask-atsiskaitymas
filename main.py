"""
Uzduotys:
1.(3) Surasti, isvardinti ir pataisyti visas projekte rastas klaidas zemiau, uz bent 5 rastas ir pataisytas pilnas balas:
    a) Sign up formoje ir def sign_up() nėra last_name
    b) class User(db.Model). Jame prie first_name nurodyta Integer, ne String
    c) neimportuotas UserMixin, logout_user
    d) def sign_in neturi metodų GET ir POST
    e) neteisinga eilutė: user = User.query.filter_by(first_name=form.email_address.data).first()
    f) neteisinga eilutė:  def update_account_information  if request.method == 'POST'. ir toliau visur email surašyta: form.email_address.data = current_user.email_address
        form.first_name.data = current_user.email_address
        form.last_name.data = current_user.email_address
    g) neįrašyta funkcija išsiregistravimo: def sign_out(): logout_user()
2.(7) Praplesti aplikacija i bibliotekos registra pagal apacioje surasytus reikalavimus:
    a)(1) Naudojant SQLAlchemy klases, aprasyti lenteles Book, Author su pasirinktinais atributais su tinkamu rysiu -
        vienas autorius, gali buti parases daug knygu, ir uzregistruoti juos admin'e
    b)(2) Sukurti (papildomus) reikiamus rysius tarp duombaziniu lenteliu, kad atitiktu zemiau pateiktus reikalavimus
    c) Sukurti puslapius Available Books ir My Books:
        i)(2) Available Books puslapis
            - isvesti bent knygos pavadinima ir autoriu
            - turi buti prieinamas tik vartotojui prisijungus,
            - rodyti visas knygas, kurios nera pasiskolintos
            - tureti mygtuka ar nuoroda "Borrow" prie kiekvienos knygos, kuri/ia paspaudus, knyga yra priskiriama
              varototojui ir puslapis perkraunamas
              (del paprastumo, sakome kad kiekvienos i sistema suvestos knygos turima lygiai 1)
        ii)(2) My Books puslapis
            - turi matytis ir buti prieinamas tik vartotojui prisijungus
            - rodyti visas knygas, kurios yra pasiskolintos prisijungusio vartotojo
            - salia kiekvienos knygos mygtuka/nuoroda "Return", kuri/ia paspaudus, knyga grazinama i biblioteka ir
              perkraunamas puslapis
    f)(2) Bonus: praplesti aplikacija taip, kad bibliotekoje kiekvienos knygos galetu buti
        daugiau negu vienas egzempliorius
Pastabos:
    - uzstrigus su pirmaja uzduotimi, galima paimti musu paskutini flask projekto template
        ir ten atlikti antra uzduoti
    - nereikalingus templates geriau panaikinti ar persidaryti, kaip reikia. Tas pats galioja su MyTable klase
    - antram vartotojui prisijungus, nebeturi matytis kyngos, kurios buvo pasiskolintos pirmojo vartotojo
        nei prie Available Books, nei prie My Books
    - visam administravimui, pvz. knygu suvedidimui galima naudoti admin
    - sprendziant bonus uzduoti, apsvarstyti papildomos lenteles isivedima
"""

from flask import Flask, render_template, redirect, url_for, flash, request
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_bcrypt import Bcrypt
from flask_login import AnonymousUserMixin, LoginManager, login_user, current_user, login_required, UserMixin, \
    logout_user
from flask_sqlalchemy import SQLAlchemy
import forms
from flask_migrate import Migrate

app = Flask(__name__)


class MyAnonymousUserMixin(AnonymousUserMixin):
    is_admin = False


login_manager = LoginManager(app)

login_manager.login_view = 'sign_in'
login_manager.login_message = 'Please login to access this page.'
login_manager.login_message_category = 'info'
login_manager.anonymous_user = MyAnonymousUserMixin

admin = Admin(app)

bcrypt = Bcrypt(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite?check_same_thread=False'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '(/("ZOHDAJK)()kafau029)ÖÄ:ÄÖ:"OI§)"Z$()&"()!§(=")/$'

db = SQLAlchemy(app)
Migrate(app, db)


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email_address = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)


class MyTable(db.Model):
    __tablename__ = 'my_table'
    id = db.Column(db.Integer, primary_key=True)
    my_column = db.Column(db.String(100), nullable=False)


class Authors(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    books = db.relationship('Book', backref='authors')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


class Book(db.Model):
    __tablename__ = 'book'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    authors_id = db.Column(db.Integer, db.ForeignKey('authors.id'))
    availables = db.relationship('AvailableBooks', backref='book')

    def __init__(self, title, authors_id):
        self.title = title
        self.authors_id = authors_id

    def __repr__(self):
        return self.title


class AvailableBooks(db.Model):
    __tablename__ = 'available_books'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id', 'authors.id'))


db.create_all()


class MyModelView(ModelView):

    def is_accessible(self):
        return current_user.is_admin


admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(MyTable, db.session))
admin.add_view(MyModelView(Authors, db.session))
admin.add_view(MyModelView(Book, db.session))


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/add_form', methods=['GET', 'POST'])
def add_form():
    form = forms.AddForm()
    if form.validate_on_submit():
        my_table = MyTable(my_column=form.my_column.data)
        db.session.add(my_table)
        db.session.commit()
        return render_template('success.html')
    return render_template('add_form.html', form=form)


@app.route('/show')
@login_required
def show():
    data = MyTable.query.all()
    return render_template('show.html', data=data)


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    form = forms.SignUpForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password1.data).decode()
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email_address=form.email_address.data,
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash(f'Welcome, {current_user.first_name}', 'success')
        return redirect(url_for('home'))
    return render_template('sign_up.html', form=form)


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    form = forms.SignInForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email_address=form.email_address.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash(f'Welcome, {current_user.first_name}', 'success')
            return redirect(request.args.get('next') or url_for('home'))
        flash(f'User or password does not match', 'danger')
        return render_template('sign_in.html', form=form)
    return render_template('sign_in.html', form=form)


@app.route('/update_account_information', methods=['GET', 'POST'])
def update_account_information():
    form = forms.UpdateAccountInformationForm()
    if request.method == 'GET':
        form.email_address.data = current_user.email_address
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
    if form.validate_on_submit():
        current_user.email_address = form.email_address.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        db.session.commit()
        flash('User information updated', 'success')
        return redirect(url_for('update_account_information'))
    return render_template('update_account_information.html', form_in_html=form)


@app.route('/sign_out')
def sign_out():
    logout_user()
    flash('Goodbye, see you next time', 'success')
    return render_template('home.html')


@app.route('/add_authors', methods=['GET', 'POST'])
def add_authors():
    form = forms.AuthorsForm()
    if form.validate_on_submit():
        authors = Authors(name=form.name.data)
        db.session.add(authors)
        db.session.commit()
        return render_template('add_authors.html', form=form, message='Success')
    return render_template('add_authors.html', form=form)


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    form = forms.BookForm()
    if form.validate_on_submit():
        book = Book(title=form.title.data, authors_id=form.authors.data.id)
        db.session.add(book)
        db.session.commit()
        return render_template('add_book.html', form=form, message='Success')
    return render_template('add_book.html', form=form)


@app.route('/choose_available_book', methods=['GET', 'POST'])
@login_required
def choose_available_books():
    form = forms.AvailableBookForm()
    if form.validate_on_submit():
        available_book = AvailableBooks(book_id=form.book_id.data)
        db.session.add(available_book)
        db.session.commit()
        return render_template('available_books.html', form=form, message='success')
    return render_template('choose_available_book.html', form=form)


@app.route('/available_books')
@login_required
def available_books():
    data = AvailableBooks.query.all()
    return render_template('available_books.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)
