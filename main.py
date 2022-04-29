import email
import logging
import sys
from flask import Flask, redirect, url_for, request, render_template, make_response
import sqlite3 as sql
app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
#unique user_id
global global_user_id
global username
global movieInfoCards
global cart

#default home page
@app.route('/')
def home():
   global cart
   cart = [] 
   global movieInfoCards 
   with sql.connect("MovieAuctionDB.db") as con:
      cur = con.cursor()
      cur.execute("SELECT * FROM MOVIEINFO LIMIT 8")
      movieInfoCards = cur.fetchall()
   # find username if global_user_id is defined
   print(movieInfoCards)
   try:
      global global_user_id
      app.logger.info(global_user_id)
      with sql.connect("MovieAuctionDB.db") as con:
         con.row_factory = sql.Row
         cur = con.cursor()
         cur.execute(f"select username from USER where user_id = '{global_user_id}';")
         rows = cur.fetchall()
         return redirect(url_for('success',name = rows[0]['username']))
   except:
      return render_template('index.html',cart=cart, cartCounter=len(cart),movieInfo = movieInfoCards)



#adding item to cart
@app.route('/addToCart/<cardNum>', methods=['GET'])
def addToCart(cardNum):
   #adding to cart try catching to see if logged in
   global cart
   try: 
      cart.append(movieInfoCards[int(cardNum)])
      print("Cart contents with username: ",username,cart)
      return redirect(url_for('success',name = username))
   except Exception as e:
      cart = []
      return render_template('login_or_signup.html',msg="You must login or signup before adding an item to cart")
   
#remove from cart
@app.route('/removeFromCart')

@app.route('/addMovie')
def addMoviePage():
   return render_template('movie_entry.html')

#adding an item for sale 
@app.route('/addMovie',methods = ['POST', 'GET'])
def addMovie():
   name = request.form['name']
   year = request.form['year']
   desc = request.form['desc']
   price = request.form['price']
   imgurl = request.form['imgurl']
   try:
      with sql.connect("MovieAuctionDB.db") as con:
         # insert info
         cur = con.cursor()
         # INSERT INTO MOVIEINFO (NAME,YEAR,DESC,PRICE) VALUES 
         if len(imgurl)==0:
            cur.execute("INSERT INTO MOVIEINFO (NAME,YEAR,DESC,PRICE) VALUES(?,?,?,?);",(name,year,desc,price))
         else:         
            cur.execute("INSERT INTO MOVIEINFO (NAME,YEAR,DESC,PRICE,IMGURL) VALUES(?,?,?,?,?);",(name,year,desc,price,imgurl))
         con.commit()
         msg = "Record successfully added"
      return redirect(url_for('success',name = username))
   except Exception as e:
      con.rollback()
      app.logger.info(e)
      return redirect(url_for('signup_again', msg='Error in entered information'))

@app.route('/showAllProducts')
def showAllProducts():
   with sql.connect("MovieAuctionDB.db") as con:
      cur = con.cursor()
      cur.execute("SELECT * FROM MOVIEINFO")
      movieInfoCards = cur.fetchall()
      print("Number of Movies queryed", len(movieInfoCards))
      return render_template('all_products.html',cart=cart, cartCounter=len(cart),movieInfo = movieInfoCards)

# login
@app.route('/<name>')
def success(name):
   global movieInfoCards 
   with sql.connect("MovieAuctionDB.db") as con:
      cur = con.cursor()
      cur.execute("SELECT * FROM MOVIEINFO LIMIT 8")
      movieInfoCards = cur.fetchall()
   return render_template('index.html', username = name,cartCounter=len(cart), movieInfo = movieInfoCards)

@app.route('/login')
def login_page():
   return render_template('login.html')

@app.route('/login/<msg>')
def login_again(msg):
   return render_template('login.html', msg=msg)

