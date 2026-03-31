# Functional Requirements

## Overview
This application is a Django-based News Platform that allows Readers, Journalists, and Editors to interact with articles, newsletters, and subscriptions.

---

## User Roles & Capabilities

### Reader
- Register and log in
- View approved articles
- View newsletters
- Subscribe to:
  - Publishers
  - Journalists
- View articles from subscriptions

---

### Journalist
- Register and log in
- Create articles
- Edit their own articles
- Delete their own articles
- Create newsletters
- Add articles to newsletters
- Submit articles for approval

---

### Editor
- Register and log in
- View all submitted articles
- Approve or reject articles
- Edit any article
- Delete any article
- Manage newsletters

---

## Article Management
- Create article with:
  - Title
  - Content
  - Author
  - Publisher (optional)
  - Created date
  - Approval status
- Articles must be approved before public visibility

---

## Newsletter Management
- Create newsletters
- Add/remove articles
- View newsletters
- Link newsletters to journalists

---

## Subscription System
- Readers can subscribe to:
  - Publishers
  - Journalists
- System filters articles based on subscriptions

---

## Notifications
- When an article is approved:
  - Email is sent to subscribers
  - Article is posted to external API (e.g., X/Twitter)

---

## Authentication & Authorization
- JWT-based authentication
- Role-based access control:
  - Readers: read-only
  - Journalists: create/edit own content
  - Editors: full control

---

## REST API Features
- Retrieve all approved articles
- Retrieve subscribed articles
- Create/update/delete articles
- Token authentication endpoints