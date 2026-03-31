# API Design

## Base URL
/api/

---

## Authentication

### POST /api/token/
- Obtain JWT token

### POST /api/token/refresh/
- Refresh token

---

## Articles

### GET /api/articles/
- Retrieve all approved articles

### GET /api/articles/<id>/
- Retrieve single article

### GET /api/articles/subscribed/
- Retrieve articles based on user subscriptions

### POST /api/articles/
- Create article (Journalists only)

### PUT /api/articles/<id>/
- Update article (Journalists/Editors)

### DELETE /api/articles/<id>/
- Delete article (Journalists/Editors)

---

## Permissions

| Role       | Permissions |
|------------|------------|
| Reader     | Read only  |
| Journalist | CRUD own   |
| Editor     | Full CRUD + approve |

---

## Response Format

```json
{
  "id": 1,
  "title": "Article Title",
  "content": "Content...",
  "author": "username",
  "approved": true
}