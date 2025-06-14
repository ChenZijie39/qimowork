from flask import request,session,redirect,render_template,Blueprint,flash
from db import execute_sql,query_sql
from login_required import login_required

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.post('/login')
def login_page():
    username=request.form.get('username')
    password=request.form.get('password')
    result=query_sql('SELECT * FROM users WHERE username = ? and password=?', (username,password))
    if len(result)>0:
        print(result[0])
        session['username']=username
        session['is_super']=result[0][4]
        session['nickname']=result[0][3]
    return redirect('/')

@user_bp.route('/register',methods=['GET','POST'])
def register_page():
    if request.method=='GET':
        return render_template('user/register.html')
    if request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')
        nickname=request.form.get('nickname')
        result=query_sql('SELECT COUNT(*) FROM users WHERE username = ?', (username,))
        if result[0][0]>0:
            flash('用户已经存在', 'error')
            return redirect('/')    
        is_super='0'
        result=execute_sql('INSERT INTO users (username, password, nickname,is_super) VALUES (?, ?, ?,?)',
                    (username, password, nickname,is_super))
        session['username']=username
        session['is_super']=is_super
        session['nickname']=nickname
        return redirect('/')
    
@user_bp.route('/logout')
@login_required
def logout_page():
    if session.get('username'):
        del session['username']
    if session.get('nickname'):
        del session['nickname']
    if session.get('is_super'):
        del session['is_super']   
    return redirect('/')

@user_bp.get("/list")
@login_required
def user_page():
    if session.get('is_super')!=1:
        return redirect('/')
    result=query_sql('select * from users order by id desc')
    return render_template('user/list.html',users=result)

@user_bp.route('/delete')
@login_required
def user_delete_page():
    if session.get('is_super')!=1:
        return redirect('/')
    if request.method=='GET':
        user_id=request.args.get('id')    
        execute_sql("DELETE FROM users WHERE id = ?", (user_id,))
        return redirect('/user/list')

@user_bp.route('/update',methods=['GET','POST'])
@login_required
def user_update_page():
    if session.get('is_super')!=1:
        return redirect('/')
    if request.method=='GET':
        user_id=request.args.get('id')    
        result=query_sql('select * from users where id=? limit 1',(user_id,))
        print(result)
        return render_template('user/update.html',user=result[0])
    if request.method=='POST':
        data = request.form
        sql = f"UPDATE users SET nickname=?,is_super=?,password=?  WHERE id = ?"
        execute_sql(sql, (data['nickname'],data['is_super'],data['password'],data['id']))
        return redirect('/user/list')