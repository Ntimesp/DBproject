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
    user='root',
    database="lab3",
    charset="utf8")


@app.route('/index')
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/campus', methods=['GET', 'POST'])
def campus():
    res = []
    if request.method == 'POST':
        print(request.form)
        cursor = conn.cursor()
        op = request.form["query"]
        if op == "insert":
            sql = """
            insert into Campus (Campus_id, Campus_name, Campus_address) values (%s,%s,%s);
            """
            Campus_id = request.form["Campus_id"]
            Campus_name = request.form["Campus_name"]
            Campus_address = request.form["Campus_address"]
            cursor.execute(sql, [Campus_id, Campus_name, Campus_address])
            flash("操作成功")
            res = cursor.fetchall()
        elif op == "delete":
            sql = """
            delete from Campus where Campus_id=%s;
            """
            Campus_id = request.form["Campus_id"]
            cursor.execute(sql, Campus_id)
            flash("操作成功")
            res = cursor.fetchall()
        elif op == "select":
            Campus_id = request.form["Campus_id"]
            Campus_name = request.form["Campus_name"]
            Campus_address = request.form["Campus_address"]
            if not Campus_id + Campus_name + Campus_address:
                sql = "select * from Campus"
            else:
                sql = "select * from Campus where 1=1"
                if Campus_id:
                    sql = sql + " and Campus_id=" + "\"" + Campus_id + "\""
                if Campus_name:
                    sql = sql + " and Campus_name=" + "\"" + Campus_name + "\""
                if Campus_address:
                    sql = sql + " and Campus_address=" + "\"" + Campus_address + "\""
            cursor.execute(sql)
            flash("操作成功")
            res = cursor.fetchall()
        elif op == "update":
            Campus_id = request.form["Campus_id"]
            Campus_name = request.form["Campus_name"]
            Campus_address = request.form["Campus_address"]
            if not Campus_name + Campus_address:
                flash("什么也不做")
            else:
                sql = "update Campus set"
                if Campus_name:
                    sql = sql + " Campus_name=" + "\"" + Campus_name + "\","
                if Campus_address:
                    sql = sql + " Campus_address=" + "\"" + Campus_address + "\""
                sql = sql + " where Campus_id=" + "\"" + Campus_id + "\""
                print(sql)
                cursor.execute(sql)
                flash("操作成功")
                res = cursor.fetchall()
        cursor.close()
    else:
        cursor = conn.cursor()
        sql = """
            select * from Campus;
            """
        cursor.execute(sql)
        res = cursor.fetchall()
        cursor.close()
    return render_template('campus.html', campus=res)


@app.route('/major', methods=['GET', 'POST'])
def major():
    res = []
    if request.method == 'POST':
        print(request.form)
        cursor = conn.cursor()
        op = request.form["query"]
        if op == "insert":
            sql = """
                insert into Major (Major_id, Major_name, Major_address, Major_campus_id, Major_leader) 
                values (%s,%s,%s, %s, %s);
                """
            Major_id = request.form["major_id"]
            Major_name = request.form["major_name"]
            Major_address = request.form["major_address"]
            Major_campus_id = request.form["major_campus"]
            Major_leader = request.form["major_leader"]
            cursor.execute(sql, [Major_id, Major_name, Major_address, Major_campus_id, Major_leader])
            flash("操作成功")
            res = cursor.fetchall()
        elif op == "delete":
            sql = """
                delete from Major where Major_id=%s;
                """
            Major_id = request.form["major_id"]
            cursor.execute(sql, Major_id)
            flash("操作成功")
            res = cursor.fetchall()
        elif op == "select":
            Major_id = request.form["major_id"]
            Major_name = request.form["major_name"]
            Major_address = request.form["major_address"]
            Major_campus_id = request.form["major_campus"]
            Major_leader = request.form["major_leader"]
            if not Major_id + Major_name + Major_address + Major_campus_id + Major_leader:
                sql = "select * from Major"
            else:
                sql = "select * from Major where 1=1"
                if Major_id:
                    sql = sql + " and Major_id=" + "\"" + Major_id + "\""
                if Major_name:
                    sql = sql + " and Major_name=" + "\"" + Major_name + "\""
                if Major_address:
                    sql = sql + " and Major_address=" + "\"" + Major_address + "\""
                if Major_campus_id:
                    sql = sql + " and Major_campus_id=" + "\"" + Major_campus_id + "\""
                if Major_leader:
                    sql = sql + " and Major_leader=" + "\"" + Major_leader + "\""
            cursor.execute(sql)
            flash("操作成功")
            res = cursor.fetchall()
        elif op == "update":
            Major_id = request.form["major_id"]
            Major_name = request.form["major_name"]
            Major_address = request.form["major_address"]
            Major_campus_id = request.form["major_campus"]
            Major_leader = request.form["major_leader"]
            if not Major_name + Major_address + Major_campus_id + Major_leader:
                flash("什么也不做")
            else:
                sql = "update Major set"
                if Major_name:
                    sql = sql + " Major_name=" + "\"" + Major_name + "\","
                if Major_address:
                    sql = sql + " Major_address=" + "\"" + Major_address + "\""
                if Major_campus_id:
                    sql = sql + " Major_campus_id=" + "\"" + Major_campus_id + "\""
                if Major_leader:
                    sql = sql + " Major_leader=" + "\"" + Major_leader + "\""
                sql = sql + " where Major_id=" + "\"" + Major_id + "\""
                print(sql)
                cursor.execute(sql)
                flash("操作成功")
                res = cursor.fetchall()
        cursor.close()
    else:
        cursor = conn.cursor()
        sql = """
            select * from Major;
            """
        cursor.execute(sql)
        res = cursor.fetchall()
        cursor.close()
    return render_template('major.html', major=res)


