FROM ubuntu:20.04

LABEL Author=Stars

WORKDIR /home/project

COPY . .
RUN sed -i "s/archive.ubuntu.com/mirrors.aliyun.com/g" /etc/apt/sources.list && \
 apt-get update && apt-get install vim python3 python3-pip sshpass ansible -y

RUN python3 -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple && \
 pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple/ -r requirements.txt

ENTRYPOINT ["python3","app.py"]