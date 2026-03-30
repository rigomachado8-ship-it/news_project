# News Project

## Overview
This is a Django and Django REST Framework news platform with role-based access for Readers, Journalists, and Editors.

The application allows:
- Journalists to create and submit articles
- Editors to review and approve articles
- Readers to view approved articles and subscribe to content
- Articles to be exposed via a REST API

---

## Features

- Custom user model with role-based access
- Groups and permissions (Reader, Journalist, Editor)
- Article creation and approval workflow
- Subscription system (publishers and journalists)
- REST API with role-based authorization
- JWT authentication for API access
- MariaDB/MySQL database integration

---

## Technology Stack

- Python
- Django
- Django REST Framework
- Simple JWT (authentication)
- MariaDB / MySQL

---

## User Roles

### Reader
- View approved articles
- Subscribe to publishers and journalists
- View subscribed content

### Journalist
- Create and edit articles
- Submit articles for review
- Manage newsletters

### Editor
- Review submitted articles
- Approve or reject articles
- Manage content

---

## REST API Design

### Endpoints

- `GET /api/articles/`  
  Returns all approved articles

- `GET /api/articles/subscribed/`  
  Returns articles from subscribed publishers/journalists

- `GET /api/articles/<id>/`  
  Retrieve a single article

- `POST /api/articles/`  
  Create article (Journalists only)

- `PUT /api/articles/<id>/`  
  Update article (Editors/Journalists)

- `DELETE /api/articles/<id>/`  
  Delete article (Editors/Journalists)

---

### Authentication

- JWT token authentication
- `POST /api/token/`
- `POST /api/token/refresh/`

---

### Authorization

- Reader: read-only access
- Journalist: create/update/delete own content
- Editor: approve, update, delete articles

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/rigomachado8-ship-it/news_project.git
cd news_project

#Author
#Rodrigo Machado