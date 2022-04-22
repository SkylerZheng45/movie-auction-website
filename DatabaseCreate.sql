
--USER TABLE
CREATE TABLE USER(
   USER_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
   EMAIL CHAR(50) NOT NULL,
   USERNAME    CHAR(50) NOT NULL,
   PASSWORD    CHAR(50) NOT NULL,
   CARD        CHAR(50),
   CARD_EXP_DATE CHAR(20),
   BILLING_ADDR CHAR(50),
   ZIP_CODE CHAR(10),
   AGE         INTEGER NOT NULL
);

--Movie Info
CREATE TABLE MOVIEINFO(
    MOVIE_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    NAME CHAR(50) NOT NULL,
    YEAR INT NOT NULL,
    DESC TEXT NOT NULL
);

--WishList Table
CREATE TABLE WISHLIST(
    WISHLIST_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    USER_ID REFERENCES USER(USER_ID)
);

--Review Table
CREATE TABLE REVIEW(
    REVIEW_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    USER_ID REFERENCES USER(USER_ID),
    MOVIE_ID REFERENCES MOVIEINFO(MOVIE_ID),
    RATING INT NOT NULL,
    REVIEW_CONTENT TEXT NOT NULL 
);

--Movie Auctions
CREATE TABLE MOVIEAUCTION(
    MOVIE_AUC_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    USER_ID REFERENCES USER(USER_ID),
    TITLE CHAR(50) NOT NULL,
    YEAR INT NOT NULL,
    DESC TEXT NOT NULL,
    PRICE FLOAT NOT NULL,
    MOVIE_ID REFERENCES MOVIEINFO(MOVIE_ID),
    BUY_NOW BOOL NOT NULL,
    SOLD BOOL NOT NULL

);

--Transactions
CREATE TABLE TRANSACTIONS(
    TRANSACTION_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    USER_ID REFERENCES USER(USER_ID),
    MOVIE_AUC_ID REFERENCES MOVIEAUCTION(MOVIE_AUC_ID),
    CASH_AMOUNT FLOAT NOT NULL
);

ALTER TABLE MOVIEAUCTION
ADD TRANSACTION_ID REFERENCES TRANSACTIONS(TRANSACTION_ID);

