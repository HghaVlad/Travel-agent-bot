
FROM joyzoursky/python-chromedriver:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY . .
ENV DATABASE_URL=postgresql://user:password@db:5432/database_name
ENV REDIS_URL=redis://redis:6379/0

CMD ["python3", "bot.py"]
