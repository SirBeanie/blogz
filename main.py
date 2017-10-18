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


@app.route("/")
def start():
	return render_template("index.html")
		
@app.route("/blog")
def blog():
	if request.args.get('id'):
		blog_id = request.args.get('id')
		blog = Blog.query.filter_by(id=blog_id).first()
		
		return render_template("new-blog.html", blog = blog)
	
	else:
		posts = Blog.query.all()
		sort(posts)
		
		return render_template("blog.html", posts=posts)
	
@app.route("/newpost", methods=['POST', 'GET'])
def newpost():
	if request.method == 'POST':
		if not request.form['title'] or not request.form['body']:
			if not request.form['title']:
				flash("Please create a title.")
			if not request.form['body']:
				flash("This area can not be blank.")
			return render_template("newpost.html")
		
		blog_title = request.form['title']
		blog_body = request.form['body']
		post = Blog(blog_title, blog_body)
		db.session.add(post)
		db.session.commit()
		
		flash("You have created a new post.")
		
		id = str(post.id)
		
		return redirect("/blog?id=" + id)
	
	return render_template("newpost.html")

@app.route("/logout", methods=['POST'])
def logout():



	return redirect("/blog")


if __name__ == "__main__":
    app.run()