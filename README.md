# 📰 News Project

## 🔗 Repository

https://github.com/rigomachado8-ship-it/news_project

---

## 📖 Overview

A full-stack Django news publishing platform with role-based access, REST API support, Sphinx documentation, and Docker containerization.

Users can create, manage, review, and subscribe to articles, publishers, and newsletters.

---

## 📌 Features

### 👤 User Roles

**Reader**

* View approved articles
* Subscribe to articles, publishers, and journalists

**Journalist**

* Create, edit, and delete their own articles (before approval)
* Submit articles for review

**Editor**

* Approve or reject articles
* Manage all content
* Create publishers and newsletters
* Manage user profiles

---

### 📰 Article Management

* Create, edit, delete articles
* Approval workflow (Draft → Pending → Approved/Rejected)
* Email notifications to subscribers when approved

---

### 👤 Profile Management (CRUD)

* View profile
* Edit profile
* Delete profile
* Role-based permissions enforced

---

### 🏢 Publisher & Newsletter

* Editors create publishers
* Editors & journalists create newsletters
* Articles linked to publishers/newsletters

---

### 🔐 Permissions

* Journalists can only delete their own articles before approval
* Editors can manage all content
* Users can only manage their own profiles (unless editor)

---

## 🛠️ Tech Stack

* Python 3
* Django
* Django REST Framework
* **MariaDB / MySQL (production-ready database)**
* Docker
* Sphinx
* HTML (Django Templates)

---

## ⚙️ Installation & Setup (Local Development)

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/rigomachado8-ship-it/news_project.git
cd news_project
```

---

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
# OR
venv\Scripts\activate      # Windows
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Configure Environment Variables

Create a `.env` file in the project root:

```env
DJANGO_SECRET_KEY=django-insecure-change-me-before-production
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=news_project_db
DB_USER=news_user
DB_PASSWORD=news_password
DB_HOST=127.0.0.1
DB_PORT=3306
```

---

### 5️⃣ Apply Migrations

```bash
python manage.py migrate
```

---

### 6️⃣ Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

---

### 7️⃣ Run the Server

```bash
python manage.py runserver
```

Open:

```
http://127.0.0.1:8000/
```

---

## 🔌 API Documentation & Usage

### Base URL

```
http://127.0.0.1:8000/
```

---

### 🔐 Authentication (JWT)

#### Get Token

```http
POST /api/token/
```

Request:

```json
{
  "username": "your_username",
  "password": "your_password"
}
```

Response:

```json
{
  "refresh": "refresh_token",
  "access": "access_token"
}
```

---

#### Refresh Token

```http
POST /api/token/refresh/
```

---

### 🔑 Authorization Header

```
Authorization: Bearer your_access_token
```

---

## 📡 API Endpoints

### Articles

#### Get all articles

```http
GET /api/articles/
```

#### Create article

```http
POST /api/articles/
```

Example:

```json
{
  "title": "Breaking News",
  "content": "Article content",
  "publisher_id": 1,
  "newsletter_id": 1,
  "status": "draft"
}
```

---

#### Get single article

```http
GET /api/articles/<id>/
```

---

#### Subscribed articles

```http
GET /api/articles/subscribed/
```

---

#### Pending articles (Editor only)

```http
GET /api/articles/pending/
```

---

### Profiles

```http
GET /api/profiles/<id>/
```

---

## 🧪 Testing the API

### Using curl

#### Get token

```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
-H "Content-Type: application/json" \
-d '{"username":"your_username","password":"your_password"}'
```

---

#### Get articles

```bash
curl http://127.0.0.1:8000/api/articles/
```

---

#### Create article

```bash
curl -X POST http://127.0.0.1:8000/api/articles/ \
-H "Authorization: Bearer your_access_token" \
-H "Content-Type: application/json" \
-d '{"title":"Test","content":"Body","status":"draft"}'
```

---

## 🐳 Run with Docker

```bash
docker build -t news_project .
docker run -p 8000:8000 news_project
```

---

## 📚 Documentation (Sphinx)

```bash
cd docs
sphinx-build -b html source build/html
```

Open:

```
docs/build/html/index.html
```

---

## 📸 Screenshots

Located in `screenshots/`

---

## 📂 Project Structure

```
news_project/
├── docs/
├── newsapp/
├── Planning/
├── screenshots/
├── manage.py
├── requirements.txt
├── Dockerfile
```

---

## 👨‍💻 Author

Rodrigo Machado
