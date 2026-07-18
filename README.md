# ONE FOR ALL - All-in-One Utility Application

A comprehensive Flask web application that combines multiple utility tools in one platform with authentication, user management, and various productivity features.

## Features

- **Authentication System**: Secure login and registration with bcrypt password hashing
- **Dashboard**: User-friendly interface to access all tools
- **Notes Manager**: Create, read, update, and delete notes
- **Quiz Generator**: Create and take quizzes
- **Password Generator**: Generate secure random passwords
- **QR Code Generator**: Create QR codes from URLs/text
- **Unit Converter**: Convert between various units
- **Text Utilities**: Various text manipulation tools
- **AI Chat**: Integration with Google Generative AI for intelligent chat

## Tech Stack

- **Backend**: Flask, SQLAlchemy, SQLite
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: JWT, bcrypt
- **APIs**: Google Generative AI
- **Server**: Gunicorn (production)
- **Web Server**: Nginx (recommended for production)

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- Virtual environment (venv)

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd ONE\ FOR\ ALL
```

### 2. Create Virtual Environment
```bash
# On Windows:
python -m venv .venv
.venv\Scripts\activate

# On macOS/Linux:
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 5. Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Development

### Project Structure
```
ONE FOR ALL/
├── app.py                 # Main Flask application
├── config.py              # Configuration management
├── wsgi.py                # WSGI entry point for production
├── requirements.txt       # Python dependencies
├── requirements-prod.txt  # Production dependencies
├── .env                   # Environment variables (not in git)
├── .env.example           # Environment variables template
├── Procfile               # Heroku deployment configuration
├── DEPLOYMENT.md          # Deployment guide
├── routes/                # Route handlers
│   ├── auth.py           # Authentication routes
│   ├── notes.py          # Notes management
│   ├── quiz.py           # Quiz functionality
│   ├── password_generator.py
│   └── ai_chat.py        # AI chat integration
├── templates/            # HTML templates
│   ├── dashboard.html
│   ├── login.html
│   ├── register.html
│   ├── notes.html
│   ├── quiz.html
│   ├── error.html
│   └── ...
├── static/               # Static files (CSS, JS)
│   ├── style.css
│   ├── css/              # Feature-specific CSS
│   └── js/               # Feature-specific JavaScript
└── logs/                 # Application logs (created at runtime)
```

### Environment Variables

Required environment variables (see `.env.example`):

- `SECRET_KEY`: Flask secret key for sessions
- `GOOGLE_API_KEY`: Google API key for services
- `GOOGLE_AI_API_KEY`: Google Generative AI key
- `FLASK_ENV`: Environment mode (development/production)
- `FLASK_HOST`: Server host (default: 127.0.0.1)
- `FLASK_PORT`: Server port (default: 5000)

## Deployment

For comprehensive deployment instructions, see [DEPLOYMENT.md](./DEPLOYMENT.md)

### Quick Start - Production

Using Gunicorn:
```bash
export FLASK_ENV=production
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
```

### Deployment Platforms

- **Heroku**: Use Procfile, follow Heroku deployment guide
- **AWS**: EC2 with Nginx + Gunicorn
- **DigitalOcean**: Droplet with Nginx + Gunicorn
- **Docker**: Containerized deployment
- **PythonAnywhere**: Upload and configure

## Security Features

✅ Password hashing with bcrypt  
✅ Session management with secure cookies  
✅ CSRF protection  
✅ Security headers (X-Content-Type-Options, X-Frame-Options, etc.)  
✅ HTTP Strict Transport Security (HSTS)  
✅ Environment variable protection  
✅ Input validation and sanitization  

## Performance

- Lightweight Flask framework
- Efficient database queries with SQLAlchemy
- Static file caching (configurable in production)
- Gunicorn worker processes for concurrent requests
- Nginx reverse proxy support

## Troubleshooting

### Common Issues

**Database locked error**
- Ensure only one Flask instance is running
- Close any other processes accessing the database

**Module not found**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

**Static files not loading**
- Check Flask static folder configuration
- Verify file paths in HTML templates

**API keys not working**
- Verify `.env` file exists and is properly formatted
- Check that API keys are valid and have necessary permissions

For more issues, check application logs in `logs/app.log`

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes and commit: `git commit -am 'Add feature'`
3. Push to branch: `git push origin feature/your-feature`
4. Submit a pull request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Support

For issues, questions, or suggestions:
- Check existing GitHub issues
- Create a new issue with detailed description
- Contact: support@oneforall.com

## Changelog

### Version 1.0.0
- Initial release
- Full authentication system
- All utility tools implemented
- Production-ready deployment setup
- Comprehensive documentation

---

**Ready for deployment!** Follow [DEPLOYMENT.md](./DEPLOYMENT.md) for platform-specific instructions.
