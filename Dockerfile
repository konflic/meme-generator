FROM python:3.9-slim

WORKDIR /bot

RUN apt update
RUN apt install git -y

COPY requirements.txt .

RUN pip install -U pip
RUN pip install -r requirements.txt

COPY . .

RUN ls -la

CMD ["python", "bot.py"]
