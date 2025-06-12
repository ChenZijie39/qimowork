from flask import Flask
from flask import render_template,request
import subprocess
 
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

app=Flask(__name__)

@app.route("/")
def index():
    return 'Hello,Ansible'

@app.route('/exec')
def exec_command():
    command=request.args.get('command')
    result=run_cmd(command)
    return result

if __name__=='__main__':
    app.run(host='0.0.0.0',debug=True)
else:
    application=app