@app.route('/login',methods = ['POST', 'GET'])
def login():
   email = request.form['email']
   password = request.form['password']
   try:
      with sql.connect("MovieAuctionDB.db") as con:
         con.row_factory = sql.Row
         cur = con.cursor()
         cur.execute(f"select username, password, user_id from USER where email = '{email}';")
         rows = cur.fetchall()
         if rows[0]['password'] == password:
            global global_user_id
            global_user_id = rows[0]['user_id']
            global username
            username = rows[0]['username']
            app.logger.info(global_user_id)
            return redirect(url_for('success',name = rows[0]['username']))
         else:
            raise Exception('Password is wrong.')
   except:
      return redirect(url_for('login_again', msg='Wrong information entered'))

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
      try:
         with sql.connect("MovieAuctionDB.db") as con:
            # insert info
            cur = con.cursor()
            cur.execute("INSERT INTO USER (EMAIL, USERNAME, PASSWORD, AGE ) VALUES(?,?,?,?);",(email,user,password,age))
            con.commit()
            msg = "Record successfully added"
         with sql.connect("MovieAuctionDB.db") as con:
            # get the user_id to store in global
            con.row_factory = sql.Row
            cur = con.cursor()
            cur.execute(f"select USER_ID FROM USER where username='{user}' and email='{email}'")
            rows = cur.fetchall()
            global global_user_id
            global_user_id = rows[0]['user_id']
            app.logger.info(global_user_id)
            app.logger.info('last row id')
            app.logger.info(rows[0]['user_id'])
            # resp.set_cookie('user_id',rows[0]['user_id'])
         return redirect(url_for('success',name = user))
      except Exception as e:
         con.rollback()
         app.logger.info(e)
         return redirect(url_for('signup_again', msg='Error in entered information'))
   else:
      return redirect(url_for('signup_again', msg='Passwords do not match.'))

# user_profile
# with feedback message
@app.route('/user_profile')
def user_profile_page():
   # get account info from the database
   with sql.connect("MovieAuctionDB.db") as con:
      con.row_factory = sql.Row
      cur = con.cursor()
      global global_user_id
      cur.execute(f"select * from USER where user_id = '{global_user_id}';")
      rows = cur.fetchall()
      app.logger.info(global_user_id)
      app.logger.info(len(rows))
      username = rows[0]['username']
      email = rows[0]['email']
      age = rows[0]['age']
      card = rows[0]['card']
      card_exp_date = rows[0]['card_exp_date']
      billing_addr = rows[0]['billing_addr']
      zip_code = rows[0]['zip_code']
   return render_template('user_profile.html',username=username, email=email, age=age, card=card, card_exp_date=card_exp_date, billing_addr=billing_addr, zip_code=zip_code)

# without feedback message
@app.route('/user_profile/<msg>')
def user_profile_after_update(msg):
   # get account info from the database
   with sql.connect("MovieAuctionDB.db") as con:
      con.row_factory = sql.Row
      cur = con.cursor()
      global global_user_id
      cur.execute(f"select * from USER where user_id = '{global_user_id}';")
      rows = cur.fetchall()
      app.logger.info(global_user_id)
      app.logger.info(len(rows))
      username = rows[0]['username']
      email = rows[0]['email']
      age = rows[0]['age']
      card = rows[0]['card']
      card_exp_date = rows[0]['card_exp_date']
      billing_addr = rows[0]['billing_addr']
      zip_code = rows[0]['zip_code']
   return render_template('user_profile.html',msg=msg,username=username, email=email, age=age, card=card, card_exp_date=card_exp_date, billing_addr=billing_addr, zip_code=zip_code)

# update user profile
@app.route('/user_profile',methods = ['POST', 'GET'])
def user_profile():
   email = request.form['email']
   user = request.form['nm']
   age = request.form['age']
   card = request.form['card']
   card_exp_date = request.form['card_exp_date']
   zip_code  = request.form['zip_code']
   billing_addr = request.form['billing_addr']
   try:
      with sql.connect("MovieAuctionDB.db") as con:
         # insert info
         cur = con.cursor()
         global global_user_id
         cur.execute(f"UPDATE USER SET EMAIL = '{email}', USERNAME = '{user}', AGE='{age}',CARD='{card}',CARD_EXP_DATE='{card_exp_date}',ZIP_CODE='{zip_code}',BILLING_ADDR='{billing_addr}' WHERE user_id = '{global_user_id}'")
         con.commit()
         msg = "Record successfully updated"
   except:
      con.rollback()
      msg = "Record failed to update"
   finally:
      return redirect(url_for('user_profile_after_update',msg = msg))


if __name__ == '__main__':
   app.run(debug = True)