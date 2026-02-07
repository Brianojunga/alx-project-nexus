# ALX Project Nexus - E-Commerce Platform

[![CI/CD Pipeline](https://github.com/YOUR_USERNAME/alx-project-nexus/workflows/CI%2FCD%20Pipeline/badge.svg)](https://github.com/YOUR_USERNAME/alx-project-nexus/actions)
[![Code Analysis](https://github.com/YOUR_USERNAME/alx-project-nexus/workflows/Code%20Analysis/badge.svg)](https://github.com/YOUR_USERNAME/alx-project-nexus/actions)
[![codecov](https://codecov.io/gh/YOUR_USERNAME/alx-project-nexus/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/alx-project-nexus)

A comprehensive e-commerce platform built with Django REST Framework, featuring vendor management, product catalog, shopping cart, and payment integration with Paystack.

## Features

- **User Management**: Custom user model with role-based access control
- **Vendor Management**: Multi-vendor support with vendor profiles
- **Product Catalog**: Category-based product organization with inventory management
- **Shopping Cart**: Session-based and user-authenticated cart system
- **Order Management**: Complete order lifecycle tracking
- **Payment Integration**: Paystack payment gateway integration
- **API Documentation**: Auto-generated API docs with Swagger/OpenAPI

## Tech Stack

- **Backend**: Django 6.0.1
- **API**: Django REST Framework 3.16.1
- **Database**: PostgreSQL 15
- **Caching**: Redis 7
- **Auth**: JWT (djangorestframework_simplejwt)
- **API Docs**: Swagger (drf-yasg)

## Prerequisites

- Python 3.10+
- PostgreSQL 13+
- Redis 7+
- Git

## Installation & Setup

### 1. Clone Repository

```bash
git clone https://github.com/brianojunga/alx-project-nexus.git
cd alx-project-nexus
```

### 2. Create Virtual Environment

```bash
python -m .venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 5. Database Setup

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Run Development Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000/` for the API and `http://localhost:8000/swagger/` for API documentation.

## Docker Setup

### Build Docker Image

```bash
docker build -t alx-project-nexus .
```

### Run with Docker Compose

```bash
docker-compose up -d
```

Services will be available at:
- API: `http://localhost:8000`
- Adminer: `http://localhost:8080`
- Redis: `localhost:6379`

## Testing

### Run All Tests

```bash
python manage.py test
```

### Run Specific App Tests

```bash
python manage.py test cart
python manage.py test products
python manage.py test accounts
python manage.py test payments
python manage.py test orders
```

### Run with Coverage

```bash
coverage run --source='.' manage.py test
coverage report -m
coverage html  # Generate HTML report
```

### Run Linting

```bash
# Check code style
black . --check
isort . --check-only
flake8 .
pylint $(find . -type f -name "*.py" ! -path "./migrations/*")
```

## CI/CD Pipeline

This project uses GitHub Actions for continuous integration. The pipeline includes:

### Workflows

1. **CI Pipeline** (`.github/workflows/ci.yml`)
   - Runs on: `push` to `main` or `develop`, and `pull_request`
   - Tests on Python 3.10, 3.11, 3.12
   - Services: PostgreSQL, Redis
   - Jobs:
     - **Tests**: Unit tests with coverage
     - **Security**: Bandit, Safety checks
     - **Code Quality**: Linting, formatting checks
     - **Docker**: Build Docker image (main branch only)

2. **Code Analysis** (`.github/workflows/code-analysis.yml`)
   - Detailed code complexity analysis
   - Cyclomatic complexity checks
   - Maintainability index calculation

### Local CI Checks

Run these before pushing:

```bash
# Format code
black .
isort .

# Check formatting
black . --check
isort . --check-only

# Lint
flake8 .
pylint $(find . -type f -name "*.py" ! -path "./migrations/*")

# Security
bandit -r . -ll --exclude "./migrations"

# Tests
python manage.py test
coverage run --source='.' manage.py test
```

## Project Structure

```
alx-project-nexus/
├── .github/
│   └── workflows/           # GitHub Actions workflows
│       ├── ci.yml           # Main CI/CD pipeline
│       └── code-analysis.yml # Code analysis workflow
├── accounts/                # User & vendor management
├── cart/                    # Shopping cart
├── orders/                  # Order management
├── payments/                # Payment integration
├── products/                # Product catalog
├── core/                    # Django settings & URL config
├── Dockerfile               # Docker image configuration
├── docker-compose.yml       # Multi-container setup
├── requirements.txt         # Python dependencies
├── manage.py               # Django management script
└── README.md               # This file
```

## SOME OF THE API Endpoints

### Authentication
- `POST /api/token/` - Obtain JWT token
- `POST /api/token/refresh/` - Refresh JWT token

### Products
- `GET /api/products/` - List all products
- `GET /api/products/{id}/` - Product detail
- `POST /api/products/` - Create product (vendor)

### Cart
- `GET /api/cart/` - Get user's cart
- `POST /api/cart/add/` - Add item to cart
- `DELETE /api/cart/items/{id}/` - Remove from cart

### Orders
- `GET /api/orders/` - List orders
- `POST /api/orders/` - Create order
- `GET /api/orders/{id}/` - Order detail

### Payments
- `POST /api/payments/initialize/` - Initialize payment
- `GET /api/payments/verify/{reference}/` - Verify payment

## Configuration

### Environment Variables

Key environment variables (see `.env.example`):

```
DEBUG=True|False
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@host:port/dbname
REDIS_URL=redis://host:port/0
PAYSTACK_SECRET_KEY=your-paystack-secret
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Testing Best Practices

- Tests are organized by app in each `tests.py` file
- Use Test Case classes for database tests
- Mock external services (Paystack, etc.)
- Aim for >80% code coverage
- Test both happy paths and error cases

## Code Quality Standards

- **Formatting**: Black (line length: 120)
- **Import Sorting**: isort
- **Linting**: flake8, pylint (min score: 7.0)
- **Security**: bandit, safety
- **Complexity**: Max cyclomatic complexity: 10

## Deployment
### Docker Deployment

```bash
docker build -t alx-project-nexus:latest .
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e SECRET_KEY=... \
  alx-project-nexus:latest
```

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes and write tests
3. Run CI checks: `black . && isort . && flake8 . && python manage.py test`
4. Commit: `git commit -am 'Add feature'`
5. Push: `git push origin feature/your-feature`
6. Open a Pull Request

## Troubleshooting

### Database Connection Issues
```bash
python manage.py migrations --dry-run
python manage.py migrate
```

### Redis Connection Issues
```bash
redis-cli ping  # Should return PONG
```

### Permission Errors
```bash
chmod +x manage.py
```

## License

This project is part of the ALX Software Engineering Program.

## Support

For issues and discussions, please use GitHub Issues.

## Acknowledgments

- Django Community
- Django REST Framework
- Paystack
- PostgreSQL
- Redis
