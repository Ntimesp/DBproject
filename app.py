# -*- coding : utf-8 -*-
# coding: utf-8

import os
from threading import Thread
import time
from datetime import datetime, timedelta, date
import io
from io import BytesIO
import base64
import random 
##from sh import git

from flask import *
from flask_bootstrap import Bootstrap
from flask_talisman import Talisman
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import *
from sqlalchemy.sql.expression import func
from wtforms.validators import *
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, fresh_login_required, login_user, login_fresh, login_url, LoginManager, \
    UserMixin, logout_user, current_user
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from cas_client import *
from sqlalchemy import *

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

basedir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
Talisman(app, content_security_policy={
    'default-src': "*",
    'style-src': "'self' http://* 'unsafe-inline'",
    'script-src': "'self' http://* 'unsafe-inline' 'unsafe-eval'",
    'img-src': "'self' http://* 'unsafe-inline' data: *",
})
app.config['SECRET_KEY'] = 'cbYSt76Vck*7^%4d'
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:123456@localhost/test?charset=utf8"
app.config['SQLALCHEMY_POOL_RECYCLE'] = 10
app.config['SQLALCHEMY_POOL_SIZE'] = 30
app.config['MAX_CONTENT_LENGTH']=10*1024*1024  #最大10MB
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SERVER_NAME'] = 'stunion.ustc.edu.cn'
# app.config['SERVER_NAME'] = 'localhost.localdomain'


app.config['MAIL_SERVER'] = 'smtp.163.com'  # 邮箱服务器
app.config['MAIL_PORT'] = 25  # 端口
# app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = "ustcstuniongirl@163.com"
app.config['MAIL_PASSWORD'] = "STUNION2020"

mail = Mail(app)
login_manager = LoginManager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
login_manager.session_protection = "strong"
timelimit = 1

NOT_START_STRING = "活动尚未开始。"
NOT_ACTIVATE_STRING = "对不起，你的账户还未激活！"
FEMALE = 0
MALE = 1


# GIT_DATA = git.log('-1', '--pretty=%H%n%an%n%s').strip().split("\n")
def checkTimeLimit():
    # 返回1则正在活动
    nowtime = datetime.now()
    starttime = datetime(2020, 2, 6, 20, 0, 0, 0)
    endtime = datetime(2020, 3, 17, 0, 0, 0, 0)
    return starttime <= nowtime < endtime


# 格式化邮件
def mySendMailFormat(mailSubject, mailSender, mailRecv, mailBody, templates, **kwargs):
    msg = Message(mailSubject, sender=mailSender, recipients=[mailRecv])
    msg.body = render_template(templates + ".txt", **kwargs)
    msg.html = render_template(templates + ".html", **kwargs)
    return msg


# 异步发送邮件函数
def sendMailSyncFuc(app, msg):
    with app.app_context():
        mail.send(msg)


def simpleSendMail(app, msg):
    thr = Thread(target=sendMailSyncFuc, args=[app, msg])
    thr.start()
    return thr


