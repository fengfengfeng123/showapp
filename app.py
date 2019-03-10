# -*- coding: utf-8 -*-
import os
import sys
import click
import tablib
from flask import Flask, render_template, request, redirect, flash
from flask import url_for
from flask_sqlalchemy import SQLAlchemy
from flask import  make_response
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager
from flask_login import login_user,login_required,logout_user


app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:feng1101@localhost:3306/duanxin'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager(app)



@login_manager.user_loader#初始化用户账号密码
def load_user(user_id):
    user = User.query.get(int(user_id))
    return user

login_manager.login_view = 'login'


@app.shell_context_processor
def make_shell_context():
    return dict(db = db,Line = Line,Taiqu = Taiqu,Kongzhi = Kongzhi,Gongbian = Gongbian,Yonghu = Yonghu,User = User)

name = '白工线'
lines = [
    {'linename' :'10KV白工线B月湖岩#00分之箱'},
    {'linename' : '10KV白工线B月湖岩FD021刀闸（D02开关）'},
    {'linename' :  '#09杆'},
    {'linename' :  '#08杆'},
    {'linename' :  '#02杆'},
]

class User(db.Model, UserMixin):#用户数据库,如果登录，current_user.is_authenticated 返回true
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash.decode(), password)

class Taiqu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20),unique=True)
    zhuangtai = db.Column(db.Boolean, default= False)
    lines = db.relationship('Line',back_populates = 'taiqu')
    def __repr__(self):
        return '<Taiqu %r>' % self.name

class Line(db.Model):#线路名称
    id = db.Column(db.Integer, primary_key=True)
    linename = db.Column(db.String(30),index=True)
    zhuangtai = db.Column(db.Boolean, default=False)
    taiqu_id = db.Column(db.Integer,db.ForeignKey('taiqu.id'))
    taiqu = db.relationship('Taiqu',back_populates = 'lines')
    kongzhis = db.relationship('Kongzhi',back_populates = 'line')#控制关系
    def __repr__(self):
        return '<Line %r>' % self.linename


class Kongzhi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kzname = db.Column(db.String(20), unique=True)
    zhuangtai = db.Column(db.Boolean, default=False)
    fushu_id = db.Column(db.Integer)
    dengji = db.Column(db.String(10))
    line_id = db.Column(db.Integer, db.ForeignKey('line.id'))
    line = db.relationship('Line', back_populates='kongzhis')
    gongbians = db.relationship('Gongbian', back_populates='kongzhi')
    def __repr__(self):
        return '<Kongzhi %r>' % self.kzname

class Gongbian(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gbname = db.Column(db.String(20), unique=True)
    beizhu = db.Column(db.String(20))
    huhao = db.Column(db.String(20), unique=True)
    ronglang = db.Column(db.String(20), unique=True)
    zhuangtai = db.Column(db.Boolean, default=False)
    kongzhi_id = db.Column(db.Integer, db.ForeignKey('kongzhi.id'))
    kongzhi = db.relationship('Kongzhi', back_populates='gongbians')
    yonghus = db.relationship('Yonghu',back_populates = 'gongbian')

class Yonghu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(40), unique=True)
    yhname = db.Column(db.String(60))
    yhdizhi  = db.Column(db.String(60), unique=True)
    telephone = db.Column(db.String(40),unique= True)
    minggandu = db.Column(db.Integer)
    zhuangtai = db.Column(db.Boolean, default=False)
    gongbian_id = db.Column(db.Integer, db.ForeignKey('gongbian.id'))
    gongbian = db.relationship('Gongbian',back_populates = 'yonghus')



@app.cli.command()
@click.option('--drop',is_flag = True,help = 'Create after drop.')
def initdb(drop):
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')


@app.cli.command()
@click.option('--username', prompt=True, help='The username used to login.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.')
def admin(username, password):
    """Create user."""
    db.create_all()

    user = User.query.first()
    if user is not None:
        click.echo('Updating user...')
        user.username = username
        user.set_password(password)
    else:
        click.echo('Creating user...')
        user = User(username=username, name='Admin')
        user.set_password(password)
        db.session.add(user)

    db.session.commit()
    click.echo('Done.')


