from flask import Flask
from flask import render_template,request,jsonify
import subprocess
import json
 
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

if __name__=='__main__':
    app.run(host='0.0.0.0',debug=True)
else:
    application=app