@app.route('/classes', methods=['GET', 'POST'])
def classes():
    res = []
    if request.method == 'POST':
        print(request.form)
        cursor = conn.cursor()
        op = request.form["query"]
        if op == "insert":
            sql = """
                    insert into Class (Class_id, Class_name, Class_create_date, Class_head_teacher, Class_grade, Class_major) 
                    values (%s,%s,%s, %s, %s, %s);
                    """
            Class_id = request.form["class_id"]
            Class_name = request.form["class_name"]
            Class_create_date = request.form["class_create_date"]
            Class_head_teacher = request.form["class_teacher"]
            Class_grade = request.form["class_grade"]
            Class_major = request.form["class_major"]
            cursor.execute(sql, [Class_id, Class_name, Class_create_date, Class_head_teacher, Class_grade, Class_major])
            flash("操作成功")
            res = cursor.fetchall()
        elif op == "delete":
            sql = """
                    delete from Class where Class_id=%s;
                    """
            Class_id = request.form["class_id"]
            cursor.execute(sql, Class_id)
            flash("操作成功")
            res = cursor.fetchall()
        elif op == "select":
            Class_id = request.form["class_id"]
            Class_name = request.form["class_name"]
            Class_create_date = request.form["class_create_date"]
            Class_head_teacher = request.form["class_teacher"]
            Class_grade = request.form["class_grade"]
            Class_major = request.form["class_major"]
            if not Class_id + Class_name + Class_create_date + Class_head_teacher + Class_grade + Class_major:
                sql = "select * from Class"
            else:
                sql = "select * from Class where 1=1"
                if Class_id:
                    sql = sql + " and Class_id=" + "\"" + Class_id + "\""
                if Class_name:
                    sql = sql + " and Class_name=" + "\"" + Class_name + "\""
                if Class_create_date:
                    sql = sql + " and Class_create_date=" + "\"" + Class_create_date + "\""
                if Class_head_teacher:
                    sql = sql + " and Class_head_teacher=" + "\"" + Class_head_teacher + "\""
                if Class_grade:
                    sql = sql + " and Class_grade=" + "\"" + Class_grade + "\""
                if Class_major:
                    sql = sql + " and Class_major=" + "\"" + Class_major + "\""
            cursor.execute(sql)
            flash("操作成功")
            res = cursor.fetchall()
        elif op == "update":
            Class_id = request.form["class_id"]
            Class_name = request.form["class_name"]
            Class_create_date = request.form["class_create_date"]
            Class_head_teacher = request.form["class_teacher"]
            Class_grade = request.form["class_grade"]
            Class_major = request.form["class_major"]
            if not Class_name + Class_create_date + Class_head_teacher + Class_grade + Class_major:
                flash("什么也不做")
            else:
                sql = "update Class set"
                if Class_name:
                    sql = sql + " Class_name=" + "\"" + Class_name + "\","
                if Class_create_date:
                    sql = sql + " Class_create_date=" + "\"" + Class_create_date + "\""
                if Class_head_teacher:
                    sql = sql + " Class_head_teacher=" + "\"" + Class_head_teacher + "\""
                if Class_grade:
                    sql = sql + " Class_grade=" + "\"" + Class_grade + "\""
                if Class_major:
                    sql = sql + " Class_major=" + "\"" + Class_major + "\""
                sql = sql + " where Class_id=" + "\"" + Class_id + "\""
                print(sql)
                cursor.execute(sql)
                flash("操作成功")
                res = cursor.fetchall()
        cursor.close()
    else:
        cursor = conn.cursor()
        sql = """
            select * from Class;
            """
        cursor.execute(sql)
        res = cursor.fetchall()
        cursor.close()
    return render_template('class.html', classes=res)


