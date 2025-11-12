# AVOCADO

A modern web application for automatic data clustering using K-Means algorithm. Upload your CSV files and get instant insights through intelligent clustering analysis.

## 🚀 Features

- **CSV File Upload**: Simple drag-and-drop interface for uploading CSV files
- **Automatic Clustering**: K-Means clustering algorithm with optimal cluster detection
- **Background Processing**: Asynchronous task processing with real-time status updates
- **Interactive Results**: Visualize clustering results with an intuitive interface
- **Data Export**: Download clustering results as JSON files
- **Modern UI**: Beautiful, responsive design with smooth animations

## 📋 Requirements

- Python 3.8+
- pip (Python package manager)

## 🛠️ Installation

1. **Clone the repository** (or navigate to the project directory):
   ```bash
   cd Fullstack
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🎯 Usage

1. **Start the development server**:
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Open your browser** and navigate to:
   ```
   http://localhost:8000
   ```

3. **Upload a CSV file**:
   - Click "Select CSV file" and choose your file
   - Ensure your CSV contains a `name` column for person identification
   - Click "Start clustering" to begin processing

4. **View results**:
   - Wait for processing to complete
   - Review the clustering results on the results page
   - Download the results as JSON if needed

## 📁 Project Structure

```
Fullstack/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application and routes
│   ├── services/
│   │   └── clustering.py       # Clustering pipeline logic
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css      # Application styles
│   │   └── images/
│   │       └── clustering-diagram.png
│   └── templates/
│       ├── base.html           # Base template
│       ├── upload.html         # File upload page
│       ├── processing.html     # Processing status page
│       └── results.html        # Results display page
├── requirements.txt            # Python dependencies
├── Procfile                    # Deployment configuration
└── README.md                   # This file
```

## 🔧 Technologies Used

- **FastAPI**: Modern, fast web framework for building APIs
- **Uvicorn**: ASGI server for running the application
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing
- **scikit-learn**: Machine learning library (K-Means clustering)
- **Jinja2**: Template engine for HTML rendering

## 📊 CSV File Requirements

Your CSV file must include:
- A `name` column for person identification
- At least one numeric column for clustering
- Optional categorical columns (automatically encoded):
  - `gaming_platform_top1`
  - `social_platform_top1`
  - `ott_top1`
  - `content_creation_freq`

## 🌐 API Endpoints

- `GET /` - Upload page
- `POST /upload` - Upload CSV file and start clustering
- `GET /processing/{task_id}` - Processing status page
- `GET /status/{task_id}` - Get task status (JSON)
- `GET /results/{task_id}` - View clustering results
- `GET /download/{task_id}` - Download results as JSON

## 🚢 Deployment

The project includes a `Procfile` for easy deployment to platforms like Heroku. To deploy:

1. Ensure all dependencies are listed in `requirements.txt`
2. Configure your deployment platform
3. The application will start using the command in `Procfile`
