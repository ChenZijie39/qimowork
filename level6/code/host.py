from flask import request,render_template,redirect
from flask import Blueprint
from db import execute_sql,query_sql
from login_required import login_required

host_bp = Blueprint('host', __name__, url_prefix='/host')

@host_bp.route('/list')
@login_required
def host_page():
    if request.method=='GET':
        query = """
        SELECT * from hosts order by id desc
        """
        hosts=query_sql(query)
        return render_template('host/list.html',hosts=hosts)

@host_bp.route('/add',methods=['GET','POST'])
@login_required
def host_add_page():
    if request.method=='GET':
        return render_template('host/add.html')
    if request.method=='POST':
        data = request.form
        execute_sql(
                "INSERT INTO hosts (ip, ansible_ssh_port, ansible_ssh_pass) VALUES (?, ?, ?)",
                (data['ip'], data['ansible_ssh_port'], data['ansible_ssh_pass'])
        )
        
        return redirect('/host/list')

@host_bp.route('/update',methods=['GET','POST'])
@login_required
def host_update_page():
    if request.method=='GET':
        host_id=request.args.get('id')    
        result=query_sql('select * from hosts where id=? limit 1',(host_id,))
        return render_template('host/update.html',host=result[0])
    if request.method=='POST':
        data = request.form
        sql = f"UPDATE hosts SET ip=?,ansible_ssh_port=?,ansible_ssh_pass=?  WHERE id = ?"
        execute_sql(sql, (data['ip'],data['ansible_ssh_port'],data['ansible_ssh_pass'],data['id']))
        return redirect('/host/list')

@host_bp.route('/delete')
@login_required
def host_delete_page():
    if request.method=='GET':
        host_id=request.args.get('id')    
        execute_sql("DELETE FROM hosts WHERE id = ?", (host_id,))
        return redirect('/host/list')