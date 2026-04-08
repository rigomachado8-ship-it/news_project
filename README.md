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

* Create, edit, and delete their own articles (only before approval)
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

* Editors can create publishers
* Editors & journalists can create newsletters
* Articles can be linked to publishers/newsletters

---

### 🔐 Permissions

* Journalists can only delete their own articles **before approval**
* Editors can manage all content
* Users can only manage their own profiles (unless editor)

---

## 🛠️ Tech Stack

* Python 3
* Django
* Django REST Framework
* SQLite
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

### 4️⃣ Apply Migrations

```bash
python manage.py migrate
```

---

### 5️⃣ Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

---

### 6️⃣ Run the Server

```bash
python manage.py runserver
```

Open:

```
http://127.0.0.1:8000/
```

---

## 🐳 Run with Docker

### 1️⃣ Build the Docker Image

```bash
docker build -t news_project .
```

---

### 2️⃣ Run the Container

```bash
docker run -p 8000:8000 news_project
```

If port 8000 is already in use:

```bash
docker run -p 8001:8000 news_project
```

Open:

```
http://127.0.0.1:8000/
```

---

## 📚 Documentation (Sphinx)

Documentation is located in the `docs/` folder.

To rebuild documentation:

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

Screenshots of the application can be found in the `screenshots/` folder.

---

## 🌿 Git Branches

* `main` → final merged project
* `docs` → Sphinx documentation
* `container` → Docker setup

---

## 🏗️ System Design Overview

The application follows Django’s Model-View-Template architecture:

* **Models:** Define entities (Article, User, Publisher, Newsletter)
* **Views:** Handle logic and enforce permissions
* **Templates:** Render UI
* **API:** Built with Django REST Framework

---

## 📂 Planning Documents

All planning documents required for the capstone are in the `Planning/` folder, including:

* Functional and non-functional requirements
* UI/UX planning
* Database normalization
* ERD
* API planning
* Testing plan

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
