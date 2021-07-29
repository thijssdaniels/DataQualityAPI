import sqlite3

from sqlalchemy import Table, create_engine, Column, Integer, String

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import configparser

conn = sqlite3.connect('data.sqlite')
engine = create_engine('sqlite:///data.sqlite')
db = SQLAlchemy()
config = configparser.ConfigParser()


# Replace with Azure SQL Database
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))


# This provides default implementations for the methods that Flask-#Login expects user objects to have
# class Users(UserMixin, Users):
#    pass


# Function to create table using Users class
def create_users_table():
    Users.metadata.create_all(engine)


# Create the table
create_users_table()

Users_tbl = Table('users', Users.metadata)
