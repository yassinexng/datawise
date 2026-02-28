# Data Analysis ML Engine

A full-stack web application for uploading, analyzing, and visualizing datasets with AI-powered data cleaning suggestions. Users can register, upload CSV/Excel/PDF files, perform exploratory data analysis, apply intelligent cleaning operations, and generate interactive visualizations.

## Tech Stack

**Frontend:**
- Vue 3 (latest)
- Vite (build tool)
- Vue Router (routing)
- Axios (HTTP client)
- ApexCharts (charting)

**Backend:**
- FastAPI (Python web framework)
- SQLAlchemy (async ORM)
- SQLite (database)
- Groq API (AI for data cleaning suggestions)
- Brevo SMTP (email verification)
- Pandas & NumPy (data processing)

## Features

- User registration and email verification
- Password reset via verification codes
- File upload support (CSV, Excel, PDF, TXT)
- Exploratory Data Analysis (EDA) with AI summaries
- Data preview and statistics
- Interactive charts (histograms, scatter plots, correlation heatmaps)
- Intelligent data cleaning with AI suggestions
- Automatic data type detection and conversion
- Outlier detection and handling
- Data visualization and export
- Cleaned dataset download

## How to Install and Run Locally

### Prerequisites
- Python 3.10 or higher
- Node.js 20.19.0 or higher
- Git

### Backend Setup

1. Clone the repository and navigate to the backend directory:
```bash
cd backend
```

2. Create a Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with required environment variables:
```bash
GROK_API_KEY=your_groq_api_key
BREVO_API_KEY=your_brevo_api_key
BREVO_SENDER_EMAIL=your_sender_email@domain.com
```

5. Start the backend server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000` with interactive docs at `http://localhost:8000/docs`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install Node dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | API info and links |
| GET | `/health` | Health check endpoint |
| POST | `/register` | Register new user |
| POST | `/confirmemail` | Confirm email with verification code |
| POST | `/login` | Login user |
| POST | `/forgetpassword1` | Request password reset |
| POST | `/forgetpassword2` | Verify password reset code |
| POST | `/forgetpassword3` | Set new password |
| POST | `/api/upload` | Upload file (CSV/Excel/PDF/TXT) |
| GET | `/dataset/{id}/data` | Get dataset preview (first 20 rows, 5 columns) |
| GET | `/dataset/{id}/analyze` | Run EDA and get analysis with charts |
| GET | `/dataset/{id}/suggestions` | Get AI cleaning suggestions |
| POST | `/dataset/{id}/clean` | Apply data cleaning operations |
| GET | `/dataset/{id}/visualize` | Get visualizations for dataset |
| GET | `/dataset/{id}/download` | Download cleaned dataset as CSV |

## Project Folder Structure

```
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py          # Authentication endpoints
│   │   │   ├── grok.py          # Groq AI integration
│   │   │   ├── script.py        # Model testing script
│   │   │   └── smtp.py          # Email sending service
│   │   ├── core/
│   │   │   ├── EDA.py           # Exploratory analysis
│   │   │   ├── clean.py         # Data cleaning operations
│   │   │   └── visualize.py     # Visualization generation
│   │   ├── database/
│   │   │   └── document.py      # File upload handling
│   │   ├── main.py              # FastAPI app setup
│   │   ├── models.py            # SQLAlchemy models
│   │   └── db_config.py         # Database configuration
│   ├── data/
│   │   ├── ml_engine.db         # SQLite database (auto-created)
│   │   └── schema.sql           # Database schema
│   └── requirements.txt         # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── LoginPage.vue
│   │   │   ├── RegisterPage.vue
│   │   │   ├── ConfirmEmail.vue
│   │   │   ├── forgetpassword1.vue
│   │   │   ├── forgetpassword2.vue
│   │   │   ├── forgetpassword3.vue
│   │   │   └── MainPage.vue
│   │   ├── tabs/
│   │   │   ├── MainLayout.vue
│   │   │   ├── FileUpload/
│   │   │   │   └── FileUploadPage.vue
│   │   │   └── DataAnalysis/
│   │   │       ├── EDA.vue
│   │   │       ├── Clean.vue
│   │   │       └── Visualize.vue
│   │   ├── router/
│   │   │   └── index.js         # Vue Router configuration
│   │   ├── App.vue
│   │   └── main.js
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
│
└── package.json                 # Root dependencies (deprecated in monorepo)
```

## Environment Variables

The following environment variables are required (create a `.env` file in the project root):

- `GROK_API_KEY` - Groq API key for AI-powered data cleaning
- `BREVO_API_KEY` - Brevo (Sendinblue) API key for email service
- `BREVO_SENDER_EMAIL` - Email address to send verification and password reset emails from

Database location and CORS settings are hardcoded in the application and configurable via code modification if needed.
