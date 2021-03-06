#from crypt import methods
import email
from glob import glob
from locale import currency
import logging
from pickle import FALSE
import sys
from flask import Flask, redirect, url_for, request, render_template, make_response
import sqlite3 as sql
from datetime import datetime
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

#Joey Chou Code starts here 
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
      print('adsfa',e)
      cart = []
      return render_template('login_or_signup.html',msg="You must login or signup before adding an item to cart")
   
#remove from cart
@app.route('/removeFromCart')

@app.route('/addMovie')
def addMoviePage():
   return render_template('movie_entry.html',msg='',name2=username)

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
               cur.execute("INSERT INTO MOVIEINFO (NAME,YEAR,DESC,PRICE,USER_ID) VALUES(?,?,?,?,?);",(name,year,desc,price,global_user_id))
            else:         
               cur.execute("INSERT INTO MOVIEINFO (NAME,YEAR,DESC,PRICE,IMGURL,USER_ID) VALUES(?,?,?,?,?,?);",(name,year,desc,price,imgurl,global_user_id))
            con.commit()
            msg = "Record successfully added"
         return redirect(url_for('success',name = username))
      except Exception as e:
         con.rollback()
         app.logger.info(e)
         return render_template('movie_entry.html', msg='Error in entered information exception found')
   else:
      return render_template('movie_entry.html', msg='Error in entered information, Please fill out again')

#remove Movie from your personal account
@app.route('/removeMovie/<movieID>',methods = ['POST', 'GET'])
def removeMovie(movieID):
   try:
      with sql.connect("MovieAuctionDB.db") as con:
         cur = con.cursor()
         print('MOVIE ID =',movieID)
         cur.execute("DELETE FROM MOVIEINFO WHERE MOVIE_ID = ? ;",(movieID,))
         con.commit()
         msg = "Movie Successfully Removed"
      return redirect(url_for('mymovies'))
   except Exception as e:
      con.rollback()
      app.logger.info(e)
      return redirect(url_for('mymovies'))


@app.route('/changeMoviePrice/<movieID>',methods = ['POST', 'GET'])
def changeMoviePrice(movieID):
   price = request.form['price']
   print("NEW PRICE REQUESTED",price )
   if len(price)>0:
      try:
         with sql.connect("MovieAuctionDB.db") as con:    
            cur = con.cursor()  
            cur.execute("UPDATE MOVIEINFO SET PRICE = ? WHERE MOVIE_ID = ? ;",(price,movieID))
            con.commit()
            msg = "Record successfully added"
         return redirect(url_for('mymovies'))
      except Exception as e:
         con.rollback()
         app.logger.info(e)
         return redirect(url_for('success',name = username))
   else:
      return redirect(url_for('success',name = username))

@app.route('/addMovieAuctionBid/<auctionID>',methods = ['POST', 'GET'])
def addMovieAuctionBid(auctionID):
   price = request.form['price']
   print("NEW PRICE REQUESTED ON AN AUCTION",price,auctionID)
   if len(price)>0:
      try:
         with sql.connect("MovieAuctionDB.db") as con:    
            cur = con.cursor()  
            cur.execute("UPDATE MOVIEAUCTION SET PRICE = ? WHERE MOVIE_AUC_ID = ? ;",(price,auctionID))
            con.commit()
            print("Record successfully updated")
         return redirect(url_for('showMovieAuction',username = username))
      except Exception as e:
         con.rollback()
         app.logger.info(e)
         return redirect(url_for('success',name = username))
   else:
      return redirect(url_for('success',name = username))

@app.route('/showAllProducts')
def showAllProducts():
   with sql.connect("MovieAuctionDB.db") as con:
      cur = con.cursor()
      cur.execute("SELECT * FROM MOVIEINFO")
      movieInfoCards = cur.fetchall()
      print("Number of Movies queryed", len(movieInfoCards))
      return render_template('all_products.html',cart=cart, cartCounter=len(cart),movieInfo = movieInfoCards)

