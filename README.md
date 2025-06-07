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
