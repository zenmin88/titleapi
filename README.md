# Overview

The api collects user review on titles. The titles are divided into categories: "Books", "Films", etc. Users can leave reviews on titles and rate them. Users can leave comments on reviews. 

# Getting started with virtualenv

Please follow the instructions below.


Run manually:
```bash
git clone REPO
cd REPO
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata api_board
python manage.py runserver
```

# Getting started with docker

Please follow the instructions below.

Run manually:
```bash
git clone REPO
cd REPO
docker build -t api-image .
docker run --rm --name api-container --network host api-image
```

You can then visit [localhost:5000](http://localhost:5000) to verify that it's running on your machine and read full API documentation for it.