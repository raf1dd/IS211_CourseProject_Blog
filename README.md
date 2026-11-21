# IS 211 Course Project: Blogging Application

A web-based blogging application built with Python, Flask, and SQLite.

## How It Works
- **Public Feed (`/`)**: Displays published blog posts in reverse chronological order (newest posts first).
- **Authentication (`/login`, `/logout`)**: Allows an authenticated user to log in and manage blog posts.
- **Dashboard (`/dashboard`)**: Displays posts in a table with **Edit** and **Delete** actions, along with a form or page to create new posts.

## Database Model (`schema.sql`)
- `users`: Stores user accounts (`id`, `username`, `password`) for login authentication.
- `posts`: Stores blog entries (`id`, `title`, `author`, `content`, `published_at`, `is_published`) so posts can be ordered newest-first and toggled between published and draft states.
