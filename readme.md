# Matana University CMS

A powerful Content Management System built specifically for Matana University using Django and Tailwind CSS.

## 📋 Prerequisites

Before you begin, ensure you have met the following requirements:
- Python 3.8+
- pip (Python package manager)
- Git
- A text editor (VS Code recommended)
- Basic knowledge of Django and Python

## 🛠️ Development Environment Setup

### Windows Setup

1. **Install Python**
```bash
# Download Python from python.org
# During installation, check "Add Python to PATH"
python --version  # Verify installation
```

2. **Install Git**
```bash
# Download Git from git-scm.com
git --version  # Verify installation
```

3. **Configure Git**
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## 📥 Installation Steps

1. **Clone Repository**
```bash
git clone https://github.com/yourusername/matana-cms.git
cd matana-cms
```

2. **Create Virtual Environment**
```bash
# Windows
python -m venv env2
source env2/Scripts/activate
```

```bash
# Linux/Mac
python3 -m venv env
source env/Scripts/activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment Setup** (optional)
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
# Required settings:
# - SECRET_KEY
# - DEBUG
# - ALLOWED_HOSTS
# - DATABASE_URL (if using PostgreSQL)
```

5. **Database Setup**
```bash
# Reset any existing migrations
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
rm db.sqlite3  # or del db.sqlite3 on Windows

# Initialize database
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

5. **Create Superuser** (optional)
```bash
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin')" | python manage.py shell
```

6. **Run Development Server**
```bash
python manage.py runserver
```

7. OPTIONAL bulk action automatically:

```bash
python -m venv env2
source env2/Scripts/activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin')" | python manage.py shell
python manage.py runserver
```


## 🗂️ Project Structure

```
matana-cms/
├── apps/                    # Django applications
│   └── pages/              # Main CMS application
│       ├── admin/          # Admin customizations
│       │   ├── __init__.py
│       │   └── views.py
│       ├── migrations/     # Database migrations
│       ├── templates/      # App-specific templates
│       ├── __init__.py
│       ├── admin.py        # Admin interface
│       ├── apps.py         # App configuration
│       ├── forms.py        # Form definitions
│       ├── models.py       # Database models
│       ├── urls.py         # URL patterns
│       └── views.py        # View logic
├── config/                 # Project configuration
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── static/                 # Static files
│   ├── css/
│   ├── js/
│   └── images/
├── templates/             # Project templates
│   ├── admin/
│   ├── pages/
│   └── base.html
├── .env                   # Environment variables
├── .gitignore            # Git ignore rules
├── manage.py             # Django CLI
└── requirements.txt      # Python dependencies
```

## 📝 Configuration

### Essential Settings (.env)
```env
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
STATIC_URL=/static/
MEDIA_URL=/media/
```

### Database Configuration

#### SQLite (Default)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

#### PostgreSQL
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'matana_db',
        'USER': 'db_user',
        'PASSWORD': 'db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 🔧 Troubleshooting

### Common Issues

1. **Migration Conflicts**
```bash
# Reset migrations
python manage.py migrate --fake pages zero
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
python manage.py makemigrations
python manage.py migrate --fake-initial
```

2. **Static Files Not Found**
```bash
# Collect static files
python manage.py collectstatic --noinput

# Verify STATIC_ROOT in settings.py
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

3. **Database Errors**
```bash
# Reset database
python manage.py flush  # Clear all data
python manage.py migrate  # Reapply migrations
```

4. **Permission Issues**
```bash
# Fix media directory permissions
chmod -R 755 media/
chmod -R 755 static/
```

## 📚 Documentation

### API Documentation

Detailed API documentation is available at `/api/docs/` when running the development server.

### Model Documentation

- **Page**: Content pages with templates
- **Article**: News and blog posts
- **MaintenanceMode**: Site maintenance settings

### View Documentation

- **home_view**: Homepage renderer
- **page_view**: Generic page renderer
- **news_view**: Article listing
- **article_detail_view**: Single article display


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


## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
```bash
git checkout -b feature/AmazingFeature
```

3. Commit your changes
```bash
git commit -m 'Add some AmazingFeature'
```

4. Push to the branch
```bash
git push origin feature/AmazingFeature
```

5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- **Your Name** - *Initial work* - [YourGithub](https://github.com/yourusername)


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

