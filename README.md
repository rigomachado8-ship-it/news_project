# News Project

## Overview
This is a Django and Django REST Framework news platform with role-based access for Readers, Journalists, and Editors.

The project includes:
- MariaDB database configuration
- Custom user roles
- Web registration and login
- Role-based article management
- Editor approval workflow
- Subscription features
- REST API endpoints with JWT authentication

---

## User Roles

### Reader
- Register and log in through the website
- View approved articles
- Subscribe to publishers
- Subscribe to journalists
- View subscribed articles

### Journalist
- Register and log in through the website
- Create articles
- Save drafts
- Submit articles for review
- Edit their own articles

### Editor
- Log in through the website
- Review pending articles
- Approve or reject submitted articles
- Create and edit articles

---

## Technology Stack
- Python
- Django
- Django REST Framework
- Simple JWT
- MariaDB

---

## Main Features
- Custom user model with role support
- Public approved article list
- Protected dashboard
- Web authentication system
- Editor approval workflow
- Subscription system
- API endpoints for article data
- JWT token endpoints for API authentication

---

## API Endpoints

### Authentication
- `POST /api/token/`
- `POST /api/token/refresh/`

### Articles
- `GET /api/articles/`
- `POST /api/articles/`
- `GET /api/articles/<id>/`
- `GET /api/articles/subscribed/`
- `GET /api/articles/pending/`

---

## Web Routes
- `/`
- `/register/`
- `/login/`
- `/logout/`
- `/dashboard/`
- `/create/`
- `/editor/approve/`
- `/subscriptions/`
- `/subscriptions/articles/`

---

## Code Quality

This project follows Python best practices and coding standards:

- Code formatted using **Black**
- PEP8 compliance verified using **Flake8**
- All modules, classes, and functions include **docstrings**
- Clean and maintainable code structure

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/rigomachado8-ship-it/news_project.git
cd news_project/news_project

#Author
#Rodrigo Machado