@app.route('/student', methods=['GET', 'POST'])
def student():
    res = []
    if request.method == 'POST':
        print(request.form)
        cursor = conn.cursor()
        op = request.form["query"]
        if op == "insert":
            sql = """
                        insert into Student (Student_id, Student_person_id, Student_email, Student_class, Student_major_id, Student_time_of_enrollment) 
                        values (%s,%s,%s, %s, %s, %s);
                        """
            Student_id = request.form["student_id"]
            Student_person_id = request.form["student_person_id"]
            Student_email = request.form["student_email_address"]
            Student_class = request.form["student_class"]
            Student_major_id = request.form["student_major"]
            Student_time_of_enrollment = request.form["student_enrollment"]
            cursor.execute(sql, [Student_id, Student_person_id, Student_email, Student_class, Student_major_id, Student_time_of_enrollment])
            flash("操作成功")
            res = cursor.fetchall()
        elif op == "delete":
            sql = """
                        delete from Student where Student_id=%s;
                        """
            Student_id = request.form["student_id"]
            cursor.execute(sql, Student_id)
            flash("操作成功")
            res = cursor.fetchall()
        elif op == "select":
            Student_id = request.form["student_id"]
            Student_person_id = request.form["student_person_id"]
            Student_email = request.form["student_email_address"]
            Student_class = request.form["student_class"]
            Student_major_id = request.form["student_major"]
            Student_time_of_enrollment = request.form["student_enrollment"]
            if not Student_id + Student_person_id + Student_email + Student_class + Student_major_id + Student_time_of_enrollment:
                sql = "select * from Student"
            else:
                sql = "select * from Student where 1=1"
                if Student_id:
                    sql = sql + " and Student_id=" + "\"" + Student_id + "\""
                if Student_person_id:
                    sql = sql + " and Student_person_id=" + "\"" + Student_person_id + "\""
                if Student_email:
                    sql = sql + " and Student_email=" + "\"" + Student_email + "\""
                if Student_class:
                    sql = sql + " and Student_class=" + "\"" + Student_class + "\""
                if Student_major_id:
                    sql = sql + " and Student_major_id=" + "\"" + Student_major_id + "\""
                if Student_time_of_enrollment:
                    sql = sql + " and Student_time_of_enrollment=" + "\"" + Student_time_of_enrollment + "\""
            cursor.execute(sql)
            flash("操作成功")
            res = cursor.fetchall()
        elif op == "update":
            Student_id = request.form["student_id"]
            Student_person_id = request.form["student_person_id"]
            Student_email = request.form["student_email_address"]
            Student_class = request.form["student_class"]
            Student_major_id = request.form["student_major"]
            Student_time_of_enrollment = request.form["student_enrollment"]
            if not Student_person_id + Student_email + Student_class + Student_major_id + Student_time_of_enrollment:
                flash("什么也不做")
            else:
                sql = "update Student set"
                if Student_person_id:
                    sql = sql + " Student_person_id=" + "\"" + Student_person_id + "\","
                if Student_email:
                    sql = sql + " Student_email=" + "\"" + Student_email + "\""
                if Student_class:
                    sql = sql + " Student_class=" + "\"" + Student_class + "\""
                if Student_major_id:
                    sql = sql + " Student_major_id=" + "\"" + Student_major_id + "\""
                if Student_time_of_enrollment:
                    sql = sql + " Student_time_of_enrollment=" + "\"" + Student_time_of_enrollment + "\""
                sql = sql + " where Student_id=" + "\"" + Student_id + "\""
                print(sql)
                cursor.execute(sql)
                flash("操作成功")
                res = cursor.fetchall()
        cursor.close()
    else:
        cursor = conn.cursor()
        sql = """
                select * from Student;
                """
        cursor.execute(sql)
        res = cursor.fetchall()
        cursor.close()
    return render_template('student.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
