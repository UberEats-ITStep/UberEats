<div align="center">

# UberEats Clone

### Modern Food Delivery Platform built with Django & React

A full-stack food delivery platform focused on scalable architecture, clean code, modern development practices, and future AI-powered features.

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=UberEats-ITStep_UberEats&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=UberEats-ITStep_UberEats)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=UberEats-ITStep_UberEats&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=UberEats-ITStep_UberEats)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=UberEats-ITStep_UberEats&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=UberEats-ITStep_UberEats)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=UberEats-ITStep_UberEats&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=UberEats-ITStep_UberEats)

[![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=green)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/DRF-A30000?style=for-the-badge&logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-B73BFE?style=for-the-badge&logo=vite&logoColor=FFD62E)](https://vitejs.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)

</div>

---

# Project Overview

**UberEats Clone** is a modern full-stack food delivery platform inspired by Uber Eats.

The project emphasizes scalable backend architecture, clean REST API design, secure authentication, modern frontend development, collaborative workflows, and maintainable code. It is being developed using professional engineering practices such as pull requests, code reviews, static code analysis, and feature-based development.

The long-term vision is to evolve the platform with AI-powered recommendation systems while maintaining a solid software architecture.

---

# Core Features

### Authentication

- JWT Authentication
- User Registration
- User Login
- User Profile
- Role-Based Access Control

### Restaurant System

- Restaurant Catalogue
- Categories
- Menu Items
- Restaurant Details

### Ordering

- Shopping Cart
- Checkout
- Orders
- Order History

### User Roles

- Client
- Courier
- Administrator

---

# Future Vision

The architecture is intentionally designed to support future expansion.

Planned features include:

- AI-powered restaurant recommendations
- AI-powered menu recommendations
- Personalized recommendations based on order history
- Recommendation explanations
- Recommendation logging
- Interactive delivery maps
- Courier dashboard
- Restaurant management dashboard
- Payment integration
- Real-time notifications

---

# Architecture

The project follows a **Monorepo** architecture.

```text
Repository
│
├── backend/     Django REST API
├── frontend/    React Application
└── README.md
```

### Backend

- Django 6
- Django REST Framework
- PostgreSQL
- SimpleJWT
- python-dotenv

Responsible for:

- Business Logic
- Authentication
- Database
- REST API
- Authorization & Permissions

### Frontend

- React 19
- TypeScript
- Vite
- Tailwind CSS
- Axios
- React Router

Responsible for:

- User Interface
- State Management
- API Communication
- Routing

---

# Technology Stack

| Technology | Purpose |
|------------|---------|
| Django 6 | Backend Framework |
| Django REST Framework | REST API |
| PostgreSQL | Relational Database |
| SimpleJWT | JWT Authentication |
| React 19 | Frontend Framework |
| TypeScript | Static Typing |
| Vite | Frontend Build Tool |
| Tailwind CSS | UI Styling |
| Axios | HTTP Client |

---

# Development Tools

| Tool | Purpose |
|------|---------|
| Git | Version Control |
| GitHub | Repository Hosting |
| Trello | Project Management |
| SonarCloud | Static Code Analysis & Quality Gates |
| Swagger / OpenAPI | API Documentation |

---

# Code Quality

The project uses **SonarCloud** to continuously monitor and improve code quality.

Static analysis includes:

- Code Quality Gates
- Maintainability Analysis
- Reliability Analysis
- Security Analysis
- Code Smell Detection
- Technical Debt Monitoring

Every Pull Request should satisfy the configured Quality Gate before being merged into the `dev` branch.

---

# Repository Structure

```text
ubereats-clone/
│
├── backend/
│   ├── config/
│   ├── restaurants/
│   ├── users/
│   ├── manage.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── context/
│   │   ├── features/
│   │   ├── hooks/
│   │   ├── layouts/
│   │   ├── pages/
│   │   ├── routes/
│   │   ├── types/
│   │   └── utils/
│   └── vite.config.ts
│
└── README.md
```

---

# Database Overview

The application uses **PostgreSQL** with a normalized relational schema.

Current entities include:

- User
- Profile
- Restaurant
- Category
- MenuItem

Upcoming entities include:

- Cart
- CartItem
- Order
- OrderItem
- Favorites
- Reviews
- RecommendationLog

The database is designed to support scalable business logic, efficient querying, and future AI-driven features.

---

# API Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register/` | POST | Register a new user |
| `/api/auth/login/` | POST | Obtain JWT access and refresh tokens |
| `/api/auth/refresh/` | POST | Refresh access token |
| `/api/profile/` | GET / PATCH | Retrieve or update authenticated user profile |
| `/api/restaurants/` | GET | Retrieve restaurant catalogue |

Complete backend API documentation is available in:

```text
backend/README.md
```

---

# Installation

## Backend

```bash
git clone https://github.com/your-username/ubereats-clone.git

cd ubereats-clone/backend

python -m venv .venv

source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env

python manage.py migrate

python manage.py runserver
```

---

## Frontend

```bash
cd ../frontend

npm install

cp .env.example .env

npm run dev
```

---

# Environment Variables

## Backend

```env
POSTGRES_DB=mydb
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

DJANGO_SECRET_KEY=your-secret-key
DEBUG=True
```

## Frontend

```env
VITE_API_URL=http://localhost:8000/api
```

---

# Running Tests

## Backend

```bash
cd backend

python manage.py test
```

## Frontend

Frontend testing will be introduced in future iterations.

---

# Development Workflow

- Create a feature branch from `dev`
- Implement a single Trello task
- Commit frequently using meaningful commit messages
- Open a Pull Request targeting `dev`
- Pass code review
- Merge using **Squash and Merge**

Example branch names:

```text
feature/cart-system
feature/frontend-auth
feature/order-api
fix/login-validation
```

---

# Team Workflow

1. Pick a Trello task.
2. Create a feature branch.
3. Implement the assigned task.
4. Open a Pull Request.
5. Address review comments.
6. Merge into `dev`.

Every Pull Request should:

- Follow project conventions
- Stay within the assigned ticket scope
- Pass local tests
- Pass SonarCloud Quality Gate (when configured)

---

# AI Vision

Artificial Intelligence is a planned extension of the platform.

Future AI capabilities include:

- Personalized restaurant recommendations
- Personalized menu recommendations
- Learning user preferences
- Recommendation explanations
- Recommendation history
- Intelligent food discovery

These features are **planned for future development** and are **not part of the current MVP**.

---

# License

This project is licensed under the MIT License.
