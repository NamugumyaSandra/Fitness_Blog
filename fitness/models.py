from datetime import datetime
from fitness import db,login_manager
from flask_login import UserMixin

#static method that queries the db
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#create User table class and specify the attributes
class User(db.Model, UserMixin):  # user mixin helps in authentication and validity checks allowing for login and out
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20),unique=True, nullable=False)
    email = db.Column(db.String(100),unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)#r/ship with the Post model class
    comments = db.relationship('Comment', backref='author', lazy=True)

# representation format... what to be printed out
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

 #creating the post table in the db.Model baseclass   
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable = False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text,nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
    comments = db.relationship('Comment', backref='post', lazy=True)
#post representation
    def __repr__(self):
        return f"Post('{self.title}', '{self.date}','{self.content}')"

# comment class structure stating its relationship with other tables
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_commented = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text,nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
    post_id = db.Column (db.Integer, db.ForeignKey('post.id'),nullable=False)

    def __repr__(self):
        return f"Comment('{self.date_commented}','{self.content}')"