@app.route('/showMovieAuction')
def showMovieAuction():
   with sql.connect("MovieAuctionDB.db") as con:
      cur = con.cursor()
      cur.execute(f"SELECT * FROM MOVIEINFO,MOVIEAUCTION WHERE MOVIEINFO.MOVIE_ID = MOVIEAUCTION.MOVIE_ID;")
      movieInfoCards = cur.fetchall()
      temp = []
      for i in movieInfoCards:
         temp.append(list(i))
      movieInfoCards = temp
      print("Number of Movies queryed", len(movieInfoCards))
      print(movieInfoCards)
      for i in range(0,len(movieInfoCards)):
         timeleft = datetime.now() - datetime.strptime(str(movieInfoCards[i][16]),'%Y-%m-%d %H:%M')
         movieInfoCards[i].append(timeleft)
      return render_template('all_movie_auctions.html',username=username,movieInfo = movieInfoCards)

@app.route('/removeMovieAuction/<auctionID>',methods = ['POST', 'GET'])
def removeMovieAuction(auctionID):
   try:
      with sql.connect("MovieAuctionDB.db") as con:
         cur = con.cursor()
         print('Auction ID =',auctionID)
         cur.execute("DELETE FROM MOVIEAUCTION WHERE MOVIE_AUC_ID = ? ;",(auctionID,))
         con.commit()
         msg = "Movie Successfully Removed"
      return redirect(url_for('mymovieauctions'))
   except Exception as e:
      con.rollback()
      app.logger.info(e)
      return redirect(url_for('mymovieauctions'))

@app.route('/mymovies')
def mymovies():
   with sql.connect("MovieAuctionDB.db") as con:
      cur = con.cursor()
      cur.execute(f"SELECT * FROM MOVIEINFO where USER_ID={global_user_id}")
      movieInfoCards = cur.fetchall()
      print("Number of Movies queryed", len(movieInfoCards))
      return render_template('mymovies.html',username=username,movieInfo = movieInfoCards)

@app.route('/mymovieauctions')
def mymovieauctions():
   with sql.connect("MovieAuctionDB.db") as con:
      cur = con.cursor()
      cur.execute(f"SELECT * FROM MOVIEINFO,MOVIEAUCTION WHERE MOVIEINFO.USER_ID={global_user_id} AND MOVIEAUCTION.USER_ID={global_user_id} AND MOVIEINFO.MOVIE_ID = MOVIEAUCTION.MOVIE_ID;")
      movieInfoCards = cur.fetchall()
      temp = []
      for i in movieInfoCards:
         temp.append(list(i))
      movieInfoCards = temp
      print("Number of Movies queryed", len(movieInfoCards))
      print(movieInfoCards)
      for i in range(0,len(movieInfoCards)):
         timeleft = datetime.now() - datetime.strptime(str(movieInfoCards[i][16]),'%Y-%m-%d %H:%M')
         movieInfoCards[i].append(timeleft)
      return render_template('mymovieauctions.html',username=username,movieInfo = movieInfoCards)
      
@app.route('/addMovieAuction')
def addMovieAuctionPage():
   return render_template('movie_auction_entry.html', msg='',name2=username)

#adding an item for sale 
@app.route('/addMovieAuction',methods = ['POST', 'GET'])
def addMovieAuction():
   global cart 
   cart = []
   name = request.form['name']
   year = request.form['year']
   desc = request.form['desc']
   price = request.form['price']
   imgurl = request.form['imgurl']
   date = request.form['date']
   time = request.form['time']
   print("this is the date and time", date,time)
   if len(name) != 0 and len(year) != 0 and len(desc) != 0 and len(price)!=0 and len(date)!=0 and len(time)!=0 :
      try:
         with sql.connect("MovieAuctionDB.db") as con:
            # insert info
            cur = con.cursor()
            if len(imgurl)==0:
               cur.execute("INSERT INTO MOVIEINFO (NAME,YEAR,DESC,PRICE,USER_ID) VALUES(?,?,?,?,?);",(name,year,desc,price,global_user_id))
            else:         
               cur.execute("INSERT INTO MOVIEINFO (NAME,YEAR,DESC,PRICE,IMGURL,USER_ID) VALUES(?,?,?,?,?,?);",(name,year,desc,price,imgurl,global_user_id))
            cur.execute("SELECT last_insert_rowid();")
            movieID = cur.fetchall()    
            msg = "Record successfully added"
            cur.execute("INSERT INTO MOVIEAUCTION (TITLE,YEAR,DESC,PRICE,USER_ID,BUY_NOW,SOLD,TIME_END,MOVIE_ID) VALUES(?,?,?,?,?,?,?,?,?)",(name,year,desc,float(price)/4,global_user_id,'FALSE','FALSE',date+" "+time,movieID[0][0]))
            con.commit()
         return redirect(url_for('success',name = username))
      except Exception as e:
         con.rollback()
         print(e)
         app.logger.info(e)
         return render_template('movie_auction_entry.html', msg='Error in entered information exception found')
   else:
      return render_template('movie_auction_entry.html', msg='Error in entered information, Please fill out again')



