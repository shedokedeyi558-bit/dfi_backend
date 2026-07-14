# Lesson 1: Apache2 Setup

Apache2 is one of the most established web servers in the world. It's been around since 1995 and powers a huge portion of the internet. In this lesson, you'll install Apache2, configure it to forward traffic to your FastAPI app, and understand how each piece fits together.

## What Apache2 actually does

When someone types your domain name into their browser, their computer sends an HTTP request to your server's IP address. Apache2 is the software listening on port 80 (HTTP) or port 443 (HTTPS). It receives that request, decides what to do with it, and sends back a response.

In our case, we want Apache2 to do something simple: take incoming requests and forward them to our FastAPI app running on Uvicorn. This is called **reverse proxying** — Apache2 acts as a middleman between the user and your app.

```
User  --->  Apache2 (port 80)  --->  Uvicorn (port 8000)  --->  Your FastAPI app
```

## Step 1: Install Apache2

First, update your package list and install Apache2:

```bash
sudo apt update
sudo apt install apache2 -y
```

`apt` is Ubuntu's package manager. `sudo` gives us admin privileges (you'll be asked for your password). The `-y` flag automatically answers "yes" to the install prompt.

After installation, Apache2 starts automatically. You can verify it's running:

```bash
sudo systemctl status apache2
```

You should see `active (running)` in green. If you see `inactive (dead)`, start it manually:

```bash
sudo systemctl start apache2
```

Open your browser and visit your server's IP address (e.g., `http://your-server-ip`). You should see the default Apache2 welcome page. If you see it, Apache2 is working.

## Step 2: Enable the proxy modules

Apache2 doesn't forward traffic to other servers by default. You need to enable the modules that give it this ability:

```bash
sudo a2enmod proxy
sudo a2enmod proxy_http
```

`a2enmod` is Apache2's tool for enabling modules. Here's what each module does:

- **`proxy`** — the core proxy module. It tells Apache2 "I can forward traffic to another server."
- **`proxy_http`** — specifically handles HTTP traffic. This lets Apache2 talk to your Uvicorn server using HTTP.

After enabling the modules, restart Apache2 so the changes take effect:

```bash
sudo systemctl restart apache2
```

## Step 3: Create a VirtualHost configuration

Apache2 uses something called **VirtualHosts** to handle different domains or different configurations on the same server. We'll create a VirtualHost that says: "any traffic coming in on port 80 should be forwarded to our FastAPI app on port 8000."

Create a new configuration file:

```bash
sudo nano /etc/apache2/sites-available/fastapi.conf
```

`nano` is a simple text editor. If you prefer `vim` or something else, use that instead.

Paste this configuration:

```apache
<VirtualHost *:80>
    ServerName your-domain.com

    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/

    ErrorLog ${APACHE_LOG_DIR}/fastapi_error.log
    CustomLog ${APACHE_LOG_DIR}/fastapi_access.log combined
</VirtualHost>
```

Let's break this down line by line:

- **`<VirtualHost *:80>`** — this block applies to all traffic on port 80. The `*` means "any IP address."
- **`ServerName your-domain.com`** — replace this with your actual domain name. If you don't have a domain yet, use your server's IP address.
- **`ProxyPreserveHost On`** — passes the original `Host` header to your app. This is useful if your app needs to know the original domain the request was for.
- **`ProxyPass / http://127.0.0.1:8000/`** — the core rule. "Forward everything from `/` to `http://127.0.0.1:8000/`." That's your Uvicorn server.
- **`ProxyPassReverse / http://127.0.0.1:8000/`** — when your app sends back a response with redirects or URLs, Apache2 rewrites them to match the original domain. Without this, responses might contain `127.0.0.1:8000` instead of your real domain.
- **ErrorLog / CustomLog** — tells Apache2 where to write logs for this VirtualHost.

Save the file and exit nano (`Ctrl+X`, then `Y`, then `Enter`).

## Step 4: Enable the site and disable the default

Apache2 comes with a default site. We don't need it anymore, so let's disable it and enable ours:

```bash
sudo a2dissite 000-default.conf
sudo a2ensite fastapi.conf
```

- **`a2dissite`** — disables a site configuration
- **`a2ensite`** — enables a site configuration

Now restart Apache2 to apply the changes:

```bash
sudo systemctl restart apache2
```

## Step 5: Start your FastAPI app

For this to work, your FastAPI app needs to be running on port 8000. If you're still using the development server, start it like this:

```bash
cd /path/to/your/project
source venv/bin/activate
uvicorn main:app --host 127.0.0.1 --port 8000
```

Notice we're using `--host 127.0.0.1` instead of the default. This makes Uvicorn only listen on localhost, which means only Apache2 (running on the same machine) can talk to it. This is more secure than exposing Uvicorn directly to the internet.

> **Important:** For production, you should run Uvicorn with a process manager like `systemd` so it starts automatically and restarts if it crashes. We'll cover that in a later lesson. For now, this is fine for testing.

## Step 6: Test it

Open your browser and visit your server's IP or domain. You should see your FastAPI app's response — not the Apache2 welcome page.

If you have a `/docs` endpoint (FastAPI's automatic docs), try visiting `http://your-server-ip/docs`. It should show the Swagger UI.

You can also test from the command line:

```bash
curl http://your-server-ip/
curl http://your-server-ip/docs
```

If both return your app's responses, the proxy is working.

## Troubleshooting

**"502 Bad Gateway" error**

This is the most common error. It means Apache2 received the request but couldn't connect to your app. Check:

1. Is Uvicorn running? (`ps aux | grep uvicorn`)
2. Is it on port 8000? (`curl http://127.0.0.1:8000/`)
3. Did you use `--host 127.0.0.1` when starting Uvicorn?

**"403 Forbidden" error**

Apache2 doesn't have permission to serve content. This usually means the default site is still active. Run:

```bash
sudo a2dissite 000-default.conf
sudo a2ensite fastapi.conf
sudo systemctl restart apache2
```

**"Connection refused" error**

Apache2 can't reach the backend at all. Make sure Uvicorn is running and listening on the correct port. Check with:

```bash
curl http://127.0.0.1:8000/
```

If this works but the proxy doesn't, the issue is in your VirtualHost config.

**Still not working? Check the logs:**

```bash
sudo tail -f /var/log/apache2/fastapi_error.log
```

This shows you the error log in real-time. Make a request in your browser, and you'll see what Apache2 is complaining about.

## What you learned

- Apache2 listens for incoming HTTP requests on port 80
- The `proxy` and `proxy_http` modules let Apache2 forward traffic to another server
- VirtualHosts define how Apache2 handles different domains or ports
- `ProxyPass` and `ProxyPassReverse` are the key directives for reverse proxying
- Uvicorn should listen on localhost only, with Apache2 as the public-facing server

## Next

Now that you've set up Apache2, let's see how Nginx does the same thing — with a different approach and different strengths.
