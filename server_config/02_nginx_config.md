# Lesson 2: Nginx Configuration

Nginx (pronounced "engine-ex") is a high-performance web server built to handle many connections at once while using very little memory. It's become the go-to choice for modern API backends, microservices, and anything that needs to handle concurrent traffic efficiently. In this lesson, you'll install Nginx, configure it to forward traffic to your FastAPI app, and learn the key differences from Apache2.

## What Nginx actually does

The concept is the same as Apache2: Nginx sits in front of your app and forwards requests. But the way it does it is different.

Apache2 uses a **process-based** model — it creates a new process (or thread) for each connection. This works well for many use cases, but can use a lot of memory when thousands of connections come in at once.

Nginx uses an **event-driven** model — it handles thousands of connections in a single process by switching between them as needed. This is why Nginx is often faster and uses less memory under heavy load.

```
User  --->  Nginx (port 80)  --->  Uvicorn (port 8000)  --->  Your FastAPI app
```

The setup looks identical. The difference is in performance and how the configuration is written.

## Step 1: Install Nginx

Update your package list and install Nginx:

```bash
sudo apt update
sudo apt install nginx -y
```

After installation, Nginx starts automatically. Verify it's running:

```bash
sudo systemctl status nginx
```

You should see `active (running)` in green. If not, start it:

```bash
sudo systemctl start nginx
```

Open your browser and visit your server's IP address. You should see the Nginx welcome page: "Welcome to nginx!" If you see it, Nginx is working.

## Step 2: Understand the Nginx directory structure

Nginx stores its configuration differently from Apache2. Here's what you need to know:

```
/etc/nginx/
├── nginx.conf           # Main configuration file
├── sites-available/     # All site configs you create
└── sites-enabled/       # Symlinks to sites that are active
```

- **`sites-available/`** — you write your configs here
- **`sites-enabled/`** — you "turn on" a config by creating a symlink from `sites-available` to `sites-enabled`

This is similar to Apache2's `a2ensite` / `a2dissite` commands, but with Nginx you do it manually (or use a helper script).

## Step 3: Create a server block

Nginx calls its VirtualHost equivalent a **server block**. Create a new configuration file:

```bash
sudo nano /etc/nginx/sites-available/fastapi
```

Paste this configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    access_log /var/log/nginx/fastapi_access.log;
    error_log /var/log/nginx/fastapi_error.log;
}
```

Let's break this down:

- **`listen 80;`** — tells Nginx to listen for HTTP traffic on port 80.
- **`server_name your-domain.com;`** — replace with your actual domain or server IP. This is how Nginx decides which server block to use when a request comes in.
- **`location / { ... }`** — this block matches any URL path. The `/` means "everything."
- **`proxy_pass http://127.0.0.1:8000;`** — forwards the request to your Uvicorn server on port 8000. This is the Nginx equivalent of Apache2's `ProxyPass`.
- **`proxy_set_header`** — these lines pass important information from the original request to your app:
  - **`Host $host`** — the original domain name the user requested
  - **`X-Real-IP $remote_addr`** — the user's actual IP address (not Nginx's)
  - **`X-Forwarded-For $proxy_add_x_forwarded_for`** — a chain of IPs the request passed through
  - **`X-Forwarded-Proto $scheme`** — whether the original request was HTTP or HTTPS
- **access_log / error_log** — where Nginx writes its logs

Save the file and exit (`Ctrl+X`, then `Y`, then `Enter`).

## Step 4: Enable the site and disable the default

First, remove the default site that Nginx comes with:

```bash
sudo rm /etc/nginx/sites-enabled/default
```

Then create a symlink to enable your new site:

```bash
sudo ln -s /etc/nginx/sites-available/fastapi /etc/nginx/sites-enabled/fastapi
```

The `ln -s` command creates a **symbolic link** (a shortcut). Nginx looks at everything in `sites-enabled/` and loads those configs. By linking your file from `sites-available` into `sites-enabled`, you're telling Nginx to use it.

Before restarting, test your configuration for syntax errors:

```bash
sudo nginx -t
```

You should see:

