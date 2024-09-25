FROM python:3.9

WORKDIR /workspace

COPY ./ ./

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

#COPY . .

EXPOSE 5000

CMD ["python3.9", "main.py"]
