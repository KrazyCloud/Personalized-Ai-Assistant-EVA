FROM python:latest
WORKDIR /usr/app/src
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "flask_app.py"]
