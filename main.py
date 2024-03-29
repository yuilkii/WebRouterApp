import datetime

from flask import render_template, Flask
from flask import redirect
from flask import request
from flask import flash
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from sqlalchemy import orm
from flask_sqlalchemy import SQLAlchemy
import sqlite3
from flask import session
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField
from wtforms.validators import DataRequired
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'zyxw4342vut123srqpo89nmlkjihgf78213123edc1233ba'

app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///server.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

user_name = 'Your Profile'
cnt_enters = 1
cnt_marshs = 1
age_acc = 1


class User(db.Model):  # таблица пользователей
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True)
    name = db.Column(db.String
                     , nullable=True)
    hashed_password = db.Column(db.String, nullable=True)

    created_date = db.Column(db.DateTime,
                             default=datetime.datetime.now)

    profiles = orm.relationship("Profile")

    def __init__(self, name: str, hashed_password: str):
        self.name = name
        self.hashed_password = hashed_password

    def __repr__(self):
        return f'Пользователь {self.name}.' \
               f'Пароль {self.hashed_password}' \
               f'Дата создания {self.created_date}'


class News(db.Model):  # таблица новостей
    __tablename__ = 'news'

    id = db.Column(db.Integer,
                   primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=True)
    content = db.Column(db.String, nullable=True)

    is_private = db.Column(db.Boolean, default=True)

    def __init__(self, title: str, content: str, is_private: bool):
        self.title = title
        self.content = content
        self.is_private = is_private

    def __repr__(self):
        return f'Заголовок {self.title}' \
               f'Контент {self.content}' \
               f'Приватность {self.is_private}'


class Profile(db.Model):  # таблица профилей
    __tablename__ = 'profiles'

    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True)
    age = db.Column(db.Integer, nullable=True)
    city = db.Column(db.String(100), nullable=True)
    cnt_ent = db.Column(db.Integer, nullable=True, default=0,
                        autoincrement=True)
    cnt_marsh = db.Column(db.Integer, nullable=True, default=0,
                          autoincrement=True)
    age_acc = db.Column(db.Integer, nullable=True, default=1,
                        autoincrement=True)
    user_id = db.Column(db.Integer,
                        db.ForeignKey("users.id"))

    user = orm.relationship('User')

    def __init__(self, age: int, city: str, cnt_ent: int, cnt_marsh: int, age_acc: int):
        self.age = age
        self.city = city
        self.cnt_ent = cnt_ent
        self.cnt_marsh = cnt_marsh
        self.age_acc = age_acc

    def __repr__(self):
        return f'Возраст {self.age}' \
               f'Город {self.city}' \
               f'Кол-во входов на сайт {self.cnt_ent}' \
               f'Кол-во построенных маршрутов {self.cnt_marsh}' \
               f'Кол-во дней на сайте {self.age_acc}'


@app.route('/')
def index():
    session['name'] = ''
    session['login'] = 0
    return "index"


@app.route('/login', methods=['POST', 'GET'])
def login():  # авторизация пользователя
    global user_name
    if 'login' in session and session['login'] == 1:
        return redirect('/about')
    if request.method == 'GET':
        return render_template('login.html')
    else:
        name = request.form.get('login')
        password = request.form.get('password')
        user = User.query.filter_by(name=name).first()
        if not user or not check_password_hash(user.hashed_password, password):
            flash('Something went wrong'
                  'Please check your login or password')
            return render_template('login.html')
        else:
            user_name = name
            session['login'] = 1
            print(session['login'])
            return redirect('/about')


@app.route('/signup', methods=['POST', 'GET'])
def signup():  # регистрация пользователя
    if 'login' in session and session['login'] == 1:
        return redirect('/about')
    if request.method == 'GET':
        return render_template('registration.html')
    else:
        name = request.form.get('login')
        password = request.form.get('password')
        user = User.query.filter_by(
            name=name).first()
        if user:
            flash('You already have a account')
            return redirect('/login')
        new_user = User(name=name, hashed_password=generate_password_hash(password, method='sha256'))
        db.session.add(new_user)
        db.session.commit()
        return render_template('login.html')


@app.route('/about')  # главная страница
def about():
    global cnt_enters
    cnt_enters += 1
    print(session['login'])
    if session['login'] == 1:
        return render_template('site_back.html', avatar_name=user_name, login='profile')
    return render_template('site_back.html', avatar_name=user_name, login='signup')


UPLOAD_FOLDER = 'C:\\Users\\dimae\\PycharmProjects\\WebRouterApp\\static\\avatars'
# путь к аватаркам, изменяем при надобности
# расширения файлов, которые разрешено загружать
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):  # загрузка файлов
    """ Функция проверки расширения файла """
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/profile', methods=['GET', 'POST'])
def upload_file():
    global cnt_marshs, cnt_enters, age_acc
    if request.method == 'GET':
        return render_template('profile.html', name=user_name, cnt_enters=cnt_enters, cnt_marshs=cnt_marshs,
                               age=age_acc)
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Не могу прочитать файл')
            return redirect(request.url)
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], f'{user_name}.jpg'))  # id + .jpg
            render_template('site_back.html', avatar_name=filename)
            return render_template('profile.html', name=user_name, cnt_enters=cnt_enters, cnt_marshs=cnt_marshs,
                                   age=age_acc, avatar_name=filename)

        return render_template('profile.html', name=user_name, cnt_enters=cnt_enters, cnt_marshs=cnt_marshs,
                               age=age_acc)


def prof_info(a):
    if a == 1:
        return User.query.order_by(User.name), User.query.order_by(User.hashed_password), \
            User.query.order_by(User.created_date)


if __name__ == '__main__':
    app.run(debug=True)
