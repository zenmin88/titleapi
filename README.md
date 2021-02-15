# Overview

The api collects user review on titles. The titles are divided into categories: "Books", "Films", etc. Users can leave reviews on titles and rate them. Users can leave comments on reviews. 

# Getting started

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
You can then visit [localhost:8000/redoc](http://localhost:8000/redoc) to verify that it's running on your machine and read full API documentation for it.
