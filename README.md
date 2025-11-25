# GOOD TEAM CRM (Call Center)

A Django + SQLite CRM starter for TTC and call center operators with role-aware dashboards, lead tracking, attendance, scripts, chat, salaries, and revenue hooks.

## Quick start (Ubuntu)

1. **Clone & enter the repo**
   ```bash
   git clone <your-fork-url>
   cd call-center-last
   ```
2. **Create a virtual environment and install dependencies**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Set environment variables (optional)**
   ```bash
   export DJANGO_SECRET_KEY="change-me"   # default is a local-only fallback
   export DJANGO_DEBUG=true                # set to false in production
   ```
4. **Initialize the database**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser  # create the initial admin
   ```
5. **Run the development server**
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```
6. **Open the app**
   Visit http://localhost:8000 in your browser. Use the admin at http://localhost:8000/admin for full data management.

## Feature highlights
- Custom user model with roles: Admin, TTC Operator, Call Center Operator.
- TTC operators can submit leads with payment status, amount due, and assignments.
- Call center operators can log call attempts and push status updates back to TTC operators via in-app messages.
- Attendance clock-in/out buttons on dashboards with daily records.
- Admins can create scripts, manage users, and browse all records.
- Lightweight in-app chat to share updates between operators.
- Dark-mode Bootstrap UI with Russian greetings and GOOD TEAM branding.

## Next steps
- Generate migrations after installing dependencies: `python manage.py makemigrations crm`.
- Add real-time notifications (Channels/WebSockets) if needed for production.
- Harden security for production (HTTPS, stricter hosts, robust secrets handling).
