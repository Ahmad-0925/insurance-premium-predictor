FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --retries 5 --timeout 300 -r requirements.txt

COPY . /app

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]