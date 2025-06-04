# Invoice-maker

A simple, secure web application for creating and managing invoices with minimal JavaScript, server-side rendered using Flask.

## Features
- User authentication (default: admin/admin, stored in DB)
- Contact management (full name, email, phone number)
- Invoice creation (with line items, supports USD, LYD (3 decimals), EUR)
- Invoice management (view, edit, delete)
- Print/export invoices in a professional format

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
3. Log in with username: `admin`, password: `admin`

---

## Directory Structure
- app.py: Main Flask application
- models.py: Database models
- templates/: HTML templates
- static/: CSS and (minimal) JS
