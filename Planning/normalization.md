# Database Normalization

## Overview
The database is normalized to Third Normal Form (3NF) to eliminate redundancy and ensure data integrity.

---

## First Normal Form (1NF)
- All fields contain atomic values
- No repeating groups

Example:
- Articles stored individually
- No multiple values in a single column

---

## Second Normal Form (2NF)
- All non-key attributes depend on the primary key

Example:
- Article attributes depend only on Article ID

---

## Third Normal Form (3NF)
- No transitive dependencies

Example:
- Publisher details stored separately
- User roles stored separately

---

## Tables

### User
- id (PK)
- username
- password
- role

### Article
- id (PK)
- title
- content
- author (FK)
- publisher (FK)
- approved
- created_at

### Publisher
- id (PK)
- name

### Newsletter
- id (PK)
- title
- description
- author (FK)

### Subscriptions
- reader_id (FK)
- journalist_id (FK)
- publisher_id (FK)

---

## Benefits
- Reduces duplication
- Improves consistency
- Enhances performance