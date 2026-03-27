# 📰 News Publishing Platform (Django + DRF)

## 📌 Overview

This project is a full-stack News Publishing Platform built using Django and Django REST Framework.

It allows users to create, review, and publish articles through a role-based workflow system.

---

## 🚀 Key Features

### 👤 User Roles

* Reader → View approved articles
* Journalist → Create articles
* Editor → Approves articles

---

### 📰 Article Workflow

1. Journalist creates article
2. Article is NOT approved by default
3. Editor reviews article
4. Editor clicks Approve
5. Article appears in approved list

---

## 🔐 Authentication

JWT Authentication using SimpleJWT

### Get Token

POST /api/token/

Request:
{
"username": "your_username",
"password": "your_password"
}

Use Token:
Authorization: Bearer YOUR_ACCESS_TOKEN

---

## 📡 API Endpoints

### Articles

GET /api/articles/ → List all articles
POST /api/articles/ → Create article
GET /api/articles/<id>/ → Article detail

---

### Subscribed Articles

GET /api/articles/subscribed/

---

### Authentication

POST /api/token/ → Get JWT token

---

## 🖥️ UI Features (IMPORTANT)

This project includes full Django frontend pages:

* Register Page
* Login Page
* Create Article Page
* Approved Articles List
* Article Detail Page
* Editor Approval Dashboard

This demonstrates full-stack functionality (not API only)

---

## 📸 Screenshots

Located in /screenshots/

### UI Screens

* register_page.png
* login_page.png
* create_article_page.png
* article_created_success.png
* editor_approve_view.png
* approved_articles_view.png
* article_detail_page.png

### API Screens

* article_list_api.png
* article_detail_api.png
* create_article_api.png
* subscribed_articles_api.png
* token_obtain_api.png

### Admin

* user_role_admin.png

---

## 🧱 Project Structure

news_project/
│
├── news_project/
│   ├── settings.py
│   ├── urls.py
│
├── newsapp/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── urls.py
│   ├── templates/
│
├── screenshots/
├── manage.py
├── requirements.txt
├── README.md

---

## ⚙️ Setup Instructions

git clone https://github.com/rigomachado8-ship-it/news_project.git
cd news_project

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

---

## 🧪 Testing

Tools used:

* Thunder Client (VS Code)
* Browser (for UI + GET endpoints)

---

## ✅ Submission Checklist

✔ REST API implemented
✔ JWT Authentication working
✔ Role-based permissions
✔ UI pages implemented
✔ Article approval workflow
✔ Screenshots included
✔ Project runs successfully

---

## 👨‍💻 Author

Rodrigo Machado

---

## 🎉 Status

✅ Final Submission — Complete & Fully Functional
