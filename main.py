from flask import Flask, request, redirect, render_template, session, flash 
from flask_sqlalchemy import SQLAlchemy
from sort import sort

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:beproductive@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = "this is a key"

db = SQLAlchemy(app)


class Blog(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(50))
	body = db.Column(db.Text)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	
	def __init__(self, title, body, user):
		self.title = title
		self.body = body
		self.user = user
		
class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(24), unique=True)
	password = db.Column(db.String(24))
	blogs = db.relationship('Blog', backref='user')
	
	def __init__(self,username,password):
		self.username = username
		self.password = password


@app.before_request
def require_login():
	whitelist = ['login','blog','signup','index', 'static']
	if request.endpoint not in whitelist and 'user' not in session:
		return redirect("/login")


@app.route("/blog")
def blog():
	if request.args.get('id'):
		blog_id = request.args.get('id')
		blog = Blog.query.filter_by(id=blog_id).first()
		
		return render_template("new-blog.html", blog = blog)


	elif request.args.get('user'):
		user_id = request.args.get('user')
		posts = Blog.query.filter_by(user_id=user_id).all()
		
		sort(posts)
		return render_template("blog.html", posts=posts, title="Posts by " + posts[0].user.username)

	
	else:
		posts = Blog.query.all()
		sort(posts)
		
		return render_template("blog.html", posts=posts, title="All Post")


@app.route("/newpost", methods=['POST', 'GET'])
def newpost():
	if request.method == 'POST':
		if not request.form['title'] or not request.form['body']:
			if not request.form['title']:
				flash("Please create a title.")
			if not request.form['body']:
				flash("This area can not be blank.")
			return render_template("newpost.html", title="New Post")
		
		blog_title = request.form['title']
		blog_body = request.form['body']
		user = User.query.filter_by(username=session['user']).first()

		post = Blog(blog_title, blog_body, user)
		db.session.add(post)
		db.session.commit()
		
		flash("You have created a new post.")
		
		id = str(post.id)
		
		return redirect("/blog?id=" + id)
	
	return render_template("newpost.html", title="New Post")


@app.route("/signup", methods=['GET','POST'])
def signup():
	if request.method == 'POST':
		errors = 0 
		if not request.form['username']:
			flash("Please enter a username.")
			errors += 1
		if not request.form['password']:
			flash("Please enter a password.")
			errors += 1
		if not request.form['verify']:
			flash("Please verify password.")
			errors += 1
		if request.form['password'] != request.form['verify']:
			flash("Passwords do not match.")
			errors += 1
		if request.form['username'] and User.query.filter_by(username=request.form['username']).first():
			flash("Username already exists.")
			errors += 1
			
		if errors > 0:
			return render_template("signup.html", title="Sign Up")		
		else:					
			username = request.form['username']
			password = request.form['password']
			verify = request.form['verify']
			
			user = User(username, password)
			db.session.add(user)
			db.session.commit()
			
			session['user'] = username
			flash("Logged in as " + username)
			return redirect("/newpost")		
	
	return render_template("signup.html", title="Sign Up")


@app.route("/login", methods=['GET','POST'])
def login():
	if request.method == 'POST':
		errors = 0 
		if not request.form['username']:
			flash("Please enter a username.")
			errors += 1
		if not request.form['password']:
			flash("Please enter a password.")
			errors += 1
		if request.form['username'] and not User.query.filter_by(username=request.form['username']).first():
			flash("Invalid username.")
			errors += 1

		if errors > 0:
			return render_template("login.html", title="Log In")		
		else:
			username = request.form['username']
			password = request.form['password']
			
			user = User.query.filter_by(username=username).first()
			if password != user.password:
				flash("Incorrect password.")
				return render_template("login.html", title="Log In")
			
			session['user'] = username
			flash("Logged in as " + username)
			return redirect("/newpost")	
	
	return render_template("login.html", title="Log In")



@app.route("/logout")
def logout():
	flash("Logged out " + session['user'])
	del session['user']
	return redirect("/blog")

@app.route("/")
def index():
	users = User.query.all()
	return render_template("user_index.html", users=users, title="Authors")



if __name__ == "__main__":
    app.run()
