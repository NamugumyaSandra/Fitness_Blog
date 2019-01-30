from flask import Flask, render_template,url_for
from forms import RegistrationForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = '9786f4c710cad7ed87cd4097403f376a'

posts = [
    {
        'author':'Sal Namuwonge',
        'title':'Blog Post 1',
        'content':'First blog post content',
        'date':'May 29, 2018'
    },
    {
        'author':'Sandra Namugumya',
        'title':'Blog Post 2',
        'content':'Second blog post content',
        'date':'May 30, 2018'
    }
]


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html',posts=posts )


@app.route('/about')
def about():
    return render_template('about.html', title='About')
 

@app.route('/register')
def register():
    form = RegistrationForm()
    return render_template('register.html', title='Register', form=form)


@app.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html', title='Login', form=form)

if __name__ == '__main__':
   app.run(debug=True)
    