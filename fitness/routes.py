import os
import secrets
from PIL import Image
from flask import render_template,url_for,flash,redirect,request,abort
from fitness import app, db, bcrypt
from fitness.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, CommentForm
from fitness.models import User, Post, Comment
from flask_login import login_user, current_user, logout_user, login_required

# home route and the functions it calls
@app.route('/')
@app.route('/home')
def home():
    page = request.args.get('page',1, type=int)
    posts = Post.query.order_by(Post.date.desc()).paginate(page=page,per_page=5)
    return render_template('home.html',posts=posts)

# home about and the functions it calls
@app.route('/about')
def about():
    return render_template('about.html', title='About')
 
# register route and the functions it calls to successfully register a user
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Account has been created! Login Now','success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

# login route and the functions it calls to successfully login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: #returns true if valid credentials are provided
        return redirect(url_for('home'))    
    form = LoginForm()
    if form.validate_on_submit():  # submits successfully
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user, remember = form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page)if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check the email and password.','danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')  #logs out a user
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):    # function to save the profile pic for each account created to the defined spec
    random_hex = secrets.token_hex(8)
    _,f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path =os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    output_size = (125,125)
    i =Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

@app.route('/account', methods=['GET', 'POST']) #url to the profile page tomake required changes
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account')) 
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static',filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)

@app.route('/post/new',methods=['GET', 'POST']) # url for a loggedin user to post
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created','success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form=form,legend = 'New Post')

@app.route('/post/<int:post_id>') #url to veiw individual created post
def post(post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.order_by(Comment.date_commented.desc())
    return render_template('post.html', title=post.title, post=post, comments=comments)

@app.route('/post/<int:post_id>/update',methods=['GET', 'POST']) #makechanges to a post
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title= form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!','success')
        return redirect(url_for('post',post_id=post.id))
    elif request.method == 'GET':   
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')


@app.route('/post/<int:post_id>/delete',methods=['POST']) # delete a post
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been successfully deleted!', 'success')
    return redirect(url_for('home'))

# to retrieve all posts of a user
@app.route('/user/<string:username>')
def user_posts(username):
    page = request.args.get('page',1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date.desc())\
        .paginate(page=page,per_page=5)
    return render_template('user_posts.html',posts=posts, user=user)

#make a comment to aparticular post
@app.route('/post/<int:post_id>/comment/new', methods=['GET', 'POST'])
@login_required
def new_comment(post_id):
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(content=form.content.data, post_id=post_id, author=current_user)
        db.session.add(comment)
        db.session.commit()
        flash('Comment Posted!','success')
        return redirect(url_for('post',post_id=post.id))
    return render_template('create_comment.html', title='New Comment', form=form, legend='New Comment')

#stores the comment made and views it
@app.route('/post/<int:post_id>/comment/<int:comment_id>')
def comment(post_id,comment_id):
    post = Post.query.get_or_404(post_id=post.id)
    comment = Comment.query.get_or_404(comment_id=comment.id)
    return render_template('comment.html',post_id=post_id, comment=comment)
   
#route to retrive all comments of a post
# @app.route('/post/<int:post_id>/post_comments')
# def post_comments(post_id):
#     post = request.args.get('post_id',1, type=int)
#     post = Post.query.filter_by(post_id=post_id).first_or_404()
#     comments = Comment.query.filter_by(post_id=post_id)\
#         .order_by(Comment.date_commented.desc())
#     return render_template('home.html', comments=comments, post_id=post_id,user=user)