@app.cli.command()
def forge():
    db.create_all()
    name = '白工线'
    lines = [
        {'linename': '10KV白工线B月湖岩#00分之箱'},
        {'linename': '10KV白工线B月湖岩FD021刀闸（D02开关）'},
        {'linename': '#09杆'},
        {'linename': '#08杆'},
        {'linename': '#02杆'},
    ]
    kongzhis = [
        {'kzname' : '901间隔',
         'dengji' : 'one',
         'fushu_id' : '1',
         'line_id' : '1',
        },
        {
            'kzname': '911间隔',
            'dengji': 'one',
            'fushu_id': '2',
            'line_id': '1',
        },
        {
            'kzname': '10KV白工线月湖花园#01分支箱',
            'dengji': 'two',
            'fushu_id': '1',
            'line_id': '1',
        },
        {
            'kzname': '911间隔1',
            'dengji': 'two',
            'fushu_id': '1',
            'line_id': '1',
        },
        {
            'kzname': '10KV白工线创景金桂苑#02分支箱',
            'dengji': 'three',
            'fushu_id': '3',
            'line_id': '1',
        },
        {
            'kzname': '#01/#07杆',
            'dengji': 'three',
            'fushu_id': '4',
            'line_id': '1',
        }, ]
    b = {
            'gbname' : '创景白鹭湾#03公变',
            'beizhu' : '专变',
            'huhao' : '0206984223',
            'ronglang' : '630',
            'kongzhi_id' : '6',
        }

    taiqu = Taiqu(name=name)
    db.session.add(taiqu)
    for l in lines:
        line = Line(linename=l['linename'])
        taiqu.lines.append(line)
    for i in kongzhis:
        kongzhi = Kongzhi(kzname = i['kzname'],dengji= i['dengji'],fushu_id= i['fushu_id'],line_id= i['line_id'])
        db.session.add(kongzhi)
    gongbian = Gongbian(gbname=b['gbname'],beizhu=b['beizhu'],huhao=b['huhao'],ronglang= b['ronglang'],kongzhi_id=b['kongzhi_id'])
    db.session.add(gongbian)
    db.session.commit()
    click.echo('Done.')

@app.route('/')
def index():
    taiqus = Taiqu.query.all()
    return render_template('index.html',taiqus = taiqus)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))

        user = User.query.first()

        if username == user.username.decode() and user.validate_password(password):
            login_user(user)
            flash('Login success.')
            return redirect(url_for('index'))

        flash('Invalid username or password.')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Goodbye.')
    return redirect(url_for('index'))

@app.route('/taiqushow/<int:taiqu_id>',methods =['GET','POST'])#仅仅是控制1 的新增
def taiqushow(taiqu_id):

    if request.method == 'POST':
        name = request.form.get('name')
        line = request.form.get('line')
        taiqu = Taiqu.query.filter_by(name = name).first()#查询功能
        line = Line(linename = line)
        taiqu.lines.append(line)
        db.session.commit()
        flash('创建成功')
        return redirect(url_for('taiqushow'))
    taiqu = Taiqu.query.get(taiqu_id)
    lines = Line.query.all()
    return render_template('taiqushow.html',taiqu = taiqu,lines = lines )

@app.route('/edit/<int:line_id>',methods=['GET','POST'])
@login_required
def edit(line_id):
    line = Line.query.get_or_404(line_id)

    if request.method == 'POST':
        linename = request.form['linename']

        if not linename:
            flash('请输入文字')
            return redirect(url_for('edit',line_id = line_id))
        line.linename = linename
        db.session.commit()
        flash('更改成功')
        return redirect(url_for('index'))
    return render_template('edit.html',line = line)


