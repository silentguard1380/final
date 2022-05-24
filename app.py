from flask import Flask,render_template,request,redirect,flash
from datetime import date
# import database lib
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,UserMixin,login_user,current_user,logout_user,login_required
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.sqlite'
app.config['SECRET_KEY']='619619'
db=SQLAlchemy(app)

loginmanager=LoginManager(app)
loginmanager.login_view = 'auth'
loginmanager.login_message = 'please login first '
loginmanager.login_message_category = 'info'
@loginmanager.user_loader
def load_user(user_id):
    print(User.query.get(int(user_id)))
    return User.query.get(int(user_id))

class User(db.Model,UserMixin):
    id =db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(100),nullable=False)
    password=db.Column(db.String(100),nullable=False)
    post=db.relationship('BlogPostDb',backref='author',lazy=True)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.id},{self.username})'

class BlogPostDb(db.Model):
    id =db.Column(db.Integer,primary_key=True)       # db.create_all() run this code in terminal python for create database
    title = db.Column(db.String(100),nullable=False)
    body = db.Column(db.Text,nullable=False)
    date = db.Column(db.Text)

    #relationship
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.title},{self.body})'
db.create_all()


@app.route("/auth")
def auth():
    return render_template("auth.html")

@app.route("/signup-control" , methods=["POST"])
def signup_control():
    user_name = request.form["name"]

    user_pass = request.form["pass"]
    try:
        user = User(username=user_name,password = user_pass)
        db.session.add(user)
        db.session.commit()
        flash('you registered succsesfuly')
        return redirect('/auth',)

    except Exception as ex:
        return "متاسفانه ثبت نام شما انجام نشد" + "<br>" + str(ex)

@app.route('/login-control' , methods=["POST"])
def login_control():
    user_name = request.form["your_name"]
    user_pass = request.form["your_pass"]
    user = User.query.filter_by(username=user_name).first()
    if current_user.is_authenticated:
        flash('you are login ')
        return redirect('/')
    if user and user.password==user_pass:
        flash('you login out successfully')
        login_user(user,remember=True)
        return redirect('/')
    else :
        return "<a href='/auth'>your password or username  is wrong please try again </a>"
@login_required
@app.route('/logout')
def logout():
    logout_user()
    flash('you logged out successfully')
    return redirect('/')

@app.route('/notlogin')
def notlogin():
    return render_template('notlogin.html')



@app.route('/todo', methods=["POST","GET"])
def test():
    user = user=User.query.get(current_user.id)
    post = user.post

    if post==[] or post =='' or post==None:

        return render_template('todo.html')
    else:

        return render_template('todo.html',posts=post)

@app.route('/')
def home():


    return render_template("base.html")




@app.route('/addpost',methods=['POST','GET'])
@login_required
def addpost():
    if current_user.is_authenticated:

        today = date.today()

        if request.method=='POST':
            post_title= request.form['title']
            post_body= request.form['body']

            blogpost=BlogPostDb(title=post_title,body=post_body,date=today,user_id=f'{current_user.id}')
            db.session.add(blogpost)
            db.session.commit()
            return redirect('/todo')
        return render_template('addpost.html')
    else:
        return redirect('/notlogin')

@app.route('/delete/post/<int:id>')
@login_required
def deletepost(id):
    blog_post=BlogPostDb.query.get(id)
    db.session.delete(blog_post)
    db.session.commit()
    return redirect('/todo')

@app.route('/update/post/<int:id>',methods=['POST','GET'])
@login_required
def updatepost(id):
    blog_post=BlogPostDb.query.get(id)
    if request.method=='POST':
        post_title= request.form['title']
        post_body= request.form['body']
        blog_post.title=post_title
        blog_post.body=post_body
        db.session.commit()
        return redirect('/todo')
    return render_template('update.html',post=blog_post)


if __name__ == '__main__':
    app.run(debug=True)