# Invoice Maker Lite

A simple, secure, and open source web application for creating and managing invoices with project tracking. Built with Flask and Flask-SQLAlchemy.

## Features
- User authentication (admin/user roles, password management)
- Project management (add, edit, delete projects – admin only)
- Invoice management (create, edit, delete, view, print)
- Company info management (admin only)
- Each invoice is linked to a project (selected from a dropdown)
- Professional print/export of invoices
- Clean, responsive UI (Jinja2 templates)
- Data integrity enforced: only valid projects can be assigned to invoices
- Admin-only controls and navigation

## Setup

### Local Development
1. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Run the app:
   ```bash
   python app.py
   ```
3. Log in with username: `admin`, password: `admin` (first run only, you should change this password immediately!)

### Running with Docker
1. Build the Docker image:
   ```bash
   docker build -t invoice-maker-lite .
   ```
2. Run the container:
   ```bash
   docker run -d -p 5000:5000 --name invoice-maker-lite invoice-maker-lite
   ```
   The app will be available at http://localhost:5000

- To override environment variables (e.g., SECRET_KEY), use:
   ```bash
   docker run -d -p 5000:5000 -e SECRET_KEY=your-secret-key --name invoice-maker-lite invoice-maker-lite
   ```

### Deploying to Hosting Services
- For platforms like Heroku, Render, or Fly.io, use the Dockerfile or a compatible Procfile.
- For traditional Python hosting, use Gunicorn:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```
- Ensure to set environment variables and use a secure SECRET_KEY in production.

### Security Reminders
- Change the `SECRET_KEY` for production (can be set via environment variable).
- Change the default admin password immediately after first login.
- Use HTTPS in production deployments.
- Review and configure database and environment settings for your deployment.

## Directory Structure
- `app.py`: Main Flask application and routes
- `models.py`: Database models
- `add_sample_projects.py`: Populate sample projects for testing
- `requirements.txt`: Python dependencies
- `templates/`: Jinja2 HTML templates
- `static/`: CSS and assets

## Security & Open Source Disclosure
- **No sensitive data or secrets are included in this repository.**
- The `SECRET_KEY` in `app.py` is set to a placeholder; you **must** change this for production.
- Default admin credentials are for local development only. Change all passwords before deploying.
- All company info and sample data are generic and for demonstration/testing.
- This project is open source and safe for public sharing.

## License
MIT License. See `LICENSE` file for details.

---
If you contribute or deploy this project, please audit your configuration and secrets before going live.