# code starting position - Sixing Zheng

# login functions
# After login and sign up correctly, go to this function
@app.route('/<name>')
def success(name):
   global movieInfoCards 
   with sql.connect("MovieAuctionDB.db") as con:
      cur = con.cursor()
      cur.execute("SELECT * FROM MOVIEINFO LIMIT 8")
      movieInfoCards = cur.fetchall()
   return render_template('index.html', username = name,cartCounter=len(cart), movieInfo = movieInfoCards)

# route to the login page
@app.route('/login')
def login_page():
   return render_template('login.html')

# route to the login page with custom message
@app.route('/login/<msg>')
def login_again(msg):
   return render_template('login.html', msg=msg)

# gettting the information for login and check for password
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
# route to the sign up page
@app.route('/signup')
def signup_page():
   return render_template('signup.html')

# route to the sign up page with custom message
@app.route('/signup/<msg>')
def signup_again(msg):
   return render_template('signup.html', msg=msg)

# getting the information for the form submmitted with the sign up page
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
            global username
            username = user
            app.logger.info(global_user_id)
            app.logger.info('last row id')
            app.logger.info(rows[0]['user_id'])
            cur.execute(f"INSERT INTO WISHLIST (USER_ID) VALUES('{global_user_id}');")
            con.commit()
         return redirect(url_for('success',name = user))
      except Exception as e:
         con.rollback()
         app.logger.info(e)
         return redirect(url_for('signup_again', msg='Error in entered information.'))
   else:
      return redirect(url_for('signup_again', msg='Passwords do not match.'))

# user_profile
# route to user profile with feedback message
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

# route to the user profile without feedback message
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

# code ending position - Sixing Zheng

# code starting position - Reed Billedo

# add a movie from the home page onto the user's wishlist
@app.route('/index/<title>', methods = ['POST', 'GET'])
def addToWishlist(title):
   try:
      with sql.connect("MovieAuctionDB.db") as con:
         global global_user_id
         con = sql.connect("MovieAuctionDB.db")
         con.row_factory = sql.Row

         # check if the the movie they are trying to add is already in the wishlist
         cur = con.cursor()
         cur.execute(f"SELECT MOVIE_ID FROM WISHLISTBRIDGE WHERE WISHLIST_ID = (SELECT WISHLIST_ID FROM WISHLIST WHERE USER_ID = '{global_user_id}');")
         movie_ids = cur.fetchall()
         for i in movie_ids:
            if(i['MOVIE_ID'] == title):
               con.rollback()
               return redirect(url_for('home'))

         # if it is not, add to wishlist
         cur.execute(f"INSERT INTO WISHLISTBRIDGE (WISHLIST_ID, MOVIE_ID) VALUES((SELECT WISHLIST_ID FROM WISHLIST WHERE USER_ID = '{global_user_id}'),'{title}');")
         con.commit()
   except:
      con.rollback()
   return redirect(url_for('home'))

# takes the user to their page that lists their wishlist
@app.route('/wishlist')
def wishlist():
   con = sql.connect("MovieAuctionDB.db")
   con.row_factory = sql.Row

   # get the items from wishlistbridge where the user's id is
   cur = con.cursor()
   cur.execute(f"SELECT * FROM WISHLISTBRIDGE WHERE WISHLIST_ID = (SELECT WISHLIST_ID FROM WISHLIST WHERE USER_ID = '{global_user_id}');")
   rows = cur.fetchall()

   # get the movie names from the query earlier
   movienames = []
   for i in rows:
      cur.execute(f"SELECT NAME FROM MOVIEINFO WHERE MOVIE_ID = '{i['MOVIE_ID']}';")
      n = cur.fetchall()
      movienames.append(n[0]['NAME'])
   app.logger.info(movienames)

   return render_template("wishlist.html", rows=rows, movienames = movienames, len = len(rows))

