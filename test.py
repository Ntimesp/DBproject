from flask import *
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import *
import pymysql

app = Flask(__name__)
bootstrap = Bootstrap(app)

conn = pymysql.connect(
    host="localhost",
    user='root',password="",
    database="lab3",
    charset="utf8")

cursor = conn.cursor()
sql="""
select * from Campus
"""
cursor.execute(sql)
res=cursor.fetchall()
cursor.close()
conn.close()

print(res)
