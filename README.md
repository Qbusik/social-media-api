# Social Media API 👦👧🧑

A comprehensive RESTful API built with Django REST Framework, Celery, and Redis.

---

## 📃 Features
- **Admin Panel** – located at /admin/

**This API allows users to:**

- Create and manage their profiles
- Create, update, and delete own posts and comments
- Schedule posts for publishing
- Upload images for posts and profiles
- Follow and unfollow other users
- Like and unlike posts
- Search through profiles and posts

---

## 🛠️ Prerequisites

To run this project, you will need:
**Docker & Docker Compose** - for an easy and consistent setup across environments.

---

## 🚀 Run with DOCKER

This is the fastest method to get the project running in an isolated environment.

1.  **Clone the repository:**
    ```
    git clone https://github.com/Qbusik/social-media-api
    ```

2.  **Configure Environment Variables:**
    Create a `.env` file in the root directory:
    ```
    Create a `.env` file in the root directory using the .env.sample
    ```

3.  **Build and Run Containers:**
    ```
    docker-compose up --build
    ```
    The application will be available at: `http://localhost:8000/`