# removes the movie from the user's wishlist
@app.route('/deleteFromWishlist/<wish_id>/<movie>', methods = ['POST','GET'])
def deleteFromWishlist(wish_id, movie):
   with sql.connect("MovieAuctionDB.db") as con:
      global global_user_id
      cur = con.cursor()
      # deletes the item from wishlistbridge where the wishlist_id and movie_id match
      cur.execute(f"DELETE FROM WISHLISTBRIDGE WHERE WISHLIST_ID = '{wish_id}' OR MOVIE_ID = '{movie}';")
      con.commit()

   return redirect(url_for('wishlist'))

# renders the page that lets the user add a review
@app.route('/review')
def review_default():
   con = sql.connect("MovieAuctionDB.db")
   con.row_factory = sql.Row

   cur = con.cursor()
   cur.execute(f"SELECT * from MOVIEINFO;")
   movies = cur.fetchall()
   return render_template("review.html",movies=movies)

# gets the data from the review page in order to add new entry to review table
@app.route('/review',methods = ['POST','GET'])
def review():
   value = request.form['selectedMovie']
   review_content = request.form['review_content']
   rating = request.form['rating']

   try:
      with sql.connect("MovieAuctionDB.db") as con:
         global global_user_id
         global global_user_id
         con = sql.connect("MovieAuctionDB.db")
         con.row_factory = sql.Row
         cur = con.cursor()
         # checks if the user has already made a review for this movie
         cur.execute(f"SELECT MOVIE_ID FROM REVIEW WHERE USER_ID = {global_user_id};")
         movie_ids = cur.fetchall()

         for i in movie_ids:
            if(i['MOVIE_ID'] == value):
               return redirect(url_for('review'))

         # if it has not, adds it to the review table
         cur.execute("INSERT INTO REVIEW (USER_ID, MOVIE_ID, RATING, REVIEW_CONTENT) VALUES(?,?,?,?);", (global_user_id,value,rating,review_content))
         con.commit()
      return redirect(url_for('home'))
   except:
      con.rollback()
      return redirect(url_for('home'))

# gets all of the reviews for a specific movie
@app.route('/reviews/<title>',methods = ['POST','GET'])
def allMovieReviews(title):
   try:
      with sql.connect("MovieAuctionDB.db") as con:
         con.row_factory = sql.Row
         cur = con.cursor()
         cur.execute(f"SELECT * from REVIEW WHERE MOVIE_ID = '{title}';")
         reviews = cur.fetchall()
         app.logger.info(reviews)

         # gets the name of the movie for the top of the page
         cur.execute(f"SELECT NAME FROM MOVIEINFO WHERE MOVIE_ID = '{title}'")
         names = cur.fetchall()
         return render_template("all_movie_reviews.html",reviews=reviews, names=names)
   except:
         con.rollback()
         return redirect(url_for('home'))

# gets all of the reviews that a specific user has written
@app.route('/myreviews')
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

         # checks if the user has already written the movie
         movienames = []
         for i in reviews:
            cur.execute(f"SELECT NAME FROM MOVIEINFO WHERE MOVIE_ID = '{i['MOVIE_ID']}';")
            n = cur.fetchall()
            movienames.append(n[0]['NAME'])
         app.logger.info(movienames)

        # cur.execute(f"SELECT NAME FROM MOVIEINFO WHERE MOVIE_ID IN(SELECT MOVIE_ID FROM REVIEW WHERE USER_ID = {global_user_id});")
        # movienames = cur.fetchall()
         app.logger.info(len(movienames))
         app.logger.info(global_user_id)
         app.logger.info(len(names))
         return render_template("all_user_reviews.html",reviews=reviews, names=names, movienames = movienames, len = len(reviews)) #<p>{{movienames[i]["NAME"]}}</p>
   except:
      con.rollback()
      return redirect(url_for('home'))

