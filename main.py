#from crypt import methods
import email
from glob import glob
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
   return render_template('movie_entry.html', msg='')

#adding an item for sale 
@app.route('/addMovie',methods = ['POST', 'GET'])
def addMovie():
   name = request.form['name']
   year = request.form['year']
   desc = request.form['desc']
   price = request.form['price']
   imgurl = request.form['imgurl']
   if len(name) != 0 and len(year) != 0 and len(desc) != 0 and len(price)!=0:
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
         return render_template('movie_entry.html', msg='Error in entered information exception found')
   else:
      return render_template('movie_entry.html', msg='Error in entered information, Please fill out again')

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
            # check if the email exsits or not
            con.row_factory = sql.Row
            cur = con.cursor()
            cur.execute(f"select * FROM USER where email='{email}'")
            rows = cur.fetchall()
            if len(rows)>0:
               return redirect(url_for('signup_again', msg='Email already existed.'))
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
            cur.execute(f"INSERT INTO WISHLIST (USER_ID) VALUES('{global_user_id}');")
            con.commit()
            # resp.set_cookie('user_id',rows[0]['user_id'])
         return redirect(url_for('success',name = user))
      except Exception as e:
         con.rollback()
         app.logger.info(e)
         return redirect(url_for('signup_again', msg='Error in entered information.'))
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
         # check if the email exsits or not
         con.row_factory = sql.Row
         cur = con.cursor()
         global global_user_id
         cur.execute(f"select email FROM USER where user_id='{global_user_id}'")
         rows = cur.fetchall()
         if len(rows)>0 and rows[0]['email']!=email:
            msg = 'Email already existed.'
            return redirect(url_for('user_profile_after_update',msg = msg))
      with sql.connect("MovieAuctionDB.db") as con:
         # insert info
         cur = con.cursor()
         cur.execute(f"UPDATE USER SET EMAIL = '{email}', USERNAME = '{user}', AGE='{age}',CARD='{card}',CARD_EXP_DATE='{card_exp_date}',ZIP_CODE='{zip_code}',BILLING_ADDR='{billing_addr}' WHERE user_id = '{global_user_id}'")
         con.commit()
         msg = "Record successfully updated"
   except:
      con.rollback()
      msg = "Record failed to update"
   finally:
      return redirect(url_for('user_profile_after_update',msg = msg))

# delete user
@app.route('/delete_user/', methods=['POST'])
def delete_user():
   with sql.connect("MovieAuctionDB.db") as con:
      global global_user_id
      cur = con.cursor()
      cur.execute(f"DELETE FROM user WHERE user_id = {global_user_id};")
      con.commit()
   global cart
   cart = [] 
   global movieInfoCards 
   with sql.connect("MovieAuctionDB.db") as con:
      cur = con.cursor()
      cur.execute("SELECT * FROM MOVIEINFO LIMIT 8")
      movieInfoCards = cur.fetchall()
   return render_template('index.html',cart=cart, cartCounter=len(cart),movieInfo = movieInfoCards)

@app.route('/index/<title>', methods = ['POST', 'GET'])
def addToWishlist(title):
   try:
      with sql.connect("MovieAuctionDB.db") as con:
         global global_user_id
         cur = con.cursor()
         cur.execute(f"INSERT INTO WISHLISTBRIDGE (WISHLIST_ID, MOVIE_ID) VALUES((SELECT WISHLIST_ID FROM WISHLIST WHERE USER_ID = '{global_user_id}'),'{title}');")
         con.commit()
   except:
      con.rollback()
   return redirect(url_for('home'))

@app.route('/wishlist')
def wishlist():
   con = sql.connect("MovieAuctionDB.db")
   con.row_factory = sql.Row

   cur = con.cursor()
   cur.execute(f"SELECT * FROM WISHLISTBRIDGE WHERE WISHLIST_ID = (SELECT WISHLIST_ID FROM WISHLIST WHERE USER_ID = '{global_user_id}');")
   rows = cur.fetchall()

   return render_template("wishlist.html", rows=rows)

@app.route('/deleteFromWishlist/<wish_id>/<movie>', methods = ['POST','GET'])
def deleteFromWishlist(wish_id, movie):
   with sql.connect("MovieAuctionDB.db") as con:
      global global_user_id
      cur = con.cursor()
      cur.execute(f"DELETE FROM WISHLISTBRIDGE WHERE WISHLIST_ID = '{wish_id}' OR MOVIE_ID = '{movie}';")
      con.commit()

   return redirect(url_for('wishlist'))

@app.route('/review')
def review_default():
   con = sql.connect("MovieAuctionDB.db")
   con.row_factory = sql.Row

   cur = con.cursor()
   cur.execute(f"SELECT * from MOVIEINFO;")
   movies = cur.fetchall()
   return render_template("review.html",movies=movies)

