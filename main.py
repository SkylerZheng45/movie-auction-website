import logging
import sys
from flask import Flask, redirect, url_for, request, render_template
import sqlite3 as sql
app = Flask(__name__)
#unique username
global_user_id = None

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
   global_user_id = user
   app.logger.info(global_user_id)
   return redirect(url_for('success',name = user))

#signup
@app.route('/signup')
def signup_page():
   return render_template('signup.html')

@app.route('/signup/<msg>')
def signup_again(msg):
   return render_template('signup.html', msg=msg)

@app.route('/signup',methods = ['POST', 'GET'])
def signup():
   password = request.form['password']
   password2 = request.form['password2']
   email = request.form['email']
   user = request.form['nm']
   age = request.form['age']
   if password == password2:
      global_user_id = user
      app.logger.info(global_user_id)
      try:
         with sql.connect("MovieAuctionDB.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO USER (EMAIL, USERNAME, PASSWORD, AGE ) VALUES(?,?,?,?);",(email,user,password,age))
            con.commit()
            msg = "Record successfully added"
      except:
         con.rollback()
         return redirect(url_for('signup_again', msg='Error in entered information'))
      finally:
         con.close()
         return redirect(url_for('success',name = user))

   else:
      return redirect(url_for('signup_again', msg='Passwords do not match.'))


if __name__ == '__main__':
   app.run(debug = True)