# allows the user to edit the reviews they have made
@app.route('/myreviews',methods = ['POST','GET'])
def updatemyreviews():
   newRating = request.form['new_rating']
   newReviewContent = request.form['new_review_content']
   id = request.form['id']
   try:
      with sql.connect("MovieAuctionDB.db") as con:
         cur = con.cursor()
         cur.execute(f"UPDATE REVIEW SET RATING = '{newRating}', REVIEW_CONTENT = '{newReviewContent}' WHERE REVIEW_ID = '{id}'; ")
         return redirect(url_for('myreviews'))

   except:
         con.rollback()
         return redirect(url_for('home'))

# allows the user to delete a review from their account
@app.route('/deleteFromReview/<id>', methods = ['POST','GET'])
def deleteFromReview(id):
   with sql.connect("MovieAuctionDB.db") as con:
      global global_user_id
      cur = con.cursor()
      cur.execute(f"DELETE FROM REVIEW WHERE REVIEW_ID = '{id}';")
      con.commit()

   return redirect(url_for('myreviews'))

# code ending - Reed Billedo


#Charles Tran Code Starts Here
#Queries for all of the cart and user data in order to process a transaction
#Shows data from cart
@app.route('/checkout',methods = ['POST', 'GET'])
def checkout():
   # Grabs user checkout info for them to review it
   with sql.connect("MovieAuctionDB.db") as con:
      con.row_factory = sql.Row
      cur = con.cursor()
      #SQL command to select all data from USER table
      cur.execute(f"select * from USER where user_id = '{global_user_id}';")
      rows = cur.fetchall()
      username = rows[0]['username']
      email = rows[0]['email']
      card = rows[0]['card']
      card_exp_date = rows[0]['card_exp_date']
      billing_addr = rows[0]['billing_addr']
      zip_code = rows[0]['zip_code']
      
   #inputs cart in order to display it at checkout
   return render_template('checkout.html',username=username, email=email, card=card, card_exp_date=card_exp_date, billing_addr=billing_addr, zip_code=zip_code,cart = cart)



#Processes a transaction by adding the movie from the cart into the transactions table.
#Then the movie is deleted from the movie database since it has been purchased.
@app.route('/transaction')
def transaction():
   with sql.connect("MovieAuctionDB.db") as con:
      #Must have one item in cart in order to process transaction
      if(len(cart)>0):
         try:
            con.row_factory = sql.Row
            cur = con.cursor()
            cur.execute(f"select * from USER where user_id = '{global_user_id}';")
            rows = cur.fetchall()
            # INSERT INTO TRANSACTIONS
            for i in range(len(cart)):
               cur.execute("INSERT INTO TRANSACTIONS (USER_ID,MOVIE_AUC_ID,NAME,CASH_AMOUNT) VALUES(?,?,?,?);",(global_user_id,cart[i][0],cart[i][1],cart[i][4]))
               con.commit()
            #Deletes contents from cart and deletes from Movie Inventory
            for i in range(len(cart)):
               if((cart[0][1])!=''):
                  print("Deleting "+cart[0][1])
                  cur.execute("DELETE FROM MOVIEINFO WHERE MOVIE_ID == "+str(cart[0][0])+";")
                  con.commit()
                  cart.pop(0)
               else:
                  cart.pop(0)
            return transactionlog("Your Transaction was Successful")
         except Exception as e:
            #if there is an error we got to the transaction menu with an error message
            con.rollback()
            app.logger.info(e)
            msg = "Your Transaction was not successful"
            return render_template('transaction.html',cart = [],msg=msg)
      
#Provides a log of transactions that the user has done.      
@app.route('/transactionlog')
def transactionlog(msg=""):
   with sql.connect("MovieAuctionDB.db") as con:
      cur = con.cursor() 
      #Fetches movies to display in transactions tab  
      cur.execute("SELECT * FROM TRANSACTIONS WHERE USER_ID = "+str(global_user_id)+";")
      transaction = cur.fetchall()
      
      #will export transaction log with all of the movies the user id has purchased. msg is used for if there is a successful purchase or an error.
      return render_template('transaction.html',cart = transaction,msg=msg)
#Charles Tran Code Ends Here


if __name__ == '__main__':
   app.run(debug = True)