@app.route('/review',methods = ['POST','GET'])
def review():
   value = request.form['selectedMovie']
   review_content = request.form['review_content']
   rating = request.form['rating']

   try:
      with sql.connect("MovieAuctionDB.db") as con:
         global global_user_id
         cur = con.cursor()
         cur.execute("INSERT INTO REVIEW (USER_ID, MOVIE_ID, RATING, REVIEW_CONTENT) VALUES(?,?,?,?);", (global_user_id,value,rating,review_content))
         con.commit()
      return redirect(url_for('home'))
   except:
      con.rollback()
      return redirect(url_for('home'))

@app.route('/reviews/<title>',methods = ['POST','GET'])
def allMovieReviews(title):
   try:
      with sql.connect("MovieAuctionDB.db") as con:
         con.row_factory = sql.Row
         cur = con.cursor()
         cur.execute(f"SELECT * from REVIEW WHERE MOVIE_ID = '{title}';")
         reviews = cur.fetchall()
         app.logger.info(reviews)
         cur.execute(f"SELECT NAME FROM MOVIEINFO WHERE MOVIE_ID = '{title}'")
         names = cur.fetchall()
         return render_template("all_movie_reviews.html",reviews=reviews, names=names)
   except:
      con.rollback()
      return redirect(url_for('home'))

@app.route('/myreviews',methods = ['POST','GET'])
def myreviews():
   try:
      with sql.connect("MovieAuctionDB.db") as con:
         global global_user_id
         con.row_factory = sql.Row
         cur = con.cursor()
         cur.execute(f"SELECT * from REVIEW WHERE USER_ID = {global_user_id};")
         reviews = cur.fetchall()
         app.logger.info(global_user_id)
         app.logger.info(len(reviews))

         cur.execute(f"SELECT USERNAME FROM USER WHERE USER_ID = '{global_user_id}';")
         names = cur.fetchall()
         app.logger.info(global_user_id)
         app.logger.info(len(names))
         return render_template("all_user_reviews.html",reviews=reviews, names=names)
   except:
      con.rollback()
      return redirect(url_for('home'))

@app.route('/deleteFromReview/<id>', methods = ['POST','GET'])
def deleteFromReview(id):
   with sql.connect("MovieAuctionDB.db") as con:
      global global_user_id
      cur = con.cursor()
      cur.execute(f"DELETE FROM REVIEW WHERE REVIEW_ID = '{id}';")
      con.commit()

   return redirect(url_for('myreviews'))

@app.route('/checkout',methods = ['POST', 'GET'])
def checkout():
   # get account info from the database
   with sql.connect("MovieAuctionDB.db") as con:
      con.row_factory = sql.Row
      cur = con.cursor()
      cur.execute(f"select * from USER where user_id = '{global_user_id}';")
      rows = cur.fetchall()
      app.logger.info(global_user_id)
      app.logger.info(len(rows))
      username = rows[0]['username']
      email = rows[0]['email']
      card = rows[0]['card']
      card_exp_date = rows[0]['card_exp_date']
      billing_addr = rows[0]['billing_addr']
      zip_code = rows[0]['zip_code']
      # print(cart)
      while(len(cart)<8):
         cart.append(('','','','',''))
      

   return render_template('checkout.html',username=username, email=email, card=card, card_exp_date=card_exp_date, billing_addr=billing_addr, zip_code=zip_code,cart = cart)



@app.route('/transaction')
def transaction():
   with sql.connect("MovieAuctionDB.db") as con:
      if(len(cart)>0):
         try:
            con.row_factory = sql.Row
            cur = con.cursor()
            cur.execute(f"select * from USER where user_id = '{global_user_id}';")
            rows = cur.fetchall()
            # INSERT INTO TRANSACTIONS
            for i in range(len(cart)):
               if(cart[i][4]!=""):
                  cur.execute("INSERT INTO TRANSACTIONS (USER_ID,MOVIE_AUC_ID,CASH_AMOUNT) VALUES(?,?,?);",(global_user_id,cart[i][0],cart[i][4]))
                  con.commit()
            for i in range(len(cart)):
               if((cart[0][1])!=''):
                  print("Deleting "+cart[0][1])
                  # cur.execute("DELETE FROM MOVIEINFO WHERE MOVIE_AUC_ID == cart[0][0]")
                  # con.commit()
                  cart.pop(0)
               else:
                  cart.pop(0)
            return transactionlog()
         except Exception as e:
            con.rollback()
            app.logger.info(e)
            msg = "Your Transaction was not successful"
            return render_template('transaction.html',cart = cart,msg=msg)
      
      
@app.route('/transactionlog')
def transactionlog():
   with sql.connect("MovieAuctionDB.db") as con:
      cur = con.cursor()   
      cur.execute("SELECT * FROM TRANSACTIONS WHERE USER_ID = "+str(global_user_id)+";")
      rows = cur.fetchall()
      

      transaction = []
      for i in rows:
         
         cur.execute("SELECT * FROM MOVIEINFO WHERE MOVIE_ID = "+str(i[2])+";")
         log = cur.fetchall()
         for i in log:
            # print(i[0])
            transaction.append(i)

      print(transaction)
      while(len(transaction)<8):
         transaction.append(('','','','',''))
      msg = ""
      return render_template('transaction.html',cart = transaction,msg=msg)


if __name__ == '__main__':
   app.run(debug = True)