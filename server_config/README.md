# Server Configuration and Web Hosting

You built an API. It runs on your laptop at `localhost:8000`. But nobody else can reach it there. To put your API on the real internet, you need a **web server** — software that listens for incoming HTTP requests and forwards them to your application.

This module covers the two most common web servers: **Apache2** and **Nginx**. You'll learn how to install each one, configure it to sit in front of your FastAPI app, and understand why this setup matters.

## Why you need a web server in front of your app

Uvicorn (the server that runs your FastAPI app) is great for development. But in production, you don't expose it directly. Instead, you put a web server like Apache2 or Nginx in front of it. Here's why:

- **Security** — the web server handles SSL/HTTPS, filters bad requests, and protects your app
- **Static files** — serving images, CSS, and JavaScript is faster through a web server than through Python
- **Load balancing** — you can run multiple copies of your app and distribute traffic
- **Logging** — web servers give you detailed access and error logs

This pattern is called a **reverse proxy** — the web server receives requests from the internet and "proxies" (forwards) them to your app running behind it.

## What you'll learn

| # | File | What you'll learn |
|---|------|-------------------|
| 1 | `01_apache2_setup.md` | Install Apache2, configure it as a reverse proxy for your FastAPI app |
| 2 | `02_nginx_config.md` | Install Nginx, configure it as a reverse proxy for your FastAPI app |

## Prerequisites

- A working FastAPI app from the API course (or any Python web app)
- A Linux server (Ubuntu/Debian) — these guides assume Ubuntu 22.04 or later
- A terminal and a text editor
- sudo access on your server

## Which one should you use?

Both Apache2 and Nginx work well. Here's the short version:

- **Apache2** — older, very widely used, huge ecosystem of modules. Good if you're already familiar with it or your hosting provider defaults to it.
- **Nginx** — newer, faster at handling many concurrent connections, uses less memory. Often the go-to choice for modern APIs and microservices.

You'll learn both. In practice, many developers prefer Nginx for API backends, but knowing both makes you more versatile.
