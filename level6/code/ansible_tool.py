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

def write_data(filepath,data):
    with open(filepath,'w') as f:
        f.write(data)
        f.close()