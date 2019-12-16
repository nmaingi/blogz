from flask import Flask, redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI']= 'mysql+pymysql://Blogz:Lingima@1@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO']=True
db = SQLAlchemy(app)
app.secret_key="ngish"

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120))
    content = db.Column(db.Text())
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, content, owner):
        self.title = title
        self.content = content
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(120), unique = True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref = 'owner')
    
    def __init__(self, username, password):
        self.username = username
        self.password = password

#home page conditions
@app.before_request
def require_login():
    allowed_routes = ['login', 'index', 'blog_list','sign_up']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

#home page
@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template('home.html', users = users)

#login in to get to write post and view posts
@app.route('/login', methods=['POST', 'GET'])
def login():
    username = ""
    username_error = ""
    password_error = ""
    blank=""

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username = username).first()

        if not user:
            username_error = "User does not exist."
            if username == blank:
                username_error = "Please enter your username."

        if password == blank:
            password_error = "Please enter your password."

        if user and user.password != password:
            password_error = "That is the wrong password."

        if user and user.password == password:
            session['username'] = username
            return render_template('newblog.html')
    
    return render_template('login.html',username = username, username_error = username_error, password_error = password_error)
#lists individual blog page
@app.route('/blogs', methods=['POST', 'GET'])
def blog_listing():
    title = ""

    if session:
        owner = User.query.filter_by(username = session['username']).first()

    if "id" in request.args:
        post_id = request.args.get('id')
        blog = Blog.query.filter_by(id = post_id).all()
        return render_template('allpost.html', title = "My blogs", blog = blog, post_id = post_id)

    elif "user" in request.args:
        user_id = request.args.get('user')
        blog = Blog.query.filter_by(owner_id = user_id).all()
        return render_template('allpost.html', title = "All my blogs", blog = blog)

    else:
        blog = Blog.query.order_by(Blog.id.desc()).all()
        return render_template('allpost.html', title = "All blogs", blog = blog)

#sign up page routed from login page
@app.route('/signup', methods=['POST','GET'])
def sign_up():   
    username=""
    username_error=""
    password_error=""
    password2_error=""
    blank=""
    
    if request.method=="POST":
        username=request.form['username']
        password=request.form['password']
        retype=request.form['password2']
        username_error=""
        password_error=""
        password2_error=""
        blank=""
        existing_user = User.query.filter_by(username = username).first()
        
        if username==blank:
            username_error="give username"
        else:
            if len(username)<3 or len(username)>20:
                username_error="out of range"
            elif username.count(' ')>0:
                username_error="cannot have spaces"
        
        if password==blank:
            password_error="give password"
        else:
            if len(password)<3 or len(password)>20:
                password_error= "password out of range"
            elif password.count(' ')>0:
                password_error="cannot contain spaces"
    
        if retype==blank:
            password2_error="give password"
        else:
            if len(retype)<3 or len(retype)>20:
                password2_error="password out of range"
            elif retype.count(' ')>0:
                password2_error="cannot contain spaces"
    
        if retype!=password:
            password2_error="password did not match"

        if not username_error and not password_error and not password2_error:
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                username = session['username']              
                return redirect('/newpost')
            else:
                username_error = "Username is already claimed."
    
    return render_template('signup.html',username=username, username_error=username_error, password_error=password_error, password2_error=password2_error)

#new post page routed from login and only accessed after login
@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    title_error = ""
    content_error = ""
    owner = User.query.filter_by(username = session['username']).first()

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_content = request.form['blogpost']

        if blog_title == "":
            title_error = "Please enter a title"

        if blog_content == "":
            content_error = "Please enter a post"

        if not title_error and not content_error:
            new_post = Blog(blog_title, blog_content, owner)
            db.session.add(new_post)
            db.session.commit()
            eachblog_id=Blog.query.order_by(Blog.id.desc()).first()
            user=owner
            return redirect('/blogs?id={}&user={}'.format(eachblog_id.id,user.username))

    return render_template('newblog.html')

#log out 
@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')

if __name__=="__main__":
    app.run()