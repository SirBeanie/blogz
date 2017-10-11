from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from sort import sort

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:beproductive@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = "this is a key"

db = SQLAlchemy(app)

class Blog(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(50))
	body = db.Column(db.Text)
	
	def __init__(self, title, body):
		self.title = title
		self.body = body

@app.route("/")
def start():
	return render_template("nav.html")
		
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
		
if __name__ == "__main__":
    app.run()