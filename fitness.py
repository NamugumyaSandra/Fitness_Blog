from flask import Flask, render_template,url_for
app = Flask(__name__)

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


if __name__ == '__main__':
   app.run(debug=True)
    