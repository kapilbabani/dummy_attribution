# Deployment Guide: Django + MSSQL + Docker + Nginx + GitHub Actions

## Prerequisites
- Windows Server (with admin rights)
- Docker installed (see below for setup)
- GitHub repository for your code
- Access to your on-prem MSSQL server

---

## 1. One-Time Server Setup

### a. Install Docker Engine and GitHub Actions Runner
- Edit `setup_onprem_windows.ps1` to set your GitHub repo URL and runner token.
- Run the script as Administrator:
  ```powershell
  .\setup_onprem_windows.ps1
  ```
- This installs Docker Engine (not Docker Desktop) and registers the self-hosted runner as a Windows service.

### b. Generate SSL Certificates for Nginx
- Run the script as Administrator:
  ```powershell
  .\nginx\generate_selfsigned_cert.ps1
  ```
- This will install OpenSSL if needed and generate `server.crt` and `server.key` in `nginx/certs/`.
- For production, replace these with real certificates.

### c. Create Your `.env` File
- Copy `env.linux`, `env.windows`, or `.env.example` to `.env` and fill in your real MSSQL credentials.
- Use `env.linux` for SQL authentication (Linux containers).
- Use `env.windows` for trusted connection (Windows containers).
- **Set your domain and ports:**
  - `DJANGO_SERVER_NAME` — The domain name or DNS for your app (e.g., `myapp.company.com`)
  - `NGINX_PORT` — HTTPS port (default: 443)
  - `NGINX_HTTP_PORT` — HTTP port (default: 80)
  - `DJANGO_RUNSERVER_PORT` — The port your Django app runs on (default: 8000)

---

## 2. Switching Between Linux and Windows Containers

- **Linux Containers (Recommended, SQL Authentication):**
  - Use: `Dockerfile.linux`, `docker-compose.linux.yml`, `env.linux`
  - Start: `docker-compose -f docker-compose.linux.yml --env-file env.linux up -d`

- **Windows Containers (Trusted Connection):**
  - Use: `Dockerfile.windows`, `docker-compose.windows.yml`, `env.windows`
  - Start: `docker-compose -f docker-compose.windows.yml --env-file env.windows up -d`
  - Make sure Docker is in Windows container mode (not Linux mode)

- See `README_SWITCH.md` for a quick reference.

---

## 3. DNS, Port, and App Port Configuration (Dynamic)

- **Domain Name:**
  - Set `DJANGO_SERVER_NAME` in your env file to your desired domain (e.g., `myapp.company.com`).
  - Nginx will use this for `server_name` and HTTPS redirects.
- **Nginx Ports:**
  - Set `NGINX_PORT` and `NGINX_HTTP_PORT` in your env file to control which ports Nginx listens on.
- **Django App Port:**
  - Set `DJANGO_RUNSERVER_PORT` in your env file to control which port Django (Gunicorn/Waitress/dev server) runs on.
  - This is used in:
    - Local dev: `start-dev.ps1` script
    - Linux containers: `Dockerfile.linux`, `docker-compose.linux.yml`
    - Windows containers: `Dockerfile.windows`, `docker-compose.windows.yml`
- **Example:**
  ```env
  DJANGO_SERVER_NAME=myapp.company.com
  NGINX_PORT=443
  NGINX_HTTP_PORT=80
  DJANGO_RUNSERVER_PORT=8000
  ```
- **How it works:**
  - The Nginx config and Docker Compose files are templated at container startup using these variables.
  - You can change the domain or ports by editing your env file and redeploying.

---

## 4. GitHub Actions CI/CD Setup

- The workflow in `.github/workflows/deploy.yml` will automatically deploy your app on push to `main`.
- It uses the `CONTAINER_MODE` secret to select Linux or Windows containers.
  - Set this in your GitHub repo settings: `Settings > Secrets and variables > Actions > New repository secret`
  - Name: `CONTAINER_MODE`, Value: `linux` or `windows`
- The workflow will:
  1. Install dependencies
  2. Run `collectstatic` for Django static files
  3. Build and deploy the correct containers with Docker Compose

---

## 5. Accessing Your App
- After deployment, access your app at:
  - `https://<your-server-ip>/` or `https://<your-domain>/`
- You may get a browser warning for self-signed certs (expected for test certs).

---

## 6. Environment Variables
- **Linux (SQL Auth):**
  - `MSSQL_DB`, `MSSQL_USER`, `MSSQL_PASSWORD`, `MSSQL_HOST`, `MSSQL_PORT`, `DJANGO_SERVER_NAME`, `NGINX_PORT`, `NGINX_HTTP_PORT`, `DJANGO_RUNSERVER_PORT`
- **Windows (Trusted Connection):**
  - `MSSQL_DB`, `MSSQL_HOST`, `MSSQL_PORT`, `DJANGO_SERVER_NAME`, `NGINX_PORT`, `NGINX_HTTP_PORT`, `DJANGO_RUNSERVER_PORT`

---

## 7. Notes & Best Practices
- Linux containers are preferred for most deployments.
- Use Windows containers only if you require trusted connection (Windows Authentication) to MSSQL.
- Never commit real secrets to the repo.
- For production, use real SSL certificates.
- Expand Terraform scripts if you want to automate more infrastructure.
- You can change your domain or ports at any time by editing your env file and redeploying.
- **You can control the Django app port everywhere using `DJANGO_RUNSERVER_PORT`.**

---

## 8. Troubleshooting
- **Runner not picking up jobs:** Check runner status in GitHub > Actions > Runners.
- **Container fails to start:** Check Docker logs:
  ```powershell
  docker logs <container-name>
  ```
- **Static files not served:** Ensure `collectstatic` runs and static volume is mounted.
- **SSL issues:** Replace self-signed certs with valid ones for production.
- **Domain/port not working:** Double-check your env file and redeploy. Ensure DNS is pointed to your server IP.

---

## 9. Useful Commands
- **Switch Docker to Windows container mode:**
  - Right-click Docker icon in system tray > "Switch to Windows containers..."
- **Re-run deployment manually:**
  ```sh
  git commit --allow-empty -m "Trigger redeploy"
  git push
  ```

---

## 10. References
- [Django + mssql-django](https://github.com/microsoft/mssql-django)
- [Docker Compose](https://docs.docker.com/compose/)
- [GitHub Actions Self-hosted Runners](https://docs.github.com/en/actions/hosting-your-own-runners/adding-self-hosted-runners)
- [OpenSSL for Windows](https://slproweb.com/products/Win32OpenSSL.html) 