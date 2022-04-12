from flask import Flask, redirect, url_for, request, render_template
app = Flask(__name__)

@app.route('/')
def home():
   return render_template('index.html')

# login
@app.route('/<name>')
def success(name):
   return render_template('index.html', username = name)

@app.route('/login')
def login_page():
   return render_template('login.html')

@app.route('/login',methods = ['POST', 'GET'])
def login():
   user = request.form['nm']
   password = request.form['password']
   return redirect(url_for('success',name = user))


if __name__ == '__main__':
   app.run(debug = True)