@app.route('/delete/<int:line_id>',methods=['POST'])
@login_required
def delete(line_id):
    line = Line.query.get_or_404(line_id)
    db.session.delete(line)
    db.session.commit()
    flash('删除成功')
    return redirect(url_for('index'))

@app.route('/then/<int:line_id>')
@login_required
def then(line_id):
    line = Line.query.get_or_404(line_id)
    kongzhis = Kongzhi.query.with_parent(line).all()#返回这个线路有关的控制
    return render_template('then.html',line = line,kongzhis = kongzhis)

@app.route('/gongbian/<int:kongzhi_id>')
def gongbian(kongzhi_id):
    kongzhi = Kongzhi.query.get_or_404(kongzhi_id)
    gongbians = Gongbian.query.with_parent(kongzhi).all()
    return render_template('gongbian.html',kongzhi = kongzhi,gongbians =gongbians)

@app.route('/tingdian/<int:line_id>',methods=['POST'])#线路停电
def tingdian(line_id):
    lines = Line.query.filter(line_id >= line_id)
    for q in lines:
        q.zhuangtai = True
        kongzhis = Kongzhi.query.filter_by(line_id = q.id).all()
        for i in kongzhis:
            i.zhuangtai = True
            gongbians = Gongbian.query.filter_by(kongzhi_id = i.id).all()
            for j in gongbians:
                j.zhuangtai = True
                yonghus = Yonghu.query.filter_by(gongbian_id = j.id).all()
                for x in  yonghus:
                    x.zhuangtai = True
    db.session.commit()
    flash('停电保存成功')
    return redirect(url_for('index'))

@app.route('/tingdian1/<int:kongzhi_id>',methods=['POST'])#控制停电
def tingdian1(kongzhi_id):
    def yong(a):
        b = Yonghu.query.filter_by(gongbian_id = a).all()
        for c in b:
            c.zhuangtai = True
        db.session.commit()
    kongzhi = Kongzhi.query.get_or_404(kongzhi_id)
    if (kongzhi.dengji.decode() == 'one'):
        kongzhi.zhuangtai = True
        gongbians = Gongbian.query.filter_by(kongzhi_id=kongzhi_id).all()
        for z in gongbians :
            z.zhuangtai = True
            yong(z.id)
        kz2s = Kongzhi.query.filter_by(fushu_id = kongzhi_id).all()
        for i in kz2s:
            i.zhuangtai = True
            gongbians2 = Gongbian.query.filter_by(kongzhi_id=i.id).all()
            for x in gongbians2 :
                x.zhuangtai = True
                yong(x.id)
            kz3s = Kongzhi.query.filter_by(fushu_id = i.id).all()
            for j in kz3s:
                j.zhuangtai = True
                gongbians3 = Gongbian.query.filter_by(kongzhi_id=j.id).all()
                for y in gongbians3:
                    y.zhuangtai = True
                    yong(y.id)
    if (kongzhi.dengji.decode() == 'two'):
        kongzhi.zhuangtai = True
        gongbians2 = Gongbian.query.filter_by(kongzhi_id=kongzhi_id).all()
        for z in gongbians2 :
            z.zhuangtai = True
            yong(z.id)
        kz3s = Kongzhi.query.filter_by(fushu_id = kongzhi_id).all()
        for i in kz3s:
            i.zhuangtai = True
            gongbians3 = Gongbian.query.filter_by(kongzhi_id = i.id).all()
            for j in gongbians3:
                j.zhuangtai = True
                yong(j.id)
    if (kongzhi.dengji.decode() == 'three'):
        kongzhi.zhuangtai = True
        gongbians3 = Gongbian.query.filter_by(kongzhi_id = kongzhi_id).all()
        for i in gongbians3:
            i.zhuangtai = True
            yong(i.id)

    db.session.commit()
    flash('停电保存成功')
    return redirect(url_for('index'))


