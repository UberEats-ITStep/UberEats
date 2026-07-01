<div align="center">

# UberEats Clone

### Modern Food Delivery Platform built with Django & React

A full-stack project focused on building a scalable food delivery platform while applying modern software engineering practices, clean architecture, and AI-driven features.

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

**UberEats Clone** is a full-stack food delivery platform inspired by Uber Eats and developed as a software engineering project.

The project is designed not only to deliver a working MVP but also to provide hands-on experience with professional backend and frontend development, REST API design, database architecture, authentication, team collaboration, Git workflow, and scalable software architecture.

The long-term goal is to evolve the platform into an AI-powered food delivery system capable of delivering personalized recommendations and intelligent user experiences.

---

# Core Features

The current scope of the project focuses on building the complete food ordering workflow.

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

The project is designed with future scalability in mind.

Planned long-term features include:

- AI-powered restaurant recommendations
- AI-powered menu recommendations
- Personalized recommendations based on previous orders
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
- Permissions

### Frontend

- React 19
- TypeScript
- Vite
- Tailwind CSS
- Axios
- React Router

Responsible for:

- User Interface
- Authentication State
- API Communication
- Routing

---

# Technology Stack

| Technology            | Purpose             |
| --------------------- | ------------------- |
| Django 6              | Backend Framework   |
| Django REST Framework | REST API            |
| PostgreSQL            | Relational Database |
| SimpleJWT             | Authentication      |
| React 19              | Frontend Framework  |
| TypeScript            | Static Typing       |
| Vite                  | Build Tool          |
| Tailwind CSS          | UI Styling          |
| Axios                 | HTTP Client         |

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
│   │   ├── layouts/
│   │   ├── pages/
│   │   └── routes/
│   └── vite.config.ts
│
└── README.md
```

---

# Database Overview

The application uses **PostgreSQL** as its primary relational database.

Current entities include:

- User
- Profile
- Restaurant
- Category
- MenuItem

The architecture is designed to support future entities such as:

- Cart
- CartItem
- Order
- OrderItem
- RecommendationLog

The system follows a relational database design with Django ORM.

---

# API Overview

| Endpoint              | Method      | Description          |
| --------------------- | ----------- | -------------------- |
| `/api/auth/register/` | POST        | Register a new user  |
| `/api/auth/login/`    | POST        | Obtain JWT tokens    |
| `/api/auth/refresh/`  | POST        | Refresh access token |
| `/api/profile/`       | GET / PATCH | User profile         |
| `/api/restaurants/`   | GET         | Restaurant catalogue |

For complete API documentation, see:

**backend/README.md**

---

# Installation

## Backend

```bash
git clone https://github.com/your-username/ubereats-clone.git

cd ubereats-clone/backend

python -m venv .venv

source .venv/bin/activate
# Windows
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

Frontend testing will be introduced in future iterations.

---

# Development Workflow

- Create a feature branch from `dev`
- Implement the assigned Trello task
- Commit frequently with meaningful commit messages
- Open a Pull Request targeting `dev`
- Pass code review
- Merge using **Squash and Merge**

Example branch names:

```text
feature/cart-system
feature/frontend-auth
fix/login-validation
```

---

# Team Workflow

Our team follows a collaborative development process:

1. Pick a Trello task.
2. Create a feature branch.
3. Implement the task.
4. Open a Pull Request.
5. Address review comments.
6. Merge into `dev`.

Every Pull Request should:

- Follow project conventions
- Pass local testing
- Stay within the assigned ticket scope

---

# AI Vision

Artificial Intelligence is one of the long-term goals of this project.

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