```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

If you see errors, check your config file for typos. Now restart Nginx:

```bash
sudo systemctl restart nginx
```

## Step 5: Start your FastAPI app

Just like with Apache2, your FastAPI app needs to be running on port 8000:

```bash
cd /path/to/your/project
source venv/bin/activate
uvicorn main:app --host 127.0.0.1 --port 8000
```

The `--host 127.0.0.1` flag is important — it makes Uvicorn listen only on localhost, so only Nginx (on the same machine) can reach it.

## Step 6: Test it

Open your browser and visit your server's IP or domain. You should see your FastAPI app's response.

Try the interactive docs too: `http://your-server-ip/docs`

Test from the command line:

```bash
curl http://your-server-ip/
curl http://your-server-ip/docs
```

Both should return your app's responses. The proxy is working.

## A closer look at the configuration

### Handling different paths

If your app has specific paths (like an API at `/api/`), you can configure Nginx to handle them differently:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Serve static files directly
    location /static/ {
        alias /var/www/your-app/static/;
    }

    # Proxy everything else to FastAPI
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

The `location /static/` block tells Nginx to serve files directly from a directory on disk, without bothering your Python app. This is faster because Nginx is optimized for serving static files.

### WebSocket support

If your FastAPI app uses WebSockets (for real-time features like chat or live updates), you need extra configuration:

```nginx
location /ws {
    proxy_pass http://127.0.0.1:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
}
```

WebSockets upgrade the connection from regular HTTP to a persistent two-way connection. The `Upgrade` and `Connection` headers tell Nginx to pass this upgrade request through to your app instead of handling it itself.

## Troubleshooting

**"502 Bad Gateway" error**

Nginx received the request but couldn't reach your app. Check:

1. Is Uvicorn running? (`ps aux | grep uvicorn`)
2. Is it on port 8000? (`curl http://127.0.0.1:8000/`)
3. Did you use `--host 127.0.0.1` when starting Uvicorn?

**"403 Forbidden" error**

This usually means the default site is still active, or there's a permissions issue. Run:

```bash
sudo rm /etc/nginx/sites-enabled/default
sudo ln -s /etc/nginx/sites-available/fastapi /etc/nginx/sites-enabled/fastapi
sudo systemctl restart nginx
```

**"Connection refused" error**

Nginx can't connect to the backend. Check if Uvicorn is running and listening:

```bash
curl http://127.0.0.1:8000/
```

If this works but the proxy doesn't, check your config file for typos.

**Check the logs:**

```bash
sudo tail -f /var/log/nginx/fastapi_error.log
```

This shows the error log in real-time. Make a request and you'll see what Nginx is complaining about.

**Check Nginx status:**

```bash
sudo systemctl status nginx
```

If Nginx won't start, the log output will tell you what's wrong.

## Nginx vs Apache2: quick comparison

| Feature | Apache2 | Nginx |
|---------|---------|-------|
| Architecture | Process-based | Event-driven |
| Memory usage | Higher under load | Lower under load |
| Config syntax | `<VirtualHost>` blocks | `server { }` blocks |
| Static file serving | Good | Excellent |
| Dynamic content | Via modules | Via proxy only |
| Learning curve | Moderate | Slightly easier |

Both work well for proxying to FastAPI. Nginx is often preferred for new projects because of its performance characteristics, but Apache2 is a perfectly valid choice — especially if you're already familiar with it.

## What you learned

- Nginx listens for incoming HTTP requests and forwards them to your app
- Server blocks define how Nginx handles different domains or paths
- `proxy_pass` is the key directive for forwarding traffic
- `proxy_set_header` passes important information (IP addresses, protocols) to your app
- Always test your config with `sudo nginx -t` before restarting
- Nginx can serve static files directly, reducing load on your Python app

## Summary

You now know how to set up both Apache2 and Nginx as reverse proxies for your FastAPI application. Both follow the same concept:

1. Install the web server
2. Configure it to listen on port 80
3. Tell it to forward requests to your app on port 8000
4. Start your app and test

In a later module, you'll learn about SSL/HTTPS setup, which adds encryption so your users' data is protected in transit.
