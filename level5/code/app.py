from flask import Flask
from flask import render_template,request,jsonify,redirect
import subprocess
import json
import sqlite3
import os
import math

def run_cmd(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            output = result.stdout.strip()
            print(output)
        else:
            output = result.stderr.strip()
            print(output)
    except Exception as e:
        output = str(e)
    return output

def write_data(filepath,data):
    with open(filepath,'w') as f:
        f.write(data)
        f.close()

app=Flask(__name__)
DATABASE = 'metrics.db'
# 初始化数据库
def init_db():
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hostname TEXT NOT NULL,
                ip TEXT NOT NULL,
                status TEXT NOT NULL,
                total_memory INTEGER NOT NULL,
                used_memory INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        c.execute('''
            CREATE TABLE hosts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip TEXT NOT NULL,
                ansible_ssh_port TEXT NOT NULL,
                ansible_ssh_pass TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

def execute_sql(sql, params=()):
    """执行 SQL 语句并返回受影响行数"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return cursor.rowcount


def query_sql(sql, params=()):
    """执行查询并返回结果"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        return cursor.fetchall()
    
@app.route("/",methods=['GET','POST'])
def index():
    if request.method=='GET':
        return render_template('index.html')
    if request.method=='POST':
        ip=request.form.get('ip')
        port=request.form.get('port')
        password=request.form.get('password')
        playbook=request.form.get('playbook')
        filename='/tmp/%s_playbook.yml'%ip
        write_data(filename,playbook)
        json_data={"ip":ip,'ansible_ssh_port':port,'ansible_ssh_pass':password}
        json_str=json.dumps(json_data,indent=4)
        host_data_filename='/tmp/%s_host.json'%ip
        write_data(host_data_filename,json_str)
        command="/usr/local/bin/ansible-playbook --ssh-extra-args='-o StrictHostKeyChecking=no'  --inventory="+ip+", --extra-vars=@"+host_data_filename+" "+filename
        result=run_cmd(command)
        return jsonify({"command":command,'result':result})

@app.route('/exec')
def exec_command():
    command=request.args.get('command')
    result=run_cmd(command)
    return result

@app.route('/board')
def board_page():
    if request.method=='GET':
        return render_template('board.html')

@app.route('/collect')
def collect_page():
    device_list=[]
    result=query_sql('select ip,ansible_ssh_port,ansible_ssh_pass from hosts')
    for item in result:
        device_list.append({
            'ip':item[0],
            'ansible_ssh_port':item[1],
            'ansible_ssh_pass':item[2]
        })
    play_book_path='/home/project/play_book.yml'
    data=[]
    for item in device_list:
        json_str=json.dumps(item,indent=4)
        host_data_filename='/tmp/%s_host.json'%item['ip']
        write_data(host_data_filename,json_str)
        command="/usr/local/bin/ansible-playbook --ssh-extra-args='-o StrictHostKeyChecking=no'  --inventory="+item['ip']+", --extra-vars=@"+host_data_filename+" "+play_book_path
        data.append({
            'ip':item['ip'],
            'result':run_cmd(command)
        })
    return jsonify({'code':'0','msg':'发送采集任务成功','data':data})

@app.route('/status',methods=['GET','POST'])
def status_page():
    if request.method=='GET':
        query = """
        SELECT m.* 
        FROM metrics m
        INNER JOIN (
            SELECT 
                hostname, 
                MAX(timestamp) AS max_ts
            FROM metrics
            GROUP BY hostname
        ) sub ON m.hostname = sub.hostname 
               AND m.timestamp = sub.max_ts
        """
        results=query_sql(query)
        devices = []
        for item in results:
            devices.append({
                'id':item[0],
                'ip':item[2],
                'name':item[1],
                'status':item[3],
                'total_memory':item[4],
                'used_memory':item[5],
                'timestamp':item[6],
                'mem_percent': math.floor(item[5]*100/item[4])
            })
        return jsonify({'code':0,'data':devices})
    
    if request.method=='POST':
        data = request.json   
        execute_sql('''
            INSERT INTO metrics (hostname, ip,status, total_memory, used_memory)
            VALUES (?, ?,?, ?, ?)
        ''', (data['hostname'], data['ip'],data['status'], data['total_memory'], data['used_memory']))
        return jsonify({"status": "success"})

@app.route('/host')
def host_page():
    if request.method=='GET':
        query = """
        SELECT * from hosts order by id desc
        """
        hosts=query_sql(query)
        return render_template('host.html',hosts=hosts)

@app.route('/host_add',methods=['GET','POST'])
def host_add_page():
    if request.method=='GET':
        return render_template('host_add.html')
    if request.method=='POST':
        data = request.form
        execute_sql(
                "INSERT INTO hosts (ip, ansible_ssh_port, ansible_ssh_pass) VALUES (?, ?, ?)",
                (data['ip'], data['ansible_ssh_port'], data['ansible_ssh_pass'])
        )
        
        return redirect('/host')

@app.route('/host_update',methods=['GET','POST'])
def host_update_page():
    if request.method=='GET':
        host_id=request.args.get('id')    
        result=query_sql('select * from hosts where id=? limit 1',(host_id,))
        return render_template('host_update.html',host=result[0])
    if request.method=='POST':
        data = request.form
        sql = f"UPDATE hosts SET ip=?,ansible_ssh_port=?,ansible_ssh_pass=?  WHERE id = ?"
        execute_sql(sql, (data['ip'],data['ansible_ssh_port'],data['ansible_ssh_pass'],data['id']))
        return redirect('/host')

@app.route('/host_delete')
def host_delete_page():
    if request.method=='GET':
        host_id=request.args.get('id')    
        execute_sql("DELETE FROM hosts WHERE id = ?", (host_id,))
        return redirect('/host')

if __name__=='__main__':
    init_db()
    app.run(host='0.0.0.0',debug=True)
else:
    application=app