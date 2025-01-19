# Matana University CMS

A powerful Content Management System built specifically for Matana University using Django and Tailwind CSS.

## 🌟 Features

### Content Management
- ✅ Dynamic Page Management
  - Template-based page creation
  - Rich text editing with CKEditor
  - Media management (images, documents)
  - SEO optimization per page
  - Content versioning
  - Draft & publish workflow

- ✅ Content Types & Pages
  - News/Articles with categories
  - Static Pages
  - Profile Pages (Visi Misi, Sejarah, etc)
  - Program/Department Pages
  - Admission Pages
  - Scholarship Information
  - Student Life Pages
  - Media Center (News, Events, Podcast, TV)

- ✅ Navigation & Structure
  - Dynamic menu management
  - Breadcrumb navigation
  - Sitemap generation
  - URL management

### Technical Features
- ✅ Security
  - Role-based access control
  - XSS protection
  - CSRF protection
  - Maintenance mode with IP whitelist
  - Anti-spam system
  - File upload validation
  - Input sanitization
  - Rate limiting
  - Content filtering

- ✅ Performance
  - Page caching
  - Image optimization
  - Lazy loading
  - Database query optimization
  - Static file compression
  - CDN support ready

- ✅ SEO Features
  - Meta tags management
  - Open Graph tags
  - Twitter Cards
  - Sitemap.xml generation
  - Robots.txt configuration
  - SEO-friendly URLs
  - Structured data (Schema.org)
  - Canonical URLs

- ✅ User Interface
  - Responsive design
  - Tailwind CSS integration
  - Custom admin interface
  - Professional maintenance mode page
  - WYSIWYG editor
  - Image cropping tool
  - Drag-and-drop functionality

### TODO Features
- [ ] Multi-language support (ID/EN)
- [ ] Advanced media library
  - Image editing
  - Gallery management
  - Video integration
- [ ] RESTful API endpoints
- [ ] Newsletter system
- [ ] Social media integration
- [ ] Analytics dashboard
- [ ] Automated backup system
- [ ] Event management system
- [ ] Student portal integration
- [ ] E-learning system integration
- [ ] Form builder
- [ ] Search functionality
- [ ] Cache management UI
- [ ] Audit logging

## 🚀 Getting Started

### System Requirements
- Python 3.8+
- Node.js 14+
- PostgreSQL/MySQL (optional, SQLite for development)
- Git
- pip
- virtualenv

### Development Setup

1. Clone the repository
```bash
git clone https://github.com/yourusername/matana-cms.git
cd matana-cms
```

2. Create and activate virtual environment
```bash
# Windows
python -m venv env
env\Scripts\activate

# Linux/Mac
python3 -m venv env
source env/bin/activate
```

3. Install Python dependencies
```bash
pip install -r requirements.txt
```

4. Install Node.js dependencies
```bash
npm install
```

5. Configure environment variables
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
# Required variables:
# - SECRET_KEY
# - DEBUG
# - ALLOWED_HOSTS
# - DATABASE_URL (optional)
```

6. Initialize the database
```bash
python manage.py makemigrations
python manage.py migrate
```

7. Create superuser
```bash
python manage.py createsuperuser
```

8. Run development server
```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000/admin to access the admin interface.

### Production Deployment

Additional steps for production:

1. Set DEBUG=False in .env
2. Configure proper database (PostgreSQL recommended)
3. Set up static files serving
4. Configure HTTPS
5. Set up proper email backend
6. Configure cache backend (Redis recommended)

## 📁 Project Structure Explained

```
matana-cms/
├── apps/                    # Django applications
│   ├── pages/              # Main CMS application
│   │   ├── admin.py       # Admin interface customization
│   │   ├── forms.py       # Form definitions & validation
│   │   ├── models.py      # Database models (Page, Article, etc)
│   │   ├── views.py       # View logic & request handling
│   │   ├── urls.py        # URL routing configuration
│   │   ├── middleware.py  # Custom middleware (maintenance, etc)
│   │   ├── sitemaps.py    # Sitemap generation
│   │   └── utils.py       # Helper functions
│   └── core/              # Core functionality & shared code
├── config/                # Project configuration
│   ├── settings/         # Split settings for different environments
│   │   ├── base.py      # Base settings
│   │   ├── local.py     # Development settings
│   │   └── prod.py      # Production settings
│   ├── urls.py          # Main URL configuration
│   └── wsgi.py          # WSGI application entry point
├── static/               # Static files (CSS, JS, Images)
│   ├── css/             # Compiled CSS files
│   ├── js/              # JavaScript files
│   └── images/          # Static images
├── templates/           # HTML templates
│   ├── admin/          # Custom admin templates
│   ├── pages/          # Page templates
│   │   ├── home.html   # Homepage template
│   │   ├── news.html   # News listing template
│   │   └── profile.html # Profile page template
│   └── components/     # Reusable template components
├── media/              # User uploaded files
├── requirements/       # Split requirements files
│   ├── base.txt       # Base requirements
│   ├── local.txt      # Development requirements
│   └── prod.txt       # Production requirements
├── manage.py          # Django management script
├── package.json       # Node.js dependencies
└── README.md         # Project documentation
```

## 🔧 Common Tasks

### Content Management
1. Creating a new page:
   - Access admin interface
   - Go to Pages > Add Page
   - Select template
   - Add content blocks
   - Set SEO metadata
   - Publish

2. Managing articles:
   - Access admin interface
   - Go to Articles
   - Create/Edit articles
   - Set categories
   - Add featured image
   - Schedule publication

### Development Tasks
1. Adding new template:
   - Create template file in templates/pages/
   - Add template choice in models.py
   - Register in admin interface
   - Create necessary views

2. Database changes:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. Clearing cache:
   ```bash
   python manage.py clear_cache
   ```

## 📝 Dependencies

Key dependencies from requirements.txt:
```
Django==4.2.7
django-ckeditor==6.7.0
Pillow==10.1.0
python-dotenv==1.0.0
django-tailwind==3.6.0
django-cleanup==8.0.0
django-redis==5.4.0
django-storages==1.14.2
psycopg2-binary==2.9.9
gunicorn==21.2.0
whitenoise==6.6.0
```

## 🤝 Contributing

See CONTRIBUTING.md for detailed contribution guidelines.

### Version History
- v1.0.0 - Initial release
- v1.1.0 - Added maintenance mode
- v1.2.0 - Enhanced security features

### Scheduled Tasks
- Daily database backup
- Weekly cache cleanup
- Monthly security audit
