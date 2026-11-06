FROM python:3.13-slim
WORKDIR /app
RUN useradd -r -u 1000 app && mkdir /data && chown app /data
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY static ./static
COPY templates ./templates
COPY app.py preview.py models.py backup.py mail.py ./
USER app
EXPOSE 8000
CMD ["gunicorn", "-b", "0.0.0.0:8000", "--timeout", "120", "app:app"]
