# Developer Guide: Local Development & Testing

## 1. Set Up Your Environment
- Ensure you have Python and pip installed.
- (First time only) Create a virtual environment:
  ```sh
  python -m venv venv
  ```

## 2. Activate the Virtual Environment
- On Windows (PowerShell):
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- On Windows (cmd):
  ```cmd
  venv\Scripts\activate.bat
  ```
- On macOS/Linux:
  ```sh
  source venv/bin/activate
  ```

## 3. Install Requirements
```sh
pip install -r requirements.txt
```

## 4. Set Up Your `.env` File
- Copy `env.windows` or `.env.example` to `.env` in your project root.
- Fill in your dev MSSQL credentials and any other required variables (including `DJANGO_RUNSERVER_PORT` if you want a custom port).

## 5. Start the Dev Server
- Use the provided script for Windows:
  ```powershell
  .\start-dev.ps1
  ```
  - This will load your `.env`, activate the venv, and start Django on the port you set (default 8000).
- Or, run manually:
  ```sh
  python manage.py runserver 0.0.0.0:8000
  ```

## 6. Test Your API
- Open your browser and go to:
  - [http://localhost:8000/swagger/](http://localhost:8000/swagger/) for interactive API docs.
  - [http://localhost:8000/api/genrate_attribution/](http://localhost:8000/api/genrate_attribution/) for your endpoint (use Swagger UI or Postman to test POST requests).

## 7. Make Code Changes
- Edit your service functions (e.g., in `core/services.py`) and any other logic.
- Save your files; the dev server will auto-reload.

## 8. Check Logs and Debug
- Watch the terminal for errors or logs.
- Use breakpoints or `print()` for debugging.

## 9. (Optional) Run Tests
- If you have Django tests, run:
  ```sh
  python manage.py test
  ```

---

## Summary Table

| Step                | Command/Action                        |
|---------------------|---------------------------------------|
| Create venv         | `python -m venv venv`                 |
| Activate venv       | `./venv/Scripts/Activate.ps1`         |
| Install deps        | `pip install -r requirements.txt`      |
| Set up .env         | Copy and edit `.env`                  |
| Start dev server    | `./start-dev.ps1` or `python manage.py runserver` |
| Test API            | Use Swagger UI or Postman             |
| Make changes        | Edit code, save, auto-reload          |
| Run tests           | `python manage.py test`               | 