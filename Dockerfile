FROM python:3.12

WORKDIR /TgApp2011

COPY requirements.txt .
COPY ./ .


RUN pip install -r requirements.txt

CMD ["python", "./main.py"]
