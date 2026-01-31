# Customer Churn Project

A Django-based application for analyzing customer churn.

## Security Setup

**IMPORTANT:** Before running this project, you need to set up your environment variables.

1. Copy `.env.example` to `.env`:
   ```
   cp .env.example .env
   ```

2. Generate a new SECRET_KEY:
   ```python
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

3. Update the `.env` file with your new SECRET_KEY

⚠️ **Never commit the `.env` file to Git!** It's already in `.gitignore`.

## Installation

1. Create a virtual environment:
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```
   cd customer_churn
   python manage.py migrate
   ```

5. Start the development server:
   ```
   python manage.py runserver
   ```

## Important Note

If this repository was previously public with the SECRET_KEY exposed, you should:
1. Generate a new SECRET_KEY
2. Rotate any other sensitive credentials
3. Consider the old key compromised
