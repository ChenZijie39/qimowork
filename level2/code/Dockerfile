FROM python:3.8.7

LABEL Author=Stars

WORKDIR /home/project

COPY . .

RUN python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple && \
 pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ -r requirements.txt

ENTRYPOINT ["python","app.py"]