@app.route('/chaxun')#查询所有停电模块
def chaxun():
    taiqus = Taiqu.query.all()
    lines = Line.query.all()
    kongzhis = Kongzhi.query.all()
    gongbians = Gongbian.query.all()
    yonghus = Yonghu.query.all()
    tais = []
    line1 = []
    kongs = []
    gongs = []
    yongs = []
    for i in taiqus:
        if (i.zhuangtai):
            tais.append(i)
    for j in lines:
        if(j.zhuangtai):
            line1.append(j)
    for x in kongzhis:
        if(x.zhuangtai):
            kongs.append(x)
    for y in  gongbians:
        if(y.zhuangtai):
            gongs.append(y)
    for q in yonghus:
        if(q.zhuangtai):
            yongs.append(q)
    return render_template('chaxun.html', tais = tais, line1 = line1,kongs = kongs,gongs = gongs,yongs = yongs)

@app.route('/huifu')#查询所有停电模块,状态改未停电
def huifu():
    taiqus = Taiqu.query.all()
    lines = Line.query.all()
    kongzhis = Kongzhi.query.all()
    gongbians = Gongbian.query.all()
    yonghus = Yonghu.query.all()
    for i in taiqus:
        if (i.zhuangtai):
            i.zhuangtai = False
    for j in lines:
        if(j.zhuangtai):
            j.zhuangtai = False
    for x in kongzhis:
        if(x.zhuangtai):
            x.zhuangtai = False
    for y in  gongbians:
        if(y.zhuangtai):
            y.zhuangtai = False
    for q in  yonghus:
        if(q.zhuangtai):
            q.zhuangtai = False
    db.session.commit()
    flash('停电状态已全部恢复')
    return redirect(url_for('index'))


@app.route('/duanxinexcel/', methods=['GET', 'POST'])
def duanxinexcel():
    datalist = []
    headers = ("用户户号","用户名称", "用户地址", "用户电话号码","用户敏感度")
    yonghus = Yonghu.query.filter_by(zhuangtai = True).all()
    for i in yonghus:
        yonghu = (i.number.decode(),i.yhname.decode(), i.yhdizhi.decode(), i.telephone.decode(), i.minggandu)
        datalist.append(yonghu)
    data = tablib.Dataset(*datalist, headers=headers)
    resp = make_response(data.xls)
    filename = 'filename.xls'  # 用户下载默认文件名
    resp.headers["Content-Disposition"] = "attachment; filename=" + filename  # 指定响应为下载文件
    resp.headers['Content-Type'] = 'xls'  # 不指定的话会默认下载html格式，下载后还要改格式才能看
    return resp


@app.route('/yongshow/<int:gongbian_id>',methods=['GET', 'POST'])
def yongshow(gongbian_id):
    if request.method == 'POST':
        yhname = request.form.get('yhname')
        yhdizhi = request.form.get('yhdizhi')
        number = request.form.get('number')
        telephone = request.form.get('telephone')
        minggandu = request.form.get('minggandu')
        gongbian = Gongbian.query.get(gongbian_id)
        yonghu = Yonghu(yhname=yhname,yhdizhi=yhdizhi,number=number,telephone=telephone,minggandu=minggandu,gongbian_id=gongbian_id)
        gongbian.yonghus.append(yonghu)
        db.session.commit()
        flash('创建成功')
        return redirect(url_for('yongshow',gongbian_id = gongbian_id))
    gongbian = Gongbian.query.get(gongbian_id)
    yonghus = Yonghu.query.filter_by(gongbian_id = gongbian_id).all()
    return render_template('yongshow.html',gongbian = gongbian,yonghus = yonghus)

@app.route('/deleteyong/<int:yonghu_id>',methods=['POST'])
def deleteyong(yonghu_id):
    yonghu = Yonghu.query.get_or_404(yonghu_id)
    gongbian_id = yonghu.gongbian_id
    db.session.delete(yonghu)
    db.session.commit()
    flash('删除成功')
    return redirect(url_for('yongshow',gongbian_id=gongbian_id))


if __name__ == "__main__":
    app.run()