from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField
from wtforms.validators import DataRequired
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisissecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
db = SQLAlchemy(app)

# Database model
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)

# Forms
class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

# Routes
@app.route('/')
def index():
    query = request.args.get('q', '')
    all_posts = Post.query.all()  # 💥 Pulling posts directly from DB

    if query:
        filtered_posts = [post for post in all_posts if query.lower() in post.title.lower() or query.lower() in post.content.lower()]
    else:
        filtered_posts = all_posts

    return render_template('index.html', posts=filtered_posts, query=query)



@app.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post)

@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.username.data == 'admin' and form.password.data == 'admin123':
            session['logged_in'] = True
            return redirect('/admin/dashboard')
    return render_template('login.html', form=form)

@app.route('/admin/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/')

@app.route('/admin/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect('/admin/login')
    posts = Post.query.all()
    return render_template('dashboard.html', posts=posts)

@app.route('/admin/create', methods=['GET', 'POST'])
def create():
    if not session.get('logged_in'):
        return redirect('/admin/login')
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data)
        db.session.add(post)
        db.session.commit()
        return redirect('/admin/dashboard')
    return render_template('create.html', form=form)

@app.route('/admin/edit/<int:post_id>', methods=['GET', 'POST'])
def edit(post_id):
    if not session.get('logged_in'):
        return redirect('/admin/login')
    post = Post.query.get_or_404(post_id)
    form = PostForm(obj=post)
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        return redirect('/admin/dashboard')
    return render_template('edit.html', form=form)

@app.route('/admin/delete/<int:post_id>')
def delete(post_id):
    if not session.get('logged_in'):
        return redirect('/admin/login')
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect('/admin/dashboard')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
    with app.app_context():
        db.create_all()
    app.run(debug=True)