# @app.context_processor
# def git_revision():
#    return {'git_revision': "Revision {}".format(GIT_DATA[0][:7])}


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True, nullable=True)
    userEmail = db.Column(db.String(64), unique=True, index=True, nullable=True)
    userStatus = db.Column(db.Integer, default=1)
    # userStatus == 0 未激活
    # userStatus == 1 已经激活
    userAccountLevel = db.Column(db.Integer, nullable=True)
    userRealName = db.Column(db.String(128), nullable=True)
    userSchoolNum = db.Column(db.String(64), unique=True, nullable=True)
    userQQnum = db.Column(db.String(64), nullable=True)
    userTelnum = db.Column(db.String(64), nullable=True)
    userSex = db.Column(db.Integer, nullable=True)
    userWeChatNum = db.Column(db.String(64), nullable=True)
    userCellPhoneNum = db.Column(db.String(64), nullable=True)
    userOpenid = db.Column(db.String(256), nullable=True)
    userPasswordHash = db.Column(db.String(256), nullable=True)
    userSecretText = db.Column(db.String(64), nullable=True)
    userNickName = db.Column(db.String(64), nullable=True)

    def setPassword(self, password):
        self.userPasswordHash = generate_password_hash(password)

    def verifyPassword(self, password):
        return check_password_hash(self.userPasswordHash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except Exception:
            return False
        if data.get('confirm') != self.id:
            return False
        self.userStatus = 1
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except Exception:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.setPassword(new_password)
        db.session.add(user)
        return True

    def __repr__(self):
        return '<User %r>' % self.username


@login_manager.user_loader
def loadUser(user_id):
    # print("loadUser: user_id =", user_id)
    return User.query.filter_by(id=int(user_id)).first()
############################################
#幸运抽奖
class TicketDatabase(db.Model):
    __tablename__ = 'ticketdatabase'
    ticketId=db.Column(db.Integer, primary_key=True, unique=True, index=True)
    ticketUserEmail=db.Column(db.String(64),nullable=True)
    ticketUserSchoolNum=db.Column(db.String(64), nullable=True)
    ticketLuckNum=db.Column(db.Integer,nullable=True)
    ticketCheck=db.Column(db.Integer,nullable=True)

def checkTicketTime():
    timenow=datetime.now()
    timepoint1 = datetime(2020, 2, 29, 21, 37, 0, 0)
    timepoint2 = datetime(2020, 3, 7, 21, 37, 0, 0)
    if timenow <= timepoint1:
        return 1
    elif timenow<=timepoint2:
        return 2
    else:
        return -1

def InserTicket(userEmail,userSchoolNum):
    checkTime=checkTicketTime()
    if checkTime==-1:
        flash('当前无法获取奖券')
        return False
    else:
        myticketNum=TicketDatabase.query.filter_by(ticketUserEmail=userEmail,
                                        ticketUserSchoolNum=userSchoolNum,ticketCheck=checkTime).count()
        if myticketNum>=7:
            flash('您或您的伙伴获取奖券失败，本周获取奖券数量已经达到7张')
            return False
        else:
            newticketId=TicketDatabase.query.count()+1
            newticketRecord=TicketDatabase(ticketId=newticketId,ticketUserEmail=userEmail,ticketCheck=checkTime,
                                           ticketUserSchoolNum=userSchoolNum,ticketLuckNum=random.randint(0,21))
            db.session.add(newticketRecord)
            db.session.commit()
            flash('获得一张奖券，请到我的奖券领取奖券~')
            return True
    return  False

@app.route('/luck', methods=['GET', 'POST'])
@fresh_login_required
def luck():
    nowtime = datetime.now()
    timepoint1 = datetime(2020, 2, 29, 21, 37, 0, 0)
    timepoint2 = datetime(2020, 3, 7, 21, 37, 0, 0)
    flag1 = nowtime <= timepoint1

    if timelimit:
        sign = checkTimeLimit()
        if not sign:
            flash(NOT_START_STRING)
            return redirect(url_for('index'))
    if current_user.userEmail is None:
        return redirect(url_for('append'))
    return render_template('luck.html', nowtime=nowtime, flag1=flag1)

@app.route('/myticket', methods=['GET', 'POST'])
@fresh_login_required
def myticket():
    if timelimit:
        sign = checkTimeLimit()
        if not sign:
            flash(NOT_START_STRING)
            return redirect(url_for('index'))
    if current_user.userEmail is None:
        return redirect(url_for('append'))
    timeweek=checkTicketTime()
    ticketes=TicketDatabase.query.filter_by(ticketUserEmail=current_user.userEmail,ticketUserSchoolNum=current_user.userSchoolNum,
                                            ticketCheck=timeweek).all()

    return render_template('myticket.html',ticketes=ticketes)

@app.route('/faq_ticket', methods=['GET', 'POST'])
@fresh_login_required
def faq_ticket():
    if timelimit:
        sign = checkTimeLimit()
        if not sign:
            flash(NOT_START_STRING)
            return redirect(url_for('index'))
    if current_user.userEmail is None:
        return redirect(url_for('append'))
    return render_template('faq_ticket.html')

#############################################################################
# 假日与你
class bottleDatabase(db.Model):
    __tablename__ = "bottle"
    userBottleId = db.Column(db.Integer, nullable=True)
    userEmail = db.Column(db.String(64), primary_key=True, unique=True, index=True)
    userStatus = db.Column(db.Integer, nullable=True)
    userSchoolNum = db.Column(db.String(64), nullable=True)
    userNickName = db.Column(db.String(64), nullable=True)
    userQQnum = db.Column(db.String(64), nullable=True)
    userTelnum = db.Column(db.String(64), nullable=True)
    userSex = db.Column(db.Integer, nullable=True)

    eventId = db.Column(db.Integer, nullable=True)
    eventName = db.Column(db.String(64), nullable=True)
    userBottleStatus = db.Column(db.Integer, nullable=True)
    # 0未投放 1已投放未匹配 2已投放已匹配
    userSalvageStatus = db.Column(db.Integer, nullable=True)
    # 0无权打捞 1有权打捞
    userBySalvageStatus = db.Column(db.Integer, nullable=True)
    # 0没有选择 1选择同伴但同伴未确认

    partnerEmail = db.Column(db.String(64), nullable=True)
    partnerSchoolNum = db.Column(db.String(64), nullable=True)
    partnerNickName = db.Column(db.String(64), nullable=True)
    partnerQQnum = db.Column(db.String(64), nullable=True)
    partnerTelnum = db.Column(db.String(64), nullable=True)
    partenerEventName = db.Column(db.String(64), nullable=True)
    partenerEventId = db.Column(db.Integer, nullable=True)

    bottleLastTime = db.Column(db.String(64), nullable=True)
    checkPartnerTime = db.Column(db.String(64), nullable=True)
    BePartenerTime = db.Column(db.String(64), nullable=True)


class EventDatabase(db.Model):
    eventId = db.Column(db.Integer, primary_key=True, unique=True, index=True)
    eventName = db.Column(db.String(64), nullable=False)


class dailyEventDatabase(db.Model):
    __tablename__ = "dailyEvent"
    dailyEventId = db.Column(db.Integer, primary_key=True, unique=True, index=True)
    dailyEventUserEmail = db.Column(db.String(64), nullable=True)
    dailyEventUserSchoolNum = db.Column(db.String(64), nullable=True)
    dailyEventUserNickName = db.Column(db.String(64), nullable=True)
    dailyEventName = db.Column(db.String(64), nullable=True)
    dailyTime = db.Column(db.String(64), nullable=True)
    dailyPartnerName = db.Column(db.String(64), nullable=True)

    eventContent = db.Column(db.String(64), nullable=True)
    thumbUpNum = db.Column(db.Integer, nullable=True)


class dailyCheckDatabase(db.Model):
    dailyCheckId = db.Column(db.Integer, primary_key=True, unique=True, index=True)
    dailyUserEmail = db.Column(db.String(64), nullable=True)
    dailyUserSchoolNum = db.Column(db.String(64), nullable=True)
    dailyDateTime = db.Column(db.String(64), nullable=True)


def querydailyCheckDatabase(userEmail, UserSchoolNum):
    today = datetime.now().strftime("%Y-%m-%d")
    userCheckEvent = dailyCheckDatabase.query.filter_by(dailyUserEmail=userEmail, dailyUserSchoolNum=UserSchoolNum,
                                                        dailyDateTime=today).all()
    if userCheckEvent is None:
        return False
    else:
        return True


def AdddailyCheckDatabase(userEmail, UserSchoolNum):
    today = datetime.now().strftime("%Y-%m-%d")
    userCheckEvent = dailyCheckDatabase.query.filter_by(dailyUserEmail=userEmail, dailyUserSchoolNum=UserSchoolNum,
                                                        dailyDateTime=today).all()
    if userCheckEvent is not None:
        return False
    else:
        newId = dailyCheckDatabase.query.count()+1
        today = datetime.now().strftime("%Y-%m-%d")
        newRecord = dailyCheckDatabase(dailyCheckId=newId, dailyUserEmail=userEmail, dailyUserSchoolNum=UserSchoolNum,
                                       dailyDateTime=today)
        db.session.add(newRecord)
        db.session.commit()
        return True


class thumbUpDailyCount(db.Model):
    thumbupDailyId = db.Column(db.Integer, primary_key=True, unique=True, index=True)
    dailyId = db.Column(db.Integer, nullable=True)
    userEmail = db.Column(db.String(64), nullable=True)


class riverStatus():
    riverStatusNum = 0
    riverTime = "2020-02-22 00:00:00.000000"


River = riverStatus()
River.riverTime = "2020-02-22 00:00:00.000000"
LastTimeAtLeast = 24*3600
LastTimeAtLeastCheck=24*3600


## set the LastTimeAtLeast=1 for test
## for reality it is 24*3600( 1 day )

class selectBottleform(FlaskForm):
    ChooseEventId = RadioField("请选择接下来的一周里，我每天要做的一件事", choices=[(i, "%d 号事件" % i) for i in range(1, 5)],
                               validators=[], coerce=int)
    throw = SubmitField("选择事件投放")


class refreshBottleForm(FlaskForm):
    refresh = SubmitField("换一批")


class ThrowBottleCheckform(FlaskForm):
    check = SubmitField("是")


class ThrowBottleCancelform(FlaskForm):
    cancel = SubmitField("取消")


def chooseEvent():
    EventChoose = EventDatabase.query.order_by(func.random()).limit(10)
    setattr(selectBottleform, 'ChooseEventId',
            RadioField("请选择接下来的一周里，我每天要做的一件事", choices=[(event.eventId, event.eventName) for event in EventChoose],
                       validators=[], coerce=int))
    return EventChoose


def checkRiverStatus():
    lasttime = datetime.strptime(str(River.riverTime), "%Y-%m-%d %H:%M:%S.%f")
    nowtime = datetime.now()
    bottleboyNum = bottleDatabase.query.filter_by(userBottleStatus=1, userSex=1).count()
    bottlegirlNum = bottleDatabase.query.filter_by(userBottleStatus=1, userSex=0).count()

    if (bottleboyNum<5 or bottlegirlNum<5 or (bottlegirlNum+bottleboyNum)<10) and (nowtime-lasttime).total_seconds()>=0:
        #进入节水期
        River.riverTime=str(nowtime+timedelta(days=1))
        River.riverStatusNum=0

    lasttime = datetime.strptime(str(River.riverTime), "%Y-%m-%d %H:%M:%S.%f")
    if (nowtime - lasttime).total_seconds() >= 0:
        River.riverStatusNum = 1
        return 1, 0
    return 0, (lasttime - nowtime).total_seconds() // 3600


class chooseCompareForm(FlaskForm):
    chooseCompare = RadioField("我要选择和同伴一起完成的事件：", choices=[(i, "%d 号漂流瓶" % i) for i in range(1, 6)],
                               validators=[], coerce=int)
    chooseBottle = SubmitField("选择漂流瓶")


class chooseRefreshForm(FlaskForm):
    refresh2 = SubmitField("换一批")




class CheckPartnerform(FlaskForm):
    continueCheck = SubmitField("选择续约")


class ReceiveInviteForm(FlaskForm):
    choosePartener = RadioField("我要选择以上几号同伴：", choices=[(i, "%d 号同伴" % i) for i in range(1, 6)], validators=[],
                                coerce=int)
    choosePartner = SubmitField('选择同伴')


class ThumbUpFormDaily(FlaskForm):
    thumbup = SubmitField('点赞')


class DailyUpForm(FlaskForm):
    dailyText = TextAreaField("打卡内容 ", validators=[DataRequired()])
    submit = SubmitField("打卡")


@app.route('/shareUp', methods=['GET', 'POST'])
@fresh_login_required
def shareUp():
    myBottle = bottleDatabase.query.filter_by(userEmail=current_user.userEmail,
                                              userSchoolNum=current_user.userSchoolNum).first()
    if myBottle is None:
        newbottleIdNum = bottleDatabase.query.count()
        myBottle = bottleDatabase(userEmail=current_user.userEmail, userStatus=current_user.userStatus,
                                  userSchoolNum=current_user.userSchoolNum, userNickName=current_user.userNickName,
                                  userQQnum=current_user.userQQnum, userTelnum=current_user.userTelnum,
                                  userSex=current_user.userSex,
                                  userBottleStatus=0, userSalvageStatus=0, userBySalvageStatus=0,
                                  bottleLastTime="2020-01-01 00:00:00.000000",
                                  checkPartnerTime="2020-01-01 00:00:00.000000",
                                  BePartenerTime="2020-01-01 00:00:00.000000",
                                  userBottleId=newbottleIdNum)
        db.session.add(myBottle)
        db.session.commit()
        return redirect(url_for('ThrowBottle'))
    check = myBottle.userBottleStatus
    dailyEvents = dailyEventDatabase.query.order_by(func.random()).limit(5)
    checkdailyEvents = dailyEvents.first()
    dailyCheck = 1
    if checkdailyEvents is None:
        dailyCheck = 0
    dailyUpForm=DailyUpForm()
    thumbUpWorkId = request.args.get('workid', '')

    if thumbUpWorkId:
        myBottle = bottleDatabase.query.filter_by(userEmail=current_user.userEmail,
                                                  userSchoolNum=current_user.userSchoolNum).first()
        thumbUpRecord = thumbUpDailyCount.query.filter_by(dailyId=thumbUpWorkId,
                                                          userEmail=myBottle.userEmail).first()
        if thumbUpRecord is None:
            thumbID = thumbUpDailyCount.query.count() + 1
            thumbUpRecords = thumbUpDailyCount(thumbupDailyId=thumbID, dailyId=thumbUpWorkId,
                                               userEmail=myBottle.userEmail)
            ChooseWish = dailyEventDatabase.query.filter_by(dailyEventId=thumbUpWorkId).first()
            ChooseWish.thumbUpNum = ChooseWish.thumbUpNum + 1
            db.session.add(ChooseWish)
            db.session.add(thumbUpRecords)
            db.session.commit()
            return '点赞成功'
        else:
            return '无法点赞，可能您已经为该愿望点赞了，或者存在其他系统故障'
        # checkdailyEvents.thumbUpNum=checkdailyEvents+1

    if  dailyUpForm.submit.data:
        dailyEventNum = dailyEventDatabase.query.count() + 1
        newRecord = dailyEventDatabase(dailyEventId=dailyEventNum, dailyEventName=myBottle.eventName,
                                       dailyEventUserEmail=myBottle.userEmail,
                                       dailyEventUserSchoolNum=myBottle.userSchoolNum,
                                       dailyEventUserNickName=myBottle.userNickName, dailyTime=str(datetime.now()),
                                       dailyPartnerName=myBottle.partnerNickName,
                                       eventContent=dailyUpForm.dailyText.data, thumbUpNum=0)
        db.session.add(newRecord)
        db.session.commit()
        flash('打卡成功')
        if AdddailyCheckDatabase(myBottle.userEmail, myBottle.userSchoolNum) and querydailyCheckDatabase(myBottle.partnerEmail, myBottle.partnerSchoolNum):
            InserTicket(myBottle.userEmail, myBottle.userSchoolNum)
            InserTicket(myBottle.partnerEmail, myBottle.partnerSchoolNum)
            flash('您和您的同伴获得了一张奖券')
        return redirect(url_for('shareUp'))

    return render_template('holiday/shareUp.html', check=check, dailyEvents=dailyEvents
                           , dailyUpForm=dailyUpForm, dailyCheck=dailyCheck)


@app.route('/attendance', methods=['GET', 'POST'])
@fresh_login_required
def attendance():
    myBottle = bottleDatabase.query.filter_by(userEmail=current_user.userEmail,
                                              userSchoolNum=current_user.userSchoolNum).first()
    if myBottle is None:
        newbottleIdNum = bottleDatabase.query.count()
        myBottle = bottleDatabase(userEmail=current_user.userEmail, userStatus=current_user.userStatus,
                                  userSchoolNum=current_user.userSchoolNum, userNickName=current_user.userNickName,
                                  userQQnum=current_user.userQQnum, userTelnum=current_user.userTelnum,
                                  userSex=current_user.userSex,
                                  userBottleStatus=0, userSalvageStatus=0, userBySalvageStatus=0,
                                  bottleLastTime="2020-01-01 00:00:00.000000",
                                  checkPartnerTime="2020-01-01 00:00:00.000000",
                                  BePartenerTime="2020-01-01 00:00:00.000000",
                                  userBottleId=newbottleIdNum)
        db.session.add(myBottle)
        db.session.commit()
        return redirect(url_for('attendance'))

    myRecord = dailyEventDatabase.query.filter_by(dailyEventUserEmail=myBottle.userEmail,
                                                  dailyEventUserSchoolNum=myBottle.userSchoolNum).all()
    mypartnerRecord = dailyEventDatabase.query.filter_by(dailyEventUserEmail=myBottle.partnerEmail,
                                                         dailyEventUserSchoolNum=myBottle.partnerSchoolNum).all()
    myRecordCheck = dailyEventDatabase.query.filter_by(dailyEventUserEmail=myBottle.userEmail,
                                                       dailyEventUserSchoolNum=myBottle.userSchoolNum).count()
    mypartnerRecordCheck = dailyEventDatabase.query.filter_by(dailyEventUserEmail=myBottle.partnerEmail,
                                                              dailyEventUserSchoolNum=myBottle.partnerSchoolNum).count()
    return render_template('holiday/attendance.html', myRecord=myRecord, mypartnerRecord=mypartnerRecord,
                           myRecordCheck=myRecordCheck, mypartnerRecordCheck=mypartnerRecordCheck)


@app.route('/ThrowBottle', methods=['GET', 'POST'])
@fresh_login_required
def ThrowBottle():
    if timelimit == 1 and not checkTimeLimit():
        flash(NOT_START_STRING)
        return redirect(url_for('index'))
    myBottle = bottleDatabase.query.filter_by(userEmail=current_user.userEmail,
                                              userSchoolNum=current_user.userSchoolNum).first()
    if myBottle is None:
        newbottleIdNum = bottleDatabase.query.count()
        myBottle = bottleDatabase(userEmail=current_user.userEmail, userStatus=current_user.userStatus,
                                  userSchoolNum=current_user.userSchoolNum, userNickName=current_user.userNickName,
                                  userQQnum=current_user.userQQnum, userTelnum=current_user.userTelnum,
                                  userSex=current_user.userSex,
                                  userBottleStatus=0, userSalvageStatus=0, userBySalvageStatus=0,
                                  bottleLastTime="2020-01-01 00:00:00.000000",
                                  checkPartnerTime="2020-01-01 00:00:00.000000",
                                  BePartenerTime="2020-01-01 00:00:00.000000",
                                  userBottleId=newbottleIdNum)
        db.session.add(myBottle)
        db.session.commit()
        return redirect(url_for('ThrowBottle'))
    chooseEvent()
    selectForms = selectBottleform()
    refreshBottleform = refreshBottleForm()
    nowTime = datetime.now()
    if myBottle.userBottleStatus == 2:
        lastTime = datetime.strptime(str(myBottle.BePartenerTime), "%Y-%m-%d %H:%M:%S.%f")
        if (nowTime - lastTime).total_seconds() >= 5 * LastTimeAtLeast:
            myBottle.userBottleStatus = 0
            db.session.commit()
            return redirect(url_for('ThrowBottle'))

    # 提交选择
    if  selectForms.throw.data:
        myBottle = bottleDatabase.query.filter_by(userEmail=current_user.userEmail,
                                                  userSchoolNum=current_user.userSchoolNum).first()

        lastTime = datetime.strptime(str(myBottle.bottleLastTime), "%Y-%m-%d %H:%M:%S.%f")
        if (nowTime - lastTime).total_seconds() <= 20:
            flash('您的提交太频繁了，至少请经过20s再重新投放瓶子')
            return redirect(url_for('ThrowBottle'))

        if myBottle.userBottleStatus == 0:
            myBottle.userBottleStatus = 1
            myBottle.eventId = selectForms.ChooseEventId.data
            myBottle.eventName = EventDatabase.query.filter_by(eventId=myBottle.eventId).first().eventName
            myBottle.bottleLastTime = str(datetime.now())
            db.session.commit()
            flash("事件瓶已成功投放到事件河流中，"
                  "漂流事件开始计时！待ta拾取后，系统将发送确认匹配消息至“我的消息”页面中，"
                  "请记得查收噢~该确认匹配消息有效期仅有一天，超过一天则默认同意匹配，"
                  "双方进入匹配状态中~事件瓶在河流中漂流至24h即可获得捞瓶资格，可前往事件河流拾取事件瓶~")
            return redirect(url_for('ThrowBottle'))

        if myBottle.userBottleStatus == 1:
            checkEvent = selectForms.ChooseEventId.data
            return redirect(url_for('ThrowBottleCheck', checkEvent=checkEvent))
        if myBottle.userBottleStatus == 2:
            flash('你已经处于匹配中,如果已经解除关系建议刷新页面后重试，不可以再投放事件瓶咯')
            return redirect(url_for('ThrowBottle'))

    # 换一批
    if refreshBottleform.refresh.data and refreshBottleform.validate_on_submit():
        chooseEvent()
        flash("换一批成功")
        return redirect(url_for('ThrowBottle'))

    return render_template('holiday/ThrowBottle.html', selectBottleform=selectForms, myBottle=myBottle,
                           refreshBottleform=refreshBottleform)


@app.route('/ThrowBottleCheck/?<int:checkEvent>', methods=['GET', 'POST'])
@fresh_login_required
def ThrowBottleCheck(checkEvent):
    checkform = ThrowBottleCheckform()
    cancelform = ThrowBottleCancelform()
    myBottle = bottleDatabase.query.filter_by(userEmail=current_user.userEmail,
                                              userSchoolNum=current_user.userSchoolNum).first()
    if checkform.check.data :
        myBottle.userBottleStatus = 1
        myBottle.userSalvageStatus = 0
        myBottle.eventId = checkEvent
        myBottle.eventName = EventDatabase.query.filter_by(eventId=myBottle.eventId).first().eventName
        myBottle.bottleLastTime = str(datetime.now())
        db.session.commit()
        flash("事件瓶已成功投放到事件河流中，"
              "漂流事件开始计时！待ta拾取后，系统将发送确认匹配消息至“我的消息”页面中，"
              "请记得查收噢~该确认匹配消息有效期仅有一天，超过一天则默认同意匹配，"
              "双方进入匹配状态中~事件瓶在河流中漂流至24h即可获得捞瓶资格，可前往事件河流拾取事件瓶~”")
        return redirect(url_for('ThrowBottle'))
    if cancelform.cancel.data :
        flash('您已经取消事件瓶的投放')
        return redirect(url_for('ThrowBottle'))
    return render_template('holiday/ThrowBottleCheck.html', checkform=checkform, cancelform=cancelform)


@app.route('/BottleRiverPick', methods=['GET', 'POST'])
@fresh_login_required
def BottleRiverPick():
    timenow = datetime.now()
    myBottle = bottleDatabase.query.filter_by(userEmail=current_user.userEmail,
                                              userSchoolNum=current_user.userSchoolNum).first()
    if myBottle is None:
        newbottleIdNum = bottleDatabase.query.count()
        myBottle = bottleDatabase(userEmail=current_user.userEmail, userStatus=current_user.userStatus,
                                  userSchoolNum=current_user.userSchoolNum, userNickName=current_user.userNickName,
                                  userQQnum=current_user.userQQnum, userTelnum=current_user.userTelnum,
                                  userSex=current_user.userSex,
                                  userBottleStatus=0, userSalvageStatus=0, userBySalvageStatus=0,
                                  bottleLastTime="2020-01-01 00:00:00.000000",
                                  checkPartnerTime="2020-01-01 00:00:00.000000",
                                  BePartenerTime="2020-01-01 00:00:00.000000",
                                  userBottleId=newbottleIdNum)
        db.session.add(myBottle)
        db.session.commit()
        return redirect(url_for('ThrowBottle'))
    lasttime = datetime.strptime(str(myBottle.bottleLastTime), "%Y-%m-%d %H:%M:%S.%f")
    if (timenow - lasttime).total_seconds() >= LastTimeAtLeastCheck and myBottle.userBottleStatus == 1 and myBottle.userSalvageStatus != 1:
        myBottle.userSalvageStatus = 1
        db.session.commit()
        return redirect(url_for('BottleRiverPick'))
    riverStatus, LeftTime = checkRiverStatus()
    chooseCompare = chooseCompareForm()
    chooseRefresh = chooseRefreshForm()
    chooseBottles = bottleDatabase.query.filter(not_(bottleDatabase.userSex == myBottle.userSex),
                                                bottleDatabase.userBottleStatus == 1).order_by(func.random()).limit(5)
    if chooseBottles is None:
        flash('暂时没有足够的异性的瓶子，可能系统正在计算，河流即将节水期，请刷新页面后重试')
        return redirect(url_for('BottleRiverPick'))
    setattr(chooseCompare, 'chooseCompare',
            RadioField("我要选择和同伴一起完成的事件", choices=[(event.userBottleId, event.eventName+'   '+event.usernickname) for event in chooseBottles],
                       validators=[], coerce=int))
    if chooseCompare.validate_on_submit() and chooseCompare.chooseBottle.data:
        if myBottle.userSalvageStatus == 0:
            flash('你暂时还没有打捞资格,或者你选取的对象还没有回应')
            return redirect(url_for('BottleRiverPick'))
        else:
            if myBottle.userBottleStatus == 2:
                myBottle.userSalvageStatus = 0
                myBottle.userBySalvageStatus = 0
                db.session.commit()
                flash('你有同伴一同打卡，或者原来同伴关系没解除，如果原有同伴已经过期，建议到我的消息里面解除同伴再来打卡')
                return redirect(url_for('BottleRiverPick'))
            bottleNum = chooseCompare.chooseCompare.data
            partnerBottle = bottleDatabase.query.filter_by(userBottleId=bottleNum).first()
            if partnerBottle.userBottleStatus == 2:
                flash('非常抱歉，你选取的漂流瓶的主人已经和别人达成了同伴关系，你可以重新刷新页面选取漂流瓶')
                return redirect(url_for('BottleRiverPick'))
            ##可以成功选取作为匹配潜在对象
            myBottle.checkPartnerTime = datetime.now()
            myBottle.userSalvageStatus = 0
            myBottle.partnerEmail = partnerBottle.userEmail
            myBottle.partnerSchoolNum = partnerBottle.userSchoolNum
            myBottle.partnerNickName = partnerBottle.userNickName
            myBottle.partnerQQnum = partnerBottle.userQQnum
            myBottle.partnerTelnum = partnerBottle.userTelnum
            myBottle.partenerEventName = partnerBottle.eventName
            myBottle.partnerEventId = partnerBottle.eventId
            myBottle.userBySalvageStatus = 1
            db.session.commit()
            flash('你的请求已经发送给对方')
            return redirect(url_for('BottleRiverPick'))
    if  chooseRefresh.refresh2.data:
        chooseBottles = bottleDatabase.query.filter(not_(bottleDatabase.userSex == myBottle.userSex),
                                                    bottleDatabase.userBottleStatus == 1).order_by(
            func.random()).limit(5)
        if chooseBottles is None:
            flash('暂时没有足够的异性的瓶子，可能系统正在计算，河流即将节水期，请刷新页面后重试')
            return redirect(url_for('BottleRiverPick'))
        setattr(chooseCompare, 'chooseCompare',
                RadioField("我要选择和同伴一起完成的事件", choices=[(event.userBottleId, event.eventName) for event in chooseBottles],
                           validators=[], coerce=int))
        flash('更换成功')
        return redirect(url_for('BottleRiverPick'))

    return render_template('holiday/BottleRiverPick.html', myBottle=myBottle, riverStatus=riverStatus,
                           LeftTime=LeftTime, Bottles=chooseBottles, chooseCompare=chooseCompare,
                           chooseRefresh=chooseRefresh)


@app.route('/bottleMessage', methods=['GET', 'POST'])
@fresh_login_required
def bottleMessage():
    timenow = datetime.now()
    myBottle = bottleDatabase.query.filter_by(userEmail=current_user.userEmail,
                                              userSchoolNum=current_user.userSchoolNum).first()
    if myBottle is None:
        newbottleIdNum = bottleDatabase.query.count()
        myBottle = bottleDatabase(userEmail=current_user.userEmail, userStatus=current_user.userStatus,
                                  userSchoolNum=current_user.userSchoolNum, userNickName=current_user.userNickName,
                                  userQQnum=current_user.userQQnum, userTelnum=current_user.userTelnum,
                                  userSex=current_user.userSex,
                                  userBottleStatus=0, userSalvageStatus=0, userBySalvageStatus=0,
                                  bottleLastTime="2020-01-01 00:00:00.000000",
                                  checkPartnerTime="2020-01-01 00:00:00.000000",
                                  BePartenerTime="2020-01-01 00:00:00.000000",
                                  userBottleId=newbottleIdNum)
        db.session.add(myBottle)
        db.session.commit()
        return redirect(url_for('bottleMessage'))
    riverStatus, LeftTime = checkRiverStatus()
    myReceiveInvite = bottleDatabase.query.filter(not_(bottleDatabase.userBottleStatus == 2),
                                                  bottleDatabase.partnerEmail == current_user.userEmail,
                                                  bottleDatabase.partnerSchoolNum == current_user.userSchoolNum,
                                                  bottleDatabase.userBySalvageStatus == 1)
    myReceiveInviteNum = myReceiveInvite.count()
    checkpartnerform = CheckPartnerform()
    receiveInviteform = ReceiveInviteForm()

    # 超过7天后登陆直接解除同伴关系
    if myBottle.userBottleStatus == 2:
        lasttime = datetime.strptime(str(myBottle.BePartenerTime), "%Y-%m-%d %H:%M:%S.%f")
        timenow = datetime.now()
        if (timenow - lasttime).total_seconds() >= 5 * LastTimeAtLeast:
            partnerBottle = bottleDatabase.query.filter_by(userEmail=myBottle.partnerEmail,
                                                           userSchoolNum=myBottle.partnerSchoolNum).first()
            if partnerBottle is None:
                myBottle.userBottleStatus = 0
                myBottle.userSalvageStatus = 0
                userBySalvageStatus = 0
                db.session.commit()
                flash('因为你没有及时续约，你的同伴已经取消，请返回愿望池重新投瓶，')
                return redirect(url_for('bottleMessage'))
            else:
                myBottle.userBottleStatus = 0
                myBottle.userSalvageStatus = 0
                myBottle.userBySalvageStatus = 0
                partnerBottle.userBottleStatus = 0
                partnerBottle.userSavageStatus = 0
                partnerBottle.userBySalvageStatus = 0
                db.session.commit()
                flash('因为你没有及时续约，你的同伴已经被系统取消，请返回愿望池重新投瓶，')
                return redirect(url_for('bottleMessage'))
    # 发出邀请一天后直接成功同伴关系
    '''
    if myBottle.userBySalvageStatus == 1 and myBottle.userBottleStatus == 1:
        nowtime = datetime.now()
        lasttime = datetime.strptime(str(myBottle.checkPartnerTime), "%Y-%m-%d %H:%M:%S.%f")
        if (nowtime - lasttime).total_seconds() >= LastTimeAtLeast:
            partnerBottle = bottleDatabase.query.filter_by(userEmail=myBottle.partnerEmail,
                                                           userSchoolNum=myBottle.partnerSchoolNum).first()
            if partnerBottle is None:
                flash('系统存在故障，请联系项目组')
                return redirect(url_for('bottleMessage'))
            if partnerBottle.userBottleStatus == 2:
                myBottle.userBottleStatus = 1
                myBottle.userBySalvageStatus = 0
                myBottle.userSalvageStatus = 1
                db.session.commit()
                flash('对方已经接受了别人的邀请，你可以回到事件河流重新领取事件瓶')
                return redirect(url_for('bottleMessage'))
            else:
                myBottle.userBottleStatus = 2
                myBottle.userSalvageStatus = 0
                myBottle.userBySalvageStatus = 0
                partnerBottle.userBySalvageStatus = 0
                partnerBottle.userBottleStatus = 2
                partnerBottle.userSavageStatus = 0
                partnerBottle.partnerEmail = myBottle.userEmail
                partnerBottle.partnerSchoolNum = myBottle.userSchoolNum
                partnerBottle.partnerQQnum = myBottle.userQQnum
                partnerBottle.partnerTelnum = myBottle.userTelnum
                partnerBottle.partnerNickName = myBottle.userNickName
                db.session.commit()
                flash('你们已经成为了同伴，可以一起打卡咯！！')
                return redirect(url_for('bottleMessage'))
    '''
    # 续约按钮功能
    if checkpartnerform.validate_on_submit() and checkpartnerform.continueCheck.data:
        if myBottle.userBottleStatus != 2:
            flash('请确认自己有同伴否则无法确认续约')
            return redirect(url_for('bottleMessage'))
        else:
            if myBottle.userBySalvageStatus == 1:
                flash('你已经同意续约，请等待对方同意')
                return redirect(url_for('bottleMessage'))
            else:
                partnerBottle = bottleDatabase.query.filter_by(userEmail=myBottle.partnerEmail,
                                                               userSchoolNum=myBottle.partnerSchoolNum).first()
                if partnerBottle is None:
                    flash('匹配情况出现问题，系统出现故障，请直接咨询项目组。')
                    return redirect(url_for('bottleMessage'))
                if partnerBottle.partnerEmail == myBottle.userEmail and partnerBottle.partnerSchoolNum == myBottle.userSchoolNum:
                    if partnerBottle.userBySalvageStatus == 1:
                        timenow = datetime.now()
                        partnerBottle.BePartenerTime = str(timenow)
                        partnerBottle.userBottleStatus = 2
                        partnerBottle.userBySalvageStatus = 0
                        myBottle.BePartenerTime = str(timenow)
                        myBottle.userBottleStatus = 2
                        myBottle.userBySalvageStatus = 0
                        db.session.commit()
                        flash('续约成功')
                        return redirect(url_for('bottleMessage'))
                    if partnerBottle.userBySalvageStatus == 0:
                        myBottle.userBySalvageStatus = 1
                        db.session.commit()
                        flash('你已经发出续约请求')
                        return redirect(url_for('bottleMessage'))
                else:
                    flash('匹配情况出现问题，系统出现故障，请直接咨询项目组。')
                    return redirect(url_for('bottleMessage'))
    # 接受邀请按钮功能
    setattr(receiveInviteform, 'choosePartener',
            RadioField("我要选择同伴的昵称是：",
                       choices=[(invite.userBottleId, invite.userNickName) for invite in myReceiveInvite],
                       validators=[], coerce=int))
    if receiveInviteform.validate_on_submit() and receiveInviteform.choosePartner.data:
        chooseNum = receiveInviteform.choosePartener.data
        AcceptPartner = bottleDatabase.query.filter_by(userBottleId=chooseNum).first()
        if myBottle.userBottleStatus==2:
            flash('你已经匹配')
            return redirect(url_for('bottleMessage'))
        if AcceptPartner is None:
            flash('系统存在故障，请联系项目组')
            return redirect(url_for('bottleMessage'))
        if AcceptPartner.userBottleStatus == 2:
            flash('对方已经和别人成为同伴，请刷新页面重试')
            return redirect(url_for('bottleMessage'))
        else:
            timenow = datetime.now()
            myBottle.BePartenerTime = str(timenow)
            myBottle.userBottleStatus=2
            myBottle.userSalvageStatus=0
            myBottle.userBySalvageStatus=0
            myBottle.partnerSchoolNum = AcceptPartner.userSchoolNum
            myBottle.partnerEmail = AcceptPartner.userEmail
            myBottle.partnerNickName = AcceptPartner.userNickName
            myBottle.partnerTelnum = AcceptPartner.userTelnum
            myBottle.partnerQQnum = AcceptPartner.userQQnum
            myBottle.partnerEventId = AcceptPartner.eventId
            myBottle.partenerEventName = AcceptPartner.eventName
            AcceptPartner.BePartenerTime=str(timenow)
            AcceptPartner.userBySalvageStatus=0
            AcceptPartner.userBottleStatus=2
            AcceptPartner.userSavageStatus=0
            AcceptPartner.partnerEmail=myBottle.userEmail
            AcceptPartner.partnerSchoolNum=myBottle.userSchoolNum
            AcceptPartner.partnerQQnum=myBottle.userQQnum
            AcceptPartner.partnerTelnum=myBottle.userTelnum
            AcceptPartner.partnerNickName=myBottle.userNickName
            AcceptPartner.partnerEventId=myBottle.eventId
            AcceptPartner.partenerEventName=myBottle.eventName
            db.session.commit()
            flash('你们已经成为了同伴，可以一起打卡咯！！')
            return redirect(url_for('bottleMessage'))

    return render_template('holiday/bottleMessage.html', myBottle=myBottle, riverStatus=riverStatus,
                           LeftTime=LeftTime, myReceiveInvite=myReceiveInvite, myReceiveInviteNum=myReceiveInviteNum,
                        checkpartnerform=checkpartnerform, receiveInviteform=receiveInviteform)





@app.route('/BottleFaq', methods=['GET', 'POST'])
@fresh_login_required
def BottleFaq():
    return render_template("holiday/BottleFaq.html")


@app.route('/holiday', methods=['GET', 'POST'])
@fresh_login_required
def holiday():
    if timelimit:
        sign = checkTimeLimit()
        if not sign:
            flash(NOT_START_STRING)
            return redirect(url_for('index'))
    if current_user.userEmail is None:
        return redirect(url_for('append'))
    riverStatus, LeftTime = checkRiverStatus()
    return render_template('holiday/holiday.html', riverStatus=riverStatus, LeftTime=LeftTime,
                           userStatus=current_user.userStatus)
######################################################################################################################
#镜像show模块

class workDatabase(db.Model):
    __tablename__ = "work"
    workid = db.Column(db.Integer, primary_key=True, nullable=True)
    workgroup = db.Column(db.String(64), nullable=True)

    userEmail = db.Column(db.String(64), nullable=True)
    userStatus = db.Column(db.Integer, nullable=True)
    userNickName = db.Column(db.String(64), nullable=True)
    
    worktitle = db.Column(db.String(64), nullable=True)
    workContent = db.Column(db.String(1000), nullable=True)
    workImgPath = db.Column(db.String(64), nullable=True)

    thumbNum = db.Column(db.Integer, nullable=True, default=0)
    thumbNumDaily = db.Column(db.Integer, nullable=True, default=0)
    thumbNumWeekly = db.Column(db.Integer, nullable=True, default=0)



@app.route('/show', methods=['GET', 'POST'])
@fresh_login_required
def show():
    if timelimit:
        sign = checkTimeLimit()
        if not sign:
            flash(NOT_START_STRING)
            return redirect(url_for('index'))
    if current_user.userEmail is None:
        return redirect(url_for('append'))
    return render_template('show.html')


class thumbWork(db.Model):
    __tablename__ = "thumbWork"
    thumbId = db.Column(db.Integer, primary_key=True, unique=True, index=True)
    workid= db.Column(db.String(64))
    thumbUpEmail = db.Column(db.String(64))
    thumbTime = db.Column(db.String(64))

@app.route('/wonderland', methods=['GET', 'POST'])
def wonderland():
    choice=request.args.get('choice', '')
    workgroup='wonderland'
    if not choice:
        choice='最热作品'
    
    if choice=='每日新秀':
        works = workDatabase.query.filter(workDatabase.workgroup == workgroup).order_by(
            workDatabase.thumbNumDaily.desc()).limit(10)
    elif choice =='每周榜单':
        works = workDatabase.query.filter(workDatabase.workgroup == workgroup).order_by(
            workDatabase.thumbNumWeekly.desc()).limit(10)
    elif choice == '随机推送':
        works = workDatabase.query.filter(workDatabase.workgroup == workgroup).order_by(
            func.random()).limit(10)
    else:       #'最热作品'
        works = workDatabase.query.filter(workDatabase.workgroup == workgroup).order_by(
            workDatabase.thumbNum.desc()).limit(10)

    #响应点赞
    thumbUpWorkId = request.args.get('workid', '')
    if thumbUpWorkId:
        thumbUpRecord = thumbWork.query.filter_by(workid=thumbUpWorkId,
                                                  thumbUpEmail=current_user.userEmail).first()
        if thumbUpRecord is None:
            thumbID = thumbWork.query.count() + 1
            thumbUpRecords = thumbWork(thumbId=thumbID, workid=thumbUpWorkId,
                                       thumbUpEmail=current_user.userEmail,
                                       thumbTime=str(datetime.now()))
            ChooseWork = workDatabase.query.filter_by(workid=thumbUpWorkId).first()

            ChooseWork.thumbNum = thumbWork.query.filter_by(workid=thumbUpWorkId).count()+1
            def istoday(t):
                 #当天
                 time=datetime.strptime(str(t), "%Y-%m-%d %H:%M:%S.%f")
                 now=datetime.now()
                 return (now-time).days==0

            def isThisWeek(t):
                 #本周
                 time=datetime.strptime(str(t), "%Y-%m-%d %H:%M:%S.%f")
                 now=datetime.now()
                 return (now-time).days<=5

            ChooseWork.thumbNumDaily = thumbWork.query.filter_by(workid=thumbUpWorkId).count()+1
            ChooseWork.thumbNumWeekly = thumbWork.query.filter_by(workid=thumbUpWorkId).count()+1

            db.session.add(ChooseWork)
            db.session.add(thumbUpRecords)
            db.session.commit()
            return "点赞成功"
        else:
            return "无法点赞，可能您已经为该愿望点赞了，或者存在其他系统故障"

    if works.count() == 0:
        flash("还没有作品")

    return render_template('wonderland.html',choice=choice,works=works)

@app.route('/party', methods=['GET', 'POST'])
def party():
    choice=request.args.get('choice', '')
    workgroup='party'
    if not choice:
        choice='最热作品'
    
    if choice=='每日新秀':
        works = workDatabase.query.filter(workDatabase.workgroup == workgroup).order_by(
            workDatabase.thumbNumDaily.desc()).limit(10)
    elif choice =='每周榜单':
        works = workDatabase.query.filter(workDatabase.workgroup == workgroup).order_by(
            workDatabase.thumbNumWeekly.desc()).limit(10)
    elif choice == '随机推送':
        works = workDatabase.query.filter(workDatabase.workgroup == workgroup).order_by(
            func.random()).limit(10)
    else:       #'最热作品'
        works = workDatabase.query.filter(workDatabase.workgroup == workgroup).order_by(
            workDatabase.thumbNum.desc()).limit(10)

    #响应点赞
    thumbUpWorkId = request.args.get('workid', '')
    if thumbUpWorkId:
        thumbUpRecord = thumbWork.query.filter_by(workid=thumbUpWorkId,
                                                  thumbUpEmail=current_user.userEmail).first()
        if thumbUpRecord is None:
            thumbID = thumbWork.query.count() + 1
            thumbUpRecords = thumbWork(thumbId=thumbID, workid=thumbUpWorkId,
                                       thumbUpEmail=current_user.userEmail,
                                       thumbTime=str(datetime.now()))
            ChooseWork = workDatabase.query.filter_by(workid=thumbUpWorkId).first()

            ChooseWork.thumbNum = thumbWork.query.filter_by(workid=thumbUpWorkId).count()+1
            def istoday(t):
                #当天
                time=datetime.strptime(str(t), "%Y-%m-%d %H:%M:%S.%f")
                now=datetime.now()
                return (now-time).days==0

            def isThisWeek(t):
                #本周
                time=datetime.strptime(str(t), "%Y-%m-%d %H:%M:%S.%f")
                now=datetime.now()
                return (now-time).days<=5

            ChooseWork.thumbNumDaily = thumbWork.query.filter(thumbWork.workid == thumbUpWorkId, istoday(thumbWork.thumbTime)).count()+1
            ChooseWork.thumbNumWeekly = thumbWork.query.filter(thumbWork.workid == thumbUpWorkId, isThisWeek(thumbWork.thumbTime)).count()+1

            db.session.add(ChooseWork)
            db.session.add(thumbUpRecords)
            db.session.commit()
            return "点赞成功"
        else:
            return "无法点赞，可能您已经为该愿望点赞了，或者存在其他系统故障"

    if works.count() == 0:
        flash("还没有作品")

    return render_template('party.html',choice=choice,works=works)

@app.route('/kitchen', methods=['GET', 'POST'])
def kitchen():
    choice=request.args.get('choice', '')
    workgroup='kitchen'
    if not choice:
        choice='最热作品'
    
    if choice=='每日新秀':
        works = workDatabase.query.filter(workDatabase.workgroup == workgroup).order_by(
            workDatabase.thumbNumDaily.desc()).limit(10)
    elif choice =='每周榜单':
        works = workDatabase.query.filter(workDatabase.workgroup == workgroup).order_by(
            workDatabase.thumbNumWeekly.desc()).limit(10)
    elif choice == '随机推送':
        works = workDatabase.query.filter(workDatabase.workgroup == workgroup).order_by(
            func.random()).limit(10)
    else:       #'最热作品'
        works = workDatabase.query.filter(workDatabase.workgroup == workgroup).order_by(
            workDatabase.thumbNum.desc()).limit(10)

    #响应点赞
    thumbUpWorkId = request.args.get('workid', '')
    if thumbUpWorkId:
        thumbUpRecord = thumbWork.query.filter_by(workid=thumbUpWorkId,
                                                  thumbUpEmail=current_user.userEmail).first()
        if thumbUpRecord is None:
            thumbID = thumbWork.query.count() + 1
            thumbUpRecords = thumbWork(thumbId=thumbID, workid=thumbUpWorkId,
                                       thumbUpEmail=current_user.userEmail,
                                       thumbTime=str(datetime.now()))
            ChooseWork = workDatabase.query.filter_by(workid=thumbUpWorkId).first()

            ChooseWork.thumbNum = thumbWork.query.filter_by(workid=thumbUpWorkId).count()+1
            def istoday(t):
                #当天
                time=datetime.strptime(str(t), "%Y-%m-%d %H:%M:%S.%f")
                now=datetime.now()
                return (now-time).days==0

            def isThisWeek(t):
                #本周
                time=datetime.strptime(str(t), "%Y-%m-%d %H:%M:%S.%f")
                now=datetime.now()
                return (now-time).days<=5

            ChooseWork.thumbNumDaily = thumbWork.query.filter(thumbWork.workid == thumbUpWorkId, istoday(thumbWork.thumbTime)).count()+1
            ChooseWork.thumbNumWeekly = thumbWork.query.filter(thumbWork.workid == thumbUpWorkId, isThisWeek(thumbWork.thumbTime)).count()+1

            db.session.add(ChooseWork)
            db.session.add(thumbUpRecords)
            db.session.commit()
            return "点赞成功"
        else:
            return "无法点赞，可能您已经为该愿望点赞了，或者存在其他系统故障"

    if works.count() == 0:
        flash("还没有作品")

    return render_template('kitchen.html',choice=choice,works=works)

@app.route('/battle', methods=['GET', 'POST'])
def battle():
    choice=request.args.get('choice', '')
    workgroup='battle'
    if not choice:
        choice='最热作品'
    
    if choice=='每日新秀':
        works = workDatabase.query.filter(workDatabase.workgroup == workgroup).order_by(
            workDatabase.thumbNumDaily.desc()).limit(10)
    elif choice =='每周榜单':
        works = workDatabase.query.filter(workDatabase.workgroup == workgroup).order_by(
            workDatabase.thumbNumWeekly.desc()).limit(10)
    elif choice == '随机推送':
        works = workDatabase.query.filter(workDatabase.workgroup == workgroup).order_by(
            func.random()).limit(10)
    else:       #'最热作品'
        works = workDatabase.query.filter(workDatabase.workgroup == workgroup).order_by(
            workDatabase.thumbNum.desc()).limit(10)

    #响应点赞
    thumbUpWorkId = request.args.get('workid', '')
    if thumbUpWorkId:
        thumbUpRecord = thumbWork.query.filter_by(workid=thumbUpWorkId,
                                                  thumbUpEmail=current_user.userEmail).first()
        if thumbUpRecord is None:
            thumbID = thumbWork.query.count() + 1
            thumbUpRecords = thumbWork(thumbId=thumbID, workid=thumbUpWorkId,
                                       thumbUpEmail=current_user.userEmail,
                                       thumbTime=str(datetime.now()))
            ChooseWork = workDatabase.query.filter_by(workid=thumbUpWorkId).first()

            ChooseWork.thumbNum = thumbWork.query.filter_by(workid=thumbUpWorkId).count()+1
            def istoday(t):
                #当天
                time=datetime.strptime(str(t), "%Y-%m-%d %H:%M:%S.%f")
                now=datetime.now()
                return (now-time).days==0

            def isThisWeek(t):
                #本周
                time=datetime.strptime(str(t), "%Y-%m-%d %H:%M:%S.%f")
                now=datetime.now()
                return (now-time).days<=5

            ChooseWork.thumbNumDaily = thumbWork.query.filter(thumbWork.workid == thumbUpWorkId, istoday(thumbWork.thumbTime)).count()+1
            ChooseWork.thumbNumWeekly = thumbWork.query.filter(thumbWork.workid == thumbUpWorkId, isThisWeek(thumbWork.thumbTime)).count()+1

            db.session.add(ChooseWork)
            db.session.add(thumbUpRecords)
            db.session.commit()
            return "点赞成功"
        else:
            return "无法点赞，可能您已经为该愿望点赞了，或者存在其他系统故障"

    if works.count() == 0:
        flash("还没有作品")

    return render_template('battle.html',choice=choice,works=works)

@app.route('/hole', methods=['GET', 'POST'])
def hole():
    if current_user.userSex:
        sex="男"
    else:
        sex="女"

    works=workDatabase.query.filter(workDatabase.userEmail==current_user.userEmail,workDatabase.workgroup != "delete")

    return render_template('hole.html',name=current_user.userNickName,sex=sex,works=works)

class uploadform(FlaskForm):
    name = StringField('作品名称')
    img =  FileField('作品内容（最大10MB）')
    type=RadioField("分区类型", choices=[(1, 'wonderland 主题为新年/春天的故事'),(2,'party 主题为宅居日常&生活杂谈'),
                                     (3,'battle 主题为疫情相关内容'),(4,'kitchen 主题为黑暗料理vs美食佳肴')],
                        validators=[], coerce=int)
    text = TextAreaField(" 作品内容 ", validators=[DataRequired()])
    submit = SubmitField("上传作品")

def save_local(file, file_name):
    save_path = "static/workImg"
    file.save(os.path.join(save_path, file_name))
    return '/image/' + file_name

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form=uploadform()
    if form.validate_on_submit():
        name = form.name.data
        img = request.files['img']
        if img.filename=='':
            flash('未选择文件')
            return redirect(url_for('upload'))
        imgname='userimg/'+str(workDatabase.query.count()+1)+img.filename
        img.save('static/'+imgname)
        text = form.text.data
        workid = workDatabase.query.filter().count()+1
        type=form.type.data
        if type==1:
            typename='wonderland'
        elif type==2:
            typename='party'
        elif type==3:
            typename='battle'
        else:
            typename='kitchen'
        mywork=workDatabase(workid=workid,workgroup=typename,
                            userEmail=current_user.userEmail,userStatus=current_user.userStatus,
                            userNickName=current_user.userNickName,
                            worktitle=name,workContent=text,workImgPath=imgname)
        db.session.add(mywork)
        db.session.commit()
        InserTicket(current_user.userEmail,current_user.userSchoolNum)

        flash("作品以上传成功！请等待审核！一张号码券已放入‘我的号码券’！")
    return render_template('upload.html',form=form)
###############################################################################################################################

@app.route('/sing', methods=['GET', 'POST'])
@fresh_login_required
def sing():
    if timelimit:
        sign = checkTimeLimit()
        if not sign:
            flash(NOT_START_STRING)
            return redirect(url_for('index'))
    if current_user.userEmail is None:
        return redirect(url_for('append'))
    return render_template('sing.html')


#####################################################################################
# 愿望实现

class thumbWish(db.Model):
    thumbId = db.Column(db.Integer, primary_key=True, unique=True, index=True)
    wishUserEmail = db.Column(db.String(64))
    thumbUpEmail = db.Column(db.String(64))


class wishform(FlaskForm):
    wishText = TextAreaField(" 许愿内容 ", validators=[DataRequired()])
    submit = SubmitField("许愿")


class selectform(FlaskForm):
    wishid = RadioField("愿望序号", choices=[(i, "%d 号愿望" % i) for i in range(1, 6)],
                        validators=[], coerce=int)
    submit1 = SubmitField("选择愿望")


class thumbUpform(FlaskForm):
    wishid = RadioField("点赞愿望", choices=[(i, "%d 号愿望" % i) for i in range(1, 6)],
                        validators=[], coerce=int)
    submit4 = SubmitField("点赞愿望")


class finishform(FlaskForm):
    submit2 = SubmitField("完成愿望")


class updateform(FlaskForm):
    submit3 = SubmitField("刷新愿望")


class refreshform(FlaskForm):
    submit4 = SubmitField("重新领取愿望")


class selectwishes(db.Model):
    userEmail = db.Column(db.String(64), primary_key=True, unique=True, index=True)
    userSchoolNum = db.Column(db.String(64), nullable=True)
    userStatus = db.Column(db.Integer, nullable=True)

    girlNickName = db.Column(db.String(64), nullable=True)
    girlEmail = db.Column(db.String(64), nullable=True)
    girlQQnum = db.Column(db.String(64), nullable=True)
    girlTelnum = db.Column(db.String(64), nullable=True)
    girlSchoolNum = db.Column(db.String(64), nullable=True)
    cashid = db.Column(db.String(1000), nullable=True)
    wishstatus = db.Column(db.Integer, nullable=True, default=0)
    # 0 选取未完成 1选取完成
    selecttime = db.Column(db.String(64), nullable=True)
    lastviewtime = db.Column(db.String(64), nullable=True)
    lastupdatetime = db.Column(db.String(64), nullable=True)
    achievestatus = db.Column(db.Integer, nullable=True, default=0)
    # 0 为女生未确认完成 ，1 为女生确认完成


class wishDatabase(db.Model):
    __tablename__ = "wishes"
    userEmail = db.Column(db.String(64), primary_key=True, unique=True, index=True)
    userStatus = db.Column(db.Integer, nullable=True)
    userSchoolNum = db.Column(db.String(64), nullable=True)
    wishNickName = db.Column(db.String(64), nullable=True)
    girlQQnum = db.Column(db.String(64), nullable=True)
    girlTelnum = db.Column(db.String(64), nullable=True)
    wishcontent = db.Column(db.String(1000), nullable=True)
    wishstatus = db.Column(db.Integer, nullable=True, default=0)
    # 0 未选取 1 男生已选取 2 男生已完成 3女生已经确认
    wishid = db.Column(db.Integer, nullable=True)

    boyNickName = db.Column(db.String(64), nullable=True)
    boyQQnum = db.Column(db.String(64), nullable=True)
    boyEmail = db.Column(db.String(64), nullable=True)
    boySchoolNum = db.Column(db.String(64), nullable=True)
    boyTelnum = db.Column(db.String(64), nullable=True)

    thumbUpNum = db.Column(db.Integer, nullable=True, default=0)


class achieveform(FlaskForm):
    submit = SubmitField("认同完成愿望")


@app.route('/wishpool', methods=['GET', 'POST'])
@fresh_login_required
def wishpool():
    # img_path = '/home/dean/USTCstunion_girl_days/static/img/before.png'
    # figfile = io.BytesIO(open(img_path, 'rb').read())
    # img_stream = base64.b64encode(figfile.getvalue()).decode('ascii')

    sex = current_user.userSex
    wishes = wishDatabase.query.filter(wishDatabase.userStatus == 1, wishDatabase.wishstatus != 3).order_by(
        func.random()).limit(5)
    thumbUpWishEmail = request.args.get('email', '')
    if thumbUpWishEmail:
        thumbUpRecord = thumbWish.query.filter_by(wishUserEmail=thumbUpWishEmail,
                                                  thumbUpEmail=current_user.userEmail).first()
        if thumbUpRecord is None:
            thumbID = thumbWish.query.count() + 1
            thumbUpRecords = thumbWish(thumbId=thumbID, wishUserEmail=thumbUpWishEmail,
                                       thumbUpEmail=current_user.userEmail)
            ChooseWish = wishDatabase.query.filter_by(userEmail=thumbUpRecords.wishUserEmail).first()
            ChooseWish.thumbUpNum = ChooseWish.thumbUpNum + 1
            db.session.add(ChooseWish)
            db.session.add(thumbUpRecords)
            db.session.commit()
            return "点赞成功"

        else:
            return "无法点赞，可能您已经为该愿望点赞了，或者存在其他系统故障"

    if wishes.count() == 0:
        flash("还没有可以选择的愿望。")
        return render_template('wishpool.html', sex=sex, wishes=wishes)
    return render_template('wishpool.html', sex=sex, wishes=wishes)



@app.route('/wish', methods=['GET', 'POST'])
@fresh_login_required
def wish():
    if timelimit:
        sign = checkTimeLimit()
        if not sign:
            flash(NOT_START_STRING)
            return redirect(url_for('index'))
    if current_user.userEmail is None:
        return redirect(url_for('append'))
    return render_template('wish.html', sex=current_user.userSex,userStatus=current_user.userStatus)

@app.route('/girl', methods=['GET', 'POST'])
@fresh_login_required
def girl():
    if current_user.userSex == MALE:
        flash("男同学不能进来啊！")
        return redirect(url_for("index"))
    if timelimit == 1 and not checkTimeLimit():
        flash(NOT_START_STRING)
        return redirect(url_for('index'))
    form = wishform()
    achieveforms = achieveform()
    if current_user.userEmail is None:
        return redirect(url_for('append'))
    if form.validate_on_submit():
        wishtext = form.wishText.data
        record = wishDatabase.query.filter_by(userEmail=current_user.userEmail,
                                              userSchoolNum=current_user.userSchoolNum).first()
        if record is None:
            mywish = wishDatabase(userEmail=current_user.userEmail, wishcontent=wishtext, wishstatus=0,
                                  girlQQnum=current_user.userQQnum, userStatus=current_user.userStatus,
                                  userSchoolNum=current_user.userSchoolNum, wishNickName=current_user.userNickName,
                                  girlTelnum=current_user.userTelnum, thumbUpNum=0)
            db.session.add(mywish)
            db.session.commit()
            flash("收到你的愿望了!")
            return redirect(url_for('girl'))
        else:
            if record.wishstatus == 0:
                record.wishcontent = wishtext
                db.session.add(record)
                db.session.commit()
                flash("修改愿望成功！")
                return redirect(url_for('girl'))
            elif record.wishstatus == 3:
                return render_template('500.html'), 500
            flash("对不起，你的愿望已经被选取！")
            return redirect(url_for('girl'))
    mywish = wishDatabase.query.filter_by(userEmail=current_user.userEmail,
                                          userSchoolNum=current_user.userSchoolNum).first()
    if mywish is not None:
        mywish.userStatus = current_user.userStatus
        db.session.add(mywish)
        db.session.commit()
        mywish = wishDatabase.query.filter_by(userEmail=current_user.userEmail,
                                              userSchoolNum=current_user.userSchoolNum).first()
        if mywish.boySchoolNum is not None:
            mywish.boySchoolNum = mywish.boySchoolNum[:-4] + "****"
    if achieveforms.validate_on_submit():
        mywish = wishDatabase.query.filter_by(userEmail=current_user.userEmail,
                                              userSchoolNum=current_user.userSchoolNum).first()
        boylog = selectwishes.query.filter_by(girlEmail=current_user.userEmail,
                                              girlSchoolNum=current_user.userSchoolNum).first()
        if mywish is not None and boylog is not None and mywish.wishstatus!=3:
            boylog.achievestatus = 1
            mywish.wishstatus = 3
            InserTicket(mywish.userEmail,mywish.userSchoolNum)
            InserTicket(boylog.userEmail,boylog.userSchoolNum)
            flash('获得一张奖券，请到我的奖券领取奖券~')
            db.session.add(boylog)
            db.session.add(mywish)
            db.session.commit()
            flash("你已确认")
            return redirect(url_for('girl'))
        return redirect(url_for('girl'))
    return render_template('girl.html', form=form, mywish=mywish, userStatus=current_user.userStatus,
                           achieveform=achieveforms)


@app.route('/boy', methods=['GET', 'POST'])
@fresh_login_required
def boy():
    if current_user.userSex == FEMALE:
        flash("女同学不能进来哦～")
        return redirect(url_for("index"))
    if timelimit == 1 and not checkTimeLimit():
        flash(NOT_START_STRING)
        return redirect(url_for('index'))
    if current_user.userEmail is None:
        return redirect(url_for('append'))
    myrecord = selectwishes.query.filter_by(userEmail=current_user.userEmail,
                                            userSchoolNum=current_user.userSchoolNum).first()
    selectwishform = selectform()
    finishwishform = finishform()
    updatewishform = updateform()
    refreshwishform = refreshform()

    # 选择愿望
    if selectwishform.validate_on_submit() and selectwishform.submit1.data:
        wishid = selectwishform.wishid.data
        myrecord = selectwishes.query.filter_by(userEmail=current_user.userEmail,
                                                userSchoolNum=current_user.userSchoolNum).first()
        if current_user.userStatus == 0:
            flash(NOT_ACTIVATE_STRING)
            return redirect(url_for('boy'))
        if myrecord.wishstatus != 0:
            flash("对不起，你已经选取了愿望。")
            return redirect(url_for('boy'))
        mycash = myrecord.cashid.split(";")
        mycash = [x for x in mycash if x]
        if wishid > len(mycash) or wishid < 0:
            flash("对不起，选择愿望序号有误。")
            return redirect(url_for("boy"))
        myselectemail = mycash[wishid - 1]
        otherselect = selectwishes.query.filter_by(girlEmail=myselectemail).first()
        if otherselect is not None:
            flash("对不起，该愿望已经被选取。")
            return redirect(url_for('wish'))
        girllog = wishDatabase.query.filter_by(userEmail=myselectemail, wishstatus=0).first()
        if girllog is None:
            flash("对不起,不能选择该愿望")
            return redirect(url_for('wish'))
        myrecord.wishstatus = 1
        myrecord.girlEmail = myselectemail
        myrecord.girlQQnum = girllog.girlQQnum
        myrecord.girlSchoolNum = girllog.userSchoolNum
        myrecord.girlTelnum = girllog.girlTelnum
        myrecord.girlNickName = girllog.wishNickName
        myrecord.achievestatus = 0
        myrecord.selecttime = datetime.now()
        girllog.wishstatus = 1
        girllog.boyQQnum = current_user.userQQnum
        girllog.boyEmail = current_user.userEmail
        girllog.boySchoolNum = current_user.userSchoolNum
        girllog.boyTelNum = current_user.userTelnum
        girllog.boyNickName = current_user.userNickName
        db.session.add(myrecord)
        db.session.add(girllog)
        db.session.commit()
        flash("选取愿望成功！")
        return redirect(url_for('boy'))

    # 完成愿望!
    if finishwishform.validate_on_submit() and finishwishform.submit2.data:
        if current_user.userStatus == 0:
            flash(NOT_ACTIVATE_STRING)
            return redirect(url_for('boy'))
        myrecord = selectwishes.query.filter_by(userEmail=current_user.userEmail,
                                                userSchoolNum=current_user.userSchoolNum).first()
        girllog = wishDatabase.query.filter_by(userEmail=myrecord.girlEmail).first()
        if (myrecord is not None) and (girllog is not None):
            myrecord.wishstatus = 2
            girllog.wishstatus = 2
            db.session.add(myrecord)
            db.session.add(girllog)
            db.session.commit()
            flash("完成愿望成功!")
            return redirect(url_for('boy'))
        return redirect(url_for('boy'))

    # 更新愿望!
    if updatewishform.validate_on_submit() and updatewishform.submit3.data:
        myrecord = selectwishes.query.filter_by(userEmail=current_user.userEmail,
                                                userSchoolNum=current_user.userSchoolNum).first()
        if current_user.userStatus == 0:
            flash(NOT_ACTIVATE_STRING)
            return redirect(url_for('boy'))
        if myrecord.lastupdatetime is None:
            wishes = wishDatabase.query.filter_by(wishstatus=0, userStatus=1).order_by(func.random()).limit(5)
            if wishes.count() == 0:
                flash("当前没有可以被选取的愿望。")
                return redirect(url_for('boy'))
            mystr = ";".join([wish.userEmail for wish in wishes if wish.userEmail])
            if mystr:
                myrecord.cashid = mystr
            myrecord.lastupdatetime = str(datetime.now())
            db.session.add(myrecord)
            db.session.commit()
            flash("刷新愿望成功。")
            return redirect(url_for('boy'))
        nowtime = datetime.now()
        lastupdatetime = datetime.strptime(myrecord.lastupdatetime, "%Y-%m-%d %H:%M:%S.%f")
        if (nowtime - lastupdatetime).total_seconds() >= 4 * 3600:  # 4 hours
            wishes = wishDatabase.query.filter_by(wishstatus=0, userStatus=1).order_by(func.random()).limit(5)
            if wishes.count() == 0:
                flash("没有可以被选取的愿望。")
                return redirect(url_for('boy'))
            mystr = ";".join([wish.userEmail for wish in wishes if wish.userEmail])
            if mystr:
                myrecord.cashid = mystr
            myrecord.lastupdatetime = str(nowtime)
            db.session.add(myrecord)
            db.session.commit()
            flash("刷新愿望成功。")
            return redirect(url_for('boy'))
        flash("每 6 小时只允许刷新一次。")
        return redirect(url_for('boy'))

    # 女生确认完成愿望后可以刷新
    if refreshwishform.validate_on_submit() and refreshwishform.submit4.data:
        if current_user.userStatus == 0:
            flash(NOT_ACTIVATE_STRING)
            return redirect(url_for('boy'))
        myrecord = selectwishes.query.filter_by(userEmail=current_user.userEmail,
                                                userSchoolNum=current_user.userSchoolNum).first()
        if (myrecord is not None):
            if myrecord.achievestatus == 1:
                myrecord.wishstatus = 0
                db.session.add(myrecord)
                db.session.commit()
                flash("刷新成功")
                return redirect(url_for('boy'))
            else:
                flash("请确认女生同意你完成")
        return redirect(url_for('boy'))
    if myrecord is None:
        myrecord = selectwishes(userEmail=current_user.userEmail, userStatus=current_user.userStatus,
                                userSchoolNum=current_user.userSchoolNum, achievestatus=0, wishstatus=0)
        db.session.add(myrecord)
        db.session.commit()
        return redirect(url_for('boy'))
    myrecord.userStatus = current_user.userStatus
    db.session.add(myrecord)
    db.session.commit()
    myrecord = selectwishes.query.filter_by(userEmail=current_user.userEmail,
                                            userSchoolNum=current_user.userSchoolNum).first()
    if myrecord.cashid is None:
        wishes = wishDatabase.query.filter_by(wishstatus=0, userStatus=1).order_by(func.random()).limit(5)
        if wishes.count() == 0:
            flash("没有可以被选取的愿望。")
            return redirect(url_for('wish'))
        mystr = ";".join([wish.userEmail for wish in wishes if wish.userEmail])
        if mystr:
            myrecord.cashid = mystr
        myrecord.lastviewtime = str(datetime.now())
        db.session.add(myrecord)
        db.session.commit()
        return redirect(url_for('boy'))
    if myrecord.lastupdatetime is None:
        myrecord.lastupdatetime = "2020-01-01 00:00:00.000000"
        db.session.add(myrecord)
        db.session.commit()
        return redirect(url_for('boy'))
    if current_user.userStatus == 0:
        flash(NOT_ACTIVATE_STRING)
    achievewish = wishDatabase.query.filter_by(wishstatus=3, userStatus=1, boyEmail=current_user.userEmail)
    achieveNum = achievewish.count()
    if myrecord.wishstatus == 1:
        myselectwish = wishDatabase.query.filter_by(userEmail=myrecord.girlEmail).first()
        wishes = []
        magiccode = 0
        return render_template("boy.html", selectwishform=selectwishform, updatewishform=updatewishform,
                               finishwishform=finishwishform, myselectwish=myselectwish, wishes=wishes,
                               magiccode=magiccode, userStatus=current_user.userStatus,
                               achieveWishes=achievewish, achieveNum=achieveNum)
    if myrecord.wishstatus == 2:
        myselectwish = wishDatabase.query.filter_by(userEmail=myrecord.girlEmail).first()
        wishes = []
        magiccode = 0
        myselectwish.userSchoolNum = myselectwish.userSchoolNum[:-4] + "****"
        return render_template("boy.html", selectwishform=selectwishform, updatewishform=updatewishform,
                               finishwishform=finishwishform, myselectwish=myselectwish, wishes=wishes,
                               magiccode=magiccode, userStatus=current_user.userStatus,
                               achieveWishes=achievewish, achieveNum=achieveNum)
    lasttime = datetime.strptime(str(myrecord.lastviewtime), "%Y-%m-%d %H:%M:%S.%f")
    nowtime = datetime.now()
    if (nowtime - lasttime).total_seconds() >= 4 * 3600:  # 4 hours
        wishes = wishDatabase.query.filter_by(wishstatus=0, userStatus=1).order_by(func.random()).limit(5)
        if wishes.count() == 0:
            flash("没有可以被选取的愿望")
        mystr = ";".join([wish.userEmail for wish in wishes if wish.userEmail])
        if mystr:
            myrecord.cashid = mystr
            myrecord.lastviewtime = str(datetime.now())
        db.session.add(myrecord)
        db.session.commit()
        return redirect(url_for('boy'))
    myselectwish = selectwishes.query.filter_by(userEmail=current_user.userEmail,
                                                userSchoolNum=current_user.userSchoolNum).first()
    wishes = []
    mywishesid = myselectwish.cashid.split(";")
    mywishesid = [x for x in mywishesid if x]

    magiccode = 1
    for peremail in mywishesid:
        if peremail is None:
            continue
        onewish = wishDatabase.query.filter_by(userEmail=peremail).first()
        wishes.append(onewish)
    setattr(selectform, 'wishid',
            RadioField("愿望序号", choices=[(i, "%d 号愿望" % i) for i in range(1, 1 + len(wishes))],
                       validators=[], coerce=int))

    return render_template("boy.html", selectwishform=selectwishform, updatewishform=updatewishform,
                           finishwishform=finishwishform, myselectwish=myselectwish, wishes=wishes, magiccode=magiccode,
                           userStatus=current_user.userStatus, achieveWishes=achievewish, achieveNum=achieveNum)


############################################################


class LoginForm(FlaskForm):
    email = StringField("请使用科大校内邮箱注册的用户名登录!\n（以 @mail.ustc.edu.cn或 @ustc.edu.cn 结尾，若无邮箱后缀则默认为 @mail.ustc.edu.cn）",
                        validators=[DataRequired(), Length(1, 256)])
    password = PasswordField("请输入密码", validators=[DataRequired()])
    remember_me = BooleanField("记住登录状态")
    submit = SubmitField("Log In")


class RegisterForm(FlaskForm):
    nickname = StringField("昵称（前台可见）", validators=[DataRequired()])
    email = StringField("电子邮箱（中科大校内邮箱，以 @mail.ustc.edu.cn、@ustc.edu.cn 结尾）",
                        validators=[DataRequired(), Length(1, 64), Email()])
    schoolnum = StringField("学号", validators=[DataRequired()])
    password = PasswordField('请设置密码', validators=[DataRequired(), Length(6, 64)])
    QQnum = StringField(" QQ 号码", validators=[DataRequired()])
    Telnum = StringField(" 手机号码", validators=[DataRequired()])
    sex = RadioField("性别", choices=[(1, "男"), (0, "女")], validators=[], coerce=int)
    accept_terms = BooleanField('是否同意如下授权？\n'
                                '（1）昵称所有平台用户可见\n'
                                '（2）填写的联系方式将会呈现给领取你愿望的人/你领取愿望的人，实现你愿望的人/你实现愿望的人，以及匹配中的同学\n'
                                '邮箱显示给匹配同学/领取（许下）愿望同学'
                                '同意在不公开姓名、昵称、学号、联系方式等个人信息的情况下个人许下的愿望或事件用于调研与采纳以及公众号展示'
                                , default='checked', validators=[DataRequired()])
    submit = SubmitField('注册')

    def validate_email(self, field):
        field.data = field.data.strip()
        if not field.data.endswith("@mail.ustc.edu.cn") and not field.data.endswith("@ustc.edu.cn"):
            raise ValidationError('请使用 @mail.ustc.edu.cn 或者 @ustc.edu.cn')
        user = User.query.filter_by(userEmail=field.data).first()
        if user is not None and user.userStatus == 1:
            raise ValidationError('电子邮箱已经注册')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('旧密码', validators=[DataRequired()])
    password = PasswordField('新密码',
                             validators=[DataRequired(), Length(6, 64), EqualTo('password2', message='两次输入的密码必须相等')])
    password2 = PasswordField('确认新密码', validators=[DataRequired()])
    submit = SubmitField('确认修改密码')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('您注册的邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    submit = SubmitField('重置密码')


class PasswordResetForm(FlaskForm):
    password = PasswordField('新的密码', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('确认新的密码', validators=[DataRequired()])
    submit = SubmitField('重置密码')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(401)
def unauthorized(e):
    flash("你尚未登录!")
    return redirect(url_for('login'))


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/index')
@app.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_anonymous:
        return render_template('index.html', userStatus=1)
    return render_template('index.html', userStatus=current_user.userStatus)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if not form.email.data.endswith("@mail.ustc.edu.cn") and not form.email.data.endswith("@ustc.edu.cn"):
            form.email.data += "@mail.ustc.edu.cn"
        user = User.query.filter_by(userEmail=form.email.data).first()
        if user is not None and user.verifyPassword(form.password.data):
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('index')
            return redirect('/')
        flash("邮箱地址或者密码不正确")
    return render_template('auth/login.html', form=form)


@app.route('/logout')
@fresh_login_required
def logout():
    logout_user()
    # cas_logout_url = cas_client.get_logout_url(service_url=app_login_url)
    return redirect("https://passport.ustc.edu.cn/logout")


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        newuserpassword = form.password.data
        newuseremail = form.email.data.strip()
        newusersex = form.sex.data
        newuserQQnum = form.QQnum.data
        newuserschoolnum = form.schoolnum.data
        newuserTelnum = form.Telnum.data
        newuserNickName = form.nickname.data
        if not form.accept_terms.data:
            flash("请同意用户协议")
            return redirect(url_for("register"))
        if not newuseremail.endswith("@mail.ustc.edu.cn") and newuseremail.endswith("@ustc.edu.cn"):
            flash("用户邮箱请使用 USTC 校内邮箱地址")
            return redirect(url_for("register"))
        user = User.query.filter_by(userEmail=form.email.data).first()
        checkuser=User.query.filter_by(userSchoolNum=newuserschoolnum).first()
        if checkuser is not None:
           flash('该学号已经被注册，请检查是否已经注册过了账户，到修改密码的地方更换')
           return redirect(url_for("register"))
        if user is None:
            user = User(userEmail=newuseremail, userSchoolNum=newuserschoolnum, userQQnum=newuserQQnum,
                        userSex=newusersex, userTelnum=newuserTelnum,
                        userNickName=newuserNickName)
        else:
            User.query.filter_by(userEmail=form.email.data).delete()
            user = User(userEmail=newuseremail, userSchoolNum=newuserschoolnum, userQQnum=newuserQQnum,
                        userSex=newusersex, userTelnum=newuserTelnum,
                        userNickName=newuserNickName)
        user.setPassword(newuserpassword)
        user.userStatus = 0
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        mymsg = mySendMailFormat("Student Union 邀请您激活账户", "ustcstuniongirl@163.com", user.userEmail, "",
                                 "auth/email/confirm",
                                 token=token, user=user)
        simpleSendMail(app, mymsg)
        flash("注册成功 , 激活账户的邮件已发往您的 USTC 校内邮箱 ！")
        flash("邮件可能标记为垃圾邮件")
        flash("您现在即可登录！")
        return redirect(url_for("login"))
    return render_template("auth/register.html", form=form)


@app.route('/confirm/<token>')
@fresh_login_required
def confirm(token):
    if current_user.userStatus:
        return redirect(url_for('index'))
    if current_user.confirm(token):
        db.session.commit()
        flash("你已经激活了你的账户，谢谢！")
    else:
        flash("激活链接已经失效！")
    return redirect(url_for("index"))


@app.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.is_anonymous or current_user.userStatus:
        return redirect(url_for('index'))
    return render_template('auth/unconfirmed.html')


class checkemailtime(db.Model):
    userEmail = db.Column(db.String(64), primary_key=True, unique=True, index=True)
    timestamp = db.Column(db.String(256), nullable=True)


@app.route('/confirm')
@fresh_login_required
def resend_confirmation():
    stamp = checkemailtime.query.filter_by(userEmail=current_user.userEmail).first()
    if stamp is None:
        newtimestamp = checkemailtime(userEmail=current_user.userEmail, timestamp=str(datetime.now()))
        db.session.add(newtimestamp)
        db.session.commit()
        token = current_user.generate_confirmation_token()
        mymsg = mySendMailFormat("Student Union 邀请您激活账户", "ustcstuniongirl@163.com", current_user.userEmail, "",
                                 "auth/email/confirm", token=token, user=current_user)
        simpleSendMail(app, mymsg)
        flash("邮件已经发送，请注意查收！")
        return redirect(url_for('index'))
    nowtime = datetime.now()
    lasttime = datetime.strptime(str(stamp.timestamp), "%Y-%m-%d %H:%M:%S.%f")
    if (nowtime - lasttime).seconds <= 600:
        flash("对不起，您申请激活邮件的次数过于频繁, 10min后再试试吧!")
        return redirect(url_for('index'))
    stamp.timestamp = str(datetime.now())
    db.session.add(stamp)
    db.session.commit()
    token = current_user.generate_confirmation_token()
    mymsg = mySendMailFormat("Student Union 邀请您激活账户", "ustcstuniongirl@163.com", current_user.userEmail, "",
                             "auth/email/confirm", token=token, user=current_user)
    simpleSendMail(app, mymsg)
    flash("邮件已经发送,请注意查收！")
    return redirect(url_for('index'))


@app.route('/change-password', methods=['GET', 'POST'])
@fresh_login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verifyPassword(form.old_password.data):
            current_user.setPassword(form.password.data)
            db.session.add(current_user)
            db.session.commit()
            flash('你已经更改密码。')
            return redirect(url_for('index'))
        else:
            flash('Invalid password.')
    return render_template("auth/change_password.html", form=form)


@app.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(userEmail=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            # send_email(user.email, 'Reset Your Password','auth/email/reset_password', user=user, token=token)
            mymsg = mySendMailFormat("Student Union 更改您的账户密码", "ustcstuniongirl@163.com", user.userEmail, "",
                                     "auth/email/reset_password", token=token, user=user)
            simpleSendMail(app, mymsg)
            flash("邮件已经发送，请注意查收！")
            return redirect(url_for('login'))
        flash('可能哪里有些不对，你确定你注册过账户吗？')
        return redirect(url_for('index'))
    return render_template('auth/reset_password.html', form=form)


@app.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.password.data):
            db.session.commit()
            flash('你已经更新了你的密码。')
            return redirect(url_for('login'))
        else:
            flash('Token 错误')
            return redirect(url_for('index'))
    return render_template('auth/reset_password.html', form=form)


########################################################
# 统一认证接口
class appendUserDataForm(FlaskForm):
    nickname = StringField("昵称（前台可见）", validators=[DataRequired()])
    email = StringField("电子邮箱（中科大校内邮箱，以 @mail.ustc.edu.cn、@ustc.edu.cn 结尾）",
                        validators=[DataRequired(), Length(1, 64), Email()])
    schoolnum = StringField("学号", validators=[DataRequired()])
    password = PasswordField('请设置密码', validators=[DataRequired(), Length(6, 64)])
    QQnum = StringField(" QQ 号码", validators=[DataRequired()])
    Telnum = StringField(" 手机号码", validators=[DataRequired()])
    sex = RadioField("性别", choices=[(1, "男"), (0, "女")], validators=[], coerce=int)
    submit = SubmitField('补全资料')

    def validate_email(self, field):
        field.data = field.data.strip()
        if not field.data.endswith("@mail.ustc.edu.cn") and not field.data.endswith("@ustc.edu.cn"):
            raise ValidationError('请使用 @mail.ustc.edu.cn 或者 @ustc.edu.cn')
        user = User.query.filter_by(userEmail=field.data).first()
        if user is not None and user.userStatus == 1:
            raise ValidationError('您填写的电子邮箱已经被注册。')


@app.route('/append', methods=['GET', 'POST'])
@fresh_login_required
def append():
    myrecord = User.query.filter_by(userSchoolNum=current_user.userSchoolNum).first()
    if myrecord is None:
        flash("请重新登录！")
        return redirect(url_for('logout'))
    infostatus = 0
    infoform = appendUserDataForm()
    if current_user.userEmail is not None:
        flash("您已完整填写个人信息。")
        return redirect(url_for('index'))
    if infoform.validate_on_submit():
        myrecord.userEmail = infoform.email.data
        myrecord.userQQnum = infoform.QQnum.data
        myrecord.userSex = infoform.sex.data
        myrecord.Telnum=infoform.Telnum.data
        myrecord.NickName=infoform.nickname.data
        myrecord.setPassword(infoform.password.data)
        db.session.add(myrecord)
        db.session.commit()
        return redirect(url_for("append"))
    return render_template('append.html', form=infoform)


@app.route('/caslogin', methods=['GET', 'POST'])
def caslogin():
    ticket = request.args.get('ticket')
    app_login_url = 'https://stunion.ustc.edu.cn/caslogin'
    cas_url = 'https://passport.ustc.edu.cn'
    cas_client = CASClient(cas_url, auth_prefix='')
    if ticket:
        try:
            cas_response = cas_client.perform_service_validate(
                ticket=ticket,
                service_url=app_login_url,
            )
        except Exception:
            # CAS server is currently broken, try again later.
            return redirect(url_for('index'))
        if cas_response and cas_response.success:
            # print(cas_response)
            # print("cas_response.response_text:", cas_response.response_text)
            # print("cas_response.data", cas_response.data)
            # print("cas_response.user", cas_response.user)
            # print("cas_response.attributes", cas_response.attributes)
            myrecord = User.query.filter_by(userSchoolNum=cas_response.user).first()
            if myrecord is None:
                newuser = User(userSchoolNum=cas_response.user, userStatus=1)
                db.session.add(newuser)
                db.session.commit()
                newuser = User.query.filter_by(userSchoolNum=cas_response.user).first()
                login_user(newuser)
                # cas_client.session_exists(ticket)
                # cas_client.delete_session(ticket)
                return redirect(url_for('append'))
            login_user(myrecord)
            # cas_client.session_exists(ticket)
            # cas_client.delete_session(ticket)
            return redirect(url_for('append'))
    cas_login_url = cas_client.get_login_url(service_url=app_login_url)
    return redirect(cas_login_url)


@app.route('/faq', methods=['GET', 'POST'])
def faq():
    return render_template("faq.html")

def flash_event():
    events=['背单词','看日出','和ta同步自习','打数理基础',
            '摄影','每天早上电话叫醒对方','学习Matlab','看剧','折纸','分享恋爱经历&经验','每日睡前故事','每天写日记'
            '每天制作手账']
    i=19
    for event in events:
        i=i+1
        newrecord=EventDatabase(eventId=i,eventName=event)
        db.session.add(newrecord)
        db.session.commit()

def refreshDatabase():
    db.drop_all()
    db.create_all()
    flash_event()


@app.teardown_request
def teardown_request(exception):
    db.session.close()

@app.after_request
def releaseDB(response):
    db.session.close()
    return response

if __name__ == "__main__":
    ##refreshDatabase()
    ##flash_event()
    ##db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
