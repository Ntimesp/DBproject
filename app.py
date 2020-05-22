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
    res=[]
    if request.method == 'POST':
        print(request.form)
        cursor = conn.cursor()
        op=request.form["query"]
        if op=="insert":
            sql="""
            insert into Campus (Campus_id, Campus_name, Campus_address) values (%s,%s,%s);
            """
            Campus_id=request.form["Campus_id"]
            Campus_name=request.form["Campus_name"]
            Campus_address=request.form["Campus_address"]
            cursor.execute(sql, [Campus_id, Campus_name, Campus_address])
            flash("操作成功")
        elif op=="delete":
            sql="""
            delete from Campus where Campus_id=%s;
            """
            Campus_id=request.form["Campus_id"]
            cursor.execute(sql, Campus_id)
            flash("操作成功")
        elif op=="select":
            Campus_id=request.form["Campus_id"]
            Campus_name=request.form["Campus_name"]
            Campus_address=request.form["Campus_address"]
            if not Campus_id + Campus_name + Campus_address:
                sql="select * from Campus"
            else:
                sql="select * from Campus where 1=1"
                if Campus_id:
                    sql=sql+" and Campus_id="+"\""+Campus_id+"\""

                if Campus_name:
                    sql=sql+" and Campus_name="+"\""+Campus_name+"\""
                
                if Campus_address:
                    sql=sql+" and Campus_address="+"\""+Campus_address+"\""

            cursor.execute(sql)
            flash("操作成功")
            res=cursor.fetchall()
        elif op=="update":
            Campus_id=request.form["Campus_id"]
            Campus_name=request.form["Campus_name"]
            Campus_address=request.form["Campus_address"]
            if not Campus_name + Campus_address:
                flash("什么也不做")
            else:
                sql="update Campus set"
                if Campus_name:
                    sql=sql+" Campus_name="+"\""+Campus_name+"\","
                
                if Campus_address:
                    sql=sql+" Campus_address="+"\""+Campus_address+"\""
                sql=sql+" where Campus_id="+"\""+Campus_id+"\""
                print(sql)
                cursor.execute(sql)
                flash("操作成功")
        cursor.close()
    return render_template('campus.html',campus=res)

@app.route('/major', methods=['GET', 'POST'])
def major():
    return render_template('major.html')
@app.route('/classes', methods=['GET', 'POST'])
def classes():
    return render_template('class.html')
@app.route('/student', methods=['GET', 'POST'])
def student():
    return render_template('student.html')
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
