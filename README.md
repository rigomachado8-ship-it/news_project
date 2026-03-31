# 📰 News Project

A Django-based news publishing platform that supports role-based access for Readers, Journalists, and Editors.

Users can create, manage, review, and subscribe to articles, publishers, and newsletters.

---

## 📌 Features

### 👤 User Roles

* **Reader**

  * View approved articles
  * Subscribe to articles, publishers, and journalists

* **Journalist**

  * Create, edit, and delete their own articles (only before approval)
  * Submit articles for review

* **Editor**

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

* Python 3.x
* Django
* Django REST Framework
* MariaDB / MySQL
* HTML (Django Templates)

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/rigomachado8-ship-it/news_project.git
cd news_project
```

---

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate     # Windows
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🗄️ Database Setup (MariaDB/MySQL)

### 4️⃣ Open MySQL

```bash
mysql -u root -p
```

---

### 5️⃣ Create Database

```sql
CREATE DATABASE news_project_db;
```

If it already exists, ignore the error.

---

### 6️⃣ Exit MySQL

```sql
EXIT;
```

---

### 7️⃣ Set Environment Variables

Mac/Linux:

```bash
export DB_NAME=news_project_db
export DB_USER=root
export DB_PASSWORD=yourpassword
export DB_HOST=localhost
export DB_PORT=3306
```

---

### 8️⃣ Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

### 9️⃣ Create Superuser

```bash
python manage.py createsuperuser
```

---

### 🔟 Run the Server

```bash
python manage.py runserver
```

Open:

```
http://127.0.0.1:8000/
```

---

## 🏗️ System Design Overview

The application follows Django’s Model-View-Template architecture:

* **Models:** Define entities (Article, User, Publisher, Newsletter)
* **Views:** Handle logic and enforce permissions
* **Templates:** Render UI
* **API:** Built with Django REST Framework

---

## 🔐 Permission Design

* Journalists:

  * Manage their own articles
  * Can delete only before approval

* Editors:

  * Approve/reject content
  * Manage all users and data

* Users:

  * Can manage their own profiles only

---

## 🧯 Troubleshooting

### MySQL Access Denied

Ensure DB_PASSWORD is correct and environment variables are set.

### Database Already Exists

Safe to ignore.

----
## Planning Documents
All planning documents required for the capstone are in the `Planning/` folder, including:
- functional and non-functional requirements
- UI/UX planning
- database normalization
- ERD
- API planning
- testing plan

---

## 📂 Project Structure

```
news_project/
├── newsapp/
├── Planning/
├── screenshots/
├── manage.py
└── requirements.txt
```

---

## 👨‍💻 Author

Rodrigo Machado
