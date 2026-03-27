# 📌 News Project – Requirements Document

## 1. Introduction

This document outlines the functional and non-functional requirements for the News Project web application. The system allows users to create, manage, and consume news articles based on their assigned roles: Reader, Journalist, and Editor.

---

## 2. Functional Requirements

### 2.1 User Authentication

* Users must be able to register through a web interface.
* Users must be able to log in and log out securely.
* Users are assigned a role during registration (Reader, Journalist, Editor).

---

### 2.2 User Roles and Permissions

#### Reader

* View all approved articles.
* Subscribe to publishers.
* Subscribe to journalists.
* View subscribed articles.
* Manage personal subscriptions.

#### Journalist

* Create new articles.
* Edit their own articles.
* Submit articles as draft or pending review.
* View their own articles on the dashboard.

#### Editor

* View all articles, including pending ones.
* Approve or reject submitted articles.
* Edit any article.
* Publish approved content.

---

### 2.3 Article Management

* Articles must include:

  * Title
  * Content
  * Author
  * Publisher (optional)
  * Newsletter (optional)
  * Status (Draft, Pending, Approved, Rejected)
* Only approved articles are visible to the public.
* Journalists cannot self-approve articles.
* Editors can approve or reject articles.

---

### 2.4 Subscription System

* Users can subscribe to:

  * Publishers
  * Journalists
* Users can view a list of their subscriptions.
* Users can view articles from subscribed sources.

---

### 2.5 Dashboard

* Logged-in users are redirected to a dashboard.
* Dashboard displays:

  * User role
  * Personal articles (for journalists/editors)
  * Pending articles (for editors)

---

### 2.6 API Functionality

* Provide API endpoints for:

  * Listing articles
  * Viewing article details
  * Creating articles (authorized users only)
  * Viewing subscribed articles
  * Viewing pending articles (editor only)

---

## 3. Non-Functional Requirements

### 3.1 Performance

* The system should handle multiple users accessing articles simultaneously.
* Database queries should be optimized using relationships and filtering.

---

### 3.2 Security

* Authentication must be required for protected actions.
* Role-based permissions must be enforced.
* Passwords must be securely hashed.
* Unauthorized users must be redirected to the login page.

---

### 3.3 Usability

* The interface should be simple and easy to navigate.
* Navigation links should be clearly visible.
* Forms should be user-friendly and intuitive.

---

### 3.4 Reliability

* The system should not crash on invalid input.
* Error messages should guide users appropriately.

---

### 3.5 Maintainability

* Code should follow Django best practices.
* Code should follow PEP 8 styling guidelines.
* Views should include comments explaining logic.

---

### 3.6 Scalability

* The application uses MariaDB for better scalability and relational data handling.
* The database structure supports many-to-many relationships for subscriptions.

---

## 4. Assumptions

* Users have internet access and a modern web browser.
* MariaDB is installed and configured properly.
* The application runs in a development or production environment with Django configured.

---

## 5. Future Improvements

* Add search functionality for articles.
* Add user profile pages.
* Implement notifications for new articles.
* Improve UI styling with CSS frameworks.
* Add pagination for large datasets.

---
