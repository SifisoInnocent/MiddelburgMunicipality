# 🏛️ Municipal Helpdesk System

A modern, responsive Django-based municipal helpdesk system for citizens to report and track community issues.

## Features

### 🎯 Core Features
- **Issue Reporting**: Citizens can report various community issues (water leaks, potholes, electricity faults, etc.)
- **Real-time Tracking**: Track issue status from submission to resolution
- **Priority Management**: Assign priority levels (Low, Medium, High, Urgent)
- **Image Upload**: Attach photos to reported issues
- **Reference Numbers**: Automatic unique tracking numbers for all issues
- **Search & Filter**: Advanced search and filtering capabilities
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices

### 📊 Dashboard Features
- **Statistics Overview**: Real-time statistics for all reported issues
- **Status Tracking**: Visual status progression (Submitted → In Progress → Resolved → Closed)
- **Pagination**: Efficient handling of large numbers of issues
- **Quick Actions**: Easy access to report new issues and track existing ones

### 🔐 User Management
- **Secure Authentication**: Django's built-in user authentication
- **User Registration**: Simple and fast registration process
- **Profile Management**: User profiles with additional information
- **Role-based Access**: Different access levels for citizens and staff

## Technology Stack

- **Backend**: Django 4.2+
- **Database**: SQLite (development), PostgreSQL (production ready)
- **Frontend**: HTML5, CSS3, JavaScript (vanilla)
- **Image Processing**: Pillow
- **Deployment**: Ready for production with proper settings

## Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Quick Setup

1. **Clone or download the project**
2. **Run the setup script**:
   ```bash
   python setup.py
   ```
3. **Start the development server**:
   ```bash
   python manage.py runserver
   ```
4. **Visit the application**: http://127.0.0.1:8000

### Manual Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up the database**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Create an admin user** (optional):
   ```bash
   python manage.py createsuperuser
   ```

4. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

## Usage

### For Citizens
1. **Register an account** or login
2. **Report an issue** using the intuitive form
3. **Track your issue** using the reference number
4. **View status updates** on your dashboard

### For Staff/Administrators
1. **Access the admin panel** at `/admin`
2. **Manage issues** and update statuses
3. **Assign issues** to staff members
4. **Generate reports** and statistics

## Project Structure

```
municipal-helpdesk/
├── accounts/                 # User management app
│   ├── models.py            # User profile model
│   ├── views.py             # Authentication views
│   └── templates/           # User templates
├── issues/                   # Issue management app
│   ├── models.py            # Issue model with enhanced features
│   ├── views.py             # Issue tracking and management views
│   └── templates/           # Issue templates
├── municipal_helpdesk/       # Django project settings
│   ├── settings.py          # Project configuration
│   └── urls.py              # Main URL configuration
├── media/                    # User uploaded files
├── static/                   # Static files (CSS, JS, images)
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── setup.py                  # Automated setup script
└── README.md                 # This file
```

## Issue Categories

The system supports the following issue categories:
- 💧 **Water Leak**: Water main breaks, leaks, water quality issues
- 🕳️ **Pothole**: Road damage, potholes, street repairs
- ⚡ **Electricity**: Power outages, electrical faults
- 🗑️ **Waste Collection**: Garbage collection, recycling issues
- 💡 **Street Light**: Street lighting problems
- 🔊 **Noise**: Noise complaints
- 🚗 **Parking**: Parking violations and issues
- 📌 **Other**: General issues not covered above

## Priority Levels

- **Low**: Minor issues that don't affect daily life
- **Medium**: Issues that should be addressed soon
- **High**: Urgent issues affecting many people
- **Urgent**: Emergency situations requiring immediate attention

## Status Flow

1. **Submitted**: Issue reported by citizen
2. **In Progress**: Issue being investigated/worked on
3. **Resolved**: Issue has been fixed
4. **Closed**: Issue resolved and verified

## Security Features

- **CSRF Protection**: Built-in Django CSRF protection
- **Input Validation**: All user inputs are validated and sanitized
- **Authentication**: Secure user authentication system
- **Authorization**: Proper access control for different user types
- **SQL Injection Prevention**: Django ORM prevents SQL injection
- **XSS Protection**: Built-in XSS protection

## Customization

### Adding New Issue Categories
Edit `issues/models.py` and add to `CATEGORY_CHOICES`:
```python
CATEGORY_CHOICES = [
    # ... existing categories ...
    ('new_category', '🔧 New Category'),
]
```

### Customizing Priority Levels
Edit `issues/models.py` and modify `PRIORITY_CHOICES`:
```python
PRIORITY_CHOICES = [
    # ... existing priorities ...
    ('critical', 'Critical'),
]
```

### Customizing Status Flow
Edit `issues/models.py` and update `STATUS_CHOICES`:
```python
STATUS_CHOICES = [
    # ... existing statuses ...
    ('verified', 'Verified'),
]
```

## Production Deployment

### Environment Variables
Set these environment variables for production:
```bash
export DEBUG=False
export SECRET_KEY='your-secret-key'
export ALLOWED_HOSTS='yourdomain.com'
export DATABASE_URL='your-database-url'
```

### Static Files
Collect static files for production:
```bash
python manage.py collectstatic
```

### Database
Use PostgreSQL for production:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'municipal_helpdesk',
        'USER': 'your-db-user',
        'PASSWORD': 'your-db-password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the Django documentation at https://docs.djangoproject.com/

## License

This project is open source and available under the MIT License.

---

🏛️ **Empowering Citizens, Improving Service Delivery**
