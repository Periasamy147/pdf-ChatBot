FROM python:3.8

WORKDIR /app

COPY . /app

RUN pip install nltk flask

CMD ["python", "Untitled-1.py"]

