# TrendMart - Full-Stack Django E-commerce Application

A full-stack e-commerce platform with trending algorithms, real-time analytics, and a custom admin interface built using Django, PostgreSQL, and modern web technologies.

---

## Live Demo

- **Application:** [https://trendmart-django.onrender.com](https://trendmart-django.onrender.com)  
- **Custom Admin Panel:** [https://trendmart-django.onrender.com/admin/](https://trendmart-django.onrender.com/admin/)  

**Demo Admin Credentials:**
- Username: `admin`  
- Password: `admin`  

---

## Project Overview

This application showcases full-stack development with:

- **CRUD Operations** – Complete API-based create, read, update, delete functionality  
- **External API Integration** – Real-time sync with Fake Store API  
- **Data Visualization** – Analytics dashboard with charts and insights  
- **PostgreSQL Database** – Optimized queries and production-ready setup  
- **Custom Admin Interface** – Professional UI for admin (not default Django)  
- **Trending Algorithm** – Product ranking system based on user clicks  

---

## Technical Stack

**Backend:**
- Django 4.2  
- Django REST Framework  
- PostgreSQL  
- Gunicorn  

**Frontend:**
- Tailwind CSS  
- Chart.js  
- HTML5  

**Integrations & Deployment:**
- Fake Store API  
- Render.com (cloud hosting)  
- WhiteNoise (static file serving)  

---

## Features

### API Integration
- Fake Store API integration for products and categories  
- Proxy implementation to bypass hosting restrictions  
- Automatic synchronization of external data  
- Error handling and fallback mechanisms  

### Data Visualization
- Real-time analytics dashboard  
- Product click-based trending analytics  
- Category distribution with pie charts  

---

## Setup & Installation

### Prerequisites
- Python 3.9+  
- PostgreSQL 15  
- Git  

### 1. Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/trendmart-django.git
cd trendmart-django
```
### 2. Environment Setup
```bash
python -m venv venv 
# Activate environment 
source venv/bin/activate   # Linux / Mac 
venv\Scripts\activate      # Windows  

# Install dependencies 
pip install -r requirements.txt

```

### 3. Database Configuration
```bash
CREATE DATABASE trendmart; 
CREATE USER trendmart_user WITH ENCRYPTED PASSWORD 'your_password'; 
GRANT ALL PRIVILEGES ON DATABASE trendmart TO trendmart_user;


```

### 4. Apply Migrations
```bash
python manage.py makemigrations 
python manage.py migrate

```

### 5. Sync External API Data
```bash
python manage.py sync_products

```

### 6. Create Admin User
```bash
python manage.py createsuperuser
```

### 7. Start Development Server
```bash
# Terminal 1: Start Django server 
python manage.py runserver
# Terminal 2: Start Tailwind CSS watcher 
python manage.py tailwind start
```