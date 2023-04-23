from sqlalchemy.util.preloaded import orm

from main import db
import datetime


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True)
    name = db.Column(db.String
                     , nullable=True)
    hashed_password = db.Column(db.String, nullable=True)

    created_date = db.Column(db.DateTime,
                             default=datetime.datetime.now)

    profiles = orm.relationship("Profiles", back_populates='user')

    def __init__(self, name: str, hashed_password: str):
        self.name = name
        self.hashed_password = hashed_password

    def __repr__(self):
        return f'Пользователь {self.name}.' \
               f'Пароль {self.hashed_password}' \
               f'Дата создания {self.created_date}'


class News(db.Model):
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


class Profile(db.Model):
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
