FROM python:3.8-slim

# set workdir
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
COPY ./requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# copy project
COPY . /usr/src/app

# migrate
RUN python manage.py migrate

# loaddata from fixtures
RUN python manage.py loaddata api_board/fixtures/api_board.json

# adding port
EXPOSE 5000

# run project
CMD ["python", "manage.py", "runserver", "127.0.0.1:5000"]
