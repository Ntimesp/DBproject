# -*- coding : utf-8 -*-
# coding: utf-8

from flask import *
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import *
import pymysql

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = 'cbYSt76Vck*7^%4d'

conn = pymysql.connect(
    host="localhost",
    user='root',password="123456",
    database="lab3",
    charset="utf8")

@app.route('/index')
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/campus', methods=['GET', 'POST'])
def campus():
    if request.method == 'POST':
        cursor = conn.cursor()
        sql="""
        insert into Campus (Campus_id, Campus_name, Campus_address) values (%s,%s,%s);
        """
        Campus_id=request.form["Campus_id"]
        Campus_name=request.form["Campus_name"]
        Campus_address=request.form["Campus_address"]
        res=cursor.execute(sql, [Campus_id, Campus_name, Campus_address])
        cursor.close()
        flash("操作成功")
    
    cursor = conn.cursor()
    sql="""
    select * from Campus
    """
    cursor.execute(sql)
    res=cursor.fetchall()
    cursor.close()
    return render_template('campus.html',campus=res)



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
