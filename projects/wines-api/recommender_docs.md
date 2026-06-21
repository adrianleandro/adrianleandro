# Wine Recommender - Two Tower Model Microservice

A personalized wine recommendation service using Google Cloud's Two Tower Model architecture with Vector Search, deployed on Cloud Run.

[![Run on Google Cloud](https://deploy.cloud.run/button.svg)](https://deploy.cloud.run)

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [User Features Guide](#user-features-guide)
- [Development](#development)
- [Deployment](#deployment)
- [Testing](#testing)
- [Contributing](#contributing)

## Overview

This microservice provides personalized wine recommendations by:
1. Accepting **55 comprehensive user preference features** as flattened JSON
2. Generating **user embeddings** via a deployed Two Tower Model on Vertex AI
3. Searching for similar wines using **pre-calculated wine embeddings** in Vertex AI Vector Search
4. Returning **top 10 wine recommendations** with similarity scores

### Two Tower Architecture

```
User Features (55)  ──→  User Tower (Neural Net)  ──→  User Embedding
                                                            │
                                                            ↓
                                                      Vector Search
                                                            ↑
Wine Features       ──→  Wine Tower (Neural Net)  ──→  Wine Embeddings (Pre-calculated)
```


## Architecture

### System Overview

```
Client Request (55 user features in flattened JSON)
     │
     ↓
[Flask App] ──────────────────> Entry Point
     │
     ↓
[Route Layer] ────────────────> /wines endpoint validates request
     │
     ↓
[Wine Service] ───────────────> Orchestrates recommendation flow
     │
     ├──> [Model Service] ────> Calls Vertex AI Two Tower Model
     │         │                 • Input: 55-dimensional feature vector
     │         │                 • Output: User embedding
     │         ↓
     │    User Embedding
     │
     └──> [Vector Search] ─────> Queries pre-calculated wine embeddings
              │                  • Input: User embedding
              │                  • Output: Top 10 similar wines + scores
              ↓
         Wine Recommendations
```

### Directory Structure

```
wines-recommender/
├── app.py                      # Application entry point
├── app_factory.py              # Flask app factory with DI
├── config.py                   # Configuration (env variables)
│
├── routes/                     # HTTP handlers (blueprints)
│   ├── wine_routes.py          # POST /wines, /wines/recommend
│   └── ocr_routes.py           # POST /ocr
│
├── services/                   # Business logic layer
│   ├── model_service.py        # Two Tower Model integration
│   ├── wine_service.py         # Wine recommendations + vector search
│   └── ocr_service.py          # Image OCR processing
│
├── schemas/                    # Data validation
│   ├── user_schema.py          # 55 user features + validation
│   └── wine_schema.py          # Wine data schema
│
└── utils/                      # Utilities
    ├── logging.py              # Structured logging
    └── metadata.py             # GCP metadata helpers
```

### Design Patterns

- **Application Factory**: `create_app()` for flexible initialization
- **Dependency Injection**: Services injected into routes
- **Blueprint Pattern**: Modular route organization
- **Service Layer**: Business logic separated from HTTP layer
- **Schema Validation**: JSON schema for input validation




## Features

### Core Capabilities
- **Two Tower Model Integration**: User preference → embedding → recommendations
- **55 Comprehensive User Features**: Detailed preference profiling
- **Vertex AI Vector Search**: Fast similarity search on wine embeddings
- **Real-time Recommendations**: Sub-second response times
- **OCR Support**: Extract wine names from label images

### Technical Features
- **Flask**: Modern web framework with Blueprint architecture
- **Structured Logging**: JSON logs with Cloud Logging integration
- **Signal Handling**: Graceful shutdown (SIGTERM, SIGINT)
- **Health Checks**: `/` endpoint for monitoring
- **Environment Config**: Full `.env` file support
- **Error Handling**: Comprehensive validation and error responses

### Model Configuration
- **Model Endpoint**: Vertex AI endpoint for Two Tower user model
  - Project: `enhanced-layout-465420-v5`
  - Region: `us-central1`
  - Endpoint ID: `4630095141611241472`

- **Vector Search**: Pre-calculated wine embeddings index
  - API Endpoint: `1034142878.us-central1-438750044055.vdb.vertexai.goog`
  - Index: `projects/438750044055/locations/us-central1/indexEndpoints/8377172494955577344`
  - Deployed Index: `wine_embeddings_1765502080376`

## Quick Start

### Prerequisites

1. **Enable Required APIs**:
```bash
gcloud services enable run.googleapis.com \
  aiplatform.googleapis.com \
  vision.googleapis.com
```

2. **Set Project**:
```bash
export GOOGLE_CLOUD_PROJECT=<YOUR_PROJECT_ID>
```

3. **Authentication**:
```bash
gcloud auth application-default login
```

### Local Development

1. **Clone and Install**:
```bash
git clone <repository-url>
cd wines-recommender
pip install -r requirements.txt
```

2. **Configure Environment**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Run the Server**:
```bash
# Development mode (auto-reload)
python app.py

# Or with gunicorn
gunicorn app:app --bind 0.0.0.0:8080
```

4. **Test the API**:
```bash
# Health check
curl http://localhost:8080/

# Get wine recommendations (see API Reference for full example)
curl -X POST http://localhost:8080/wines \
  -H "Content-Type: application/json" \
  -d @sample_user_features.json
```




## API Reference

### POST /wines (Recommended)

Get personalized wine recommendations using comprehensive user features.

**Request Format** (Flattened JSON with 55 features + optional wine_id):

```json
{
  "wine_id": 12345,
  "rating_mean": 3.8,
  "rating_std": 0.95,
  "rating_count": 150,
  "rating_min": 1.0,
  "rating_max": 5.0,
  "wines_tried": 120,
  "avg_ratings_per_wine": 1.25,
  "coefficient_of_variation": 0.25,
  "red_wine_preference": 4.2,
  "white_wine_preference": 3.5,
  "sparkling_wine_preference": 3.8,
  "rose_wine_preference": 3.3,
  "dessert_wine_preference": 0.0,
  "dessert_port_wine_preference": 0.0,
  "weighted_abv_preference": 13.5,
  "avg_abv_tried": 13.2,
  "high_vs_low_abv_preference": 0.3,
  "very_light_bodied_preference": 0.0,
  "light_bodied_preference": 3.2,
  "medium_bodied_preference": 3.8,
  "full_bodied_preference": 4.1,
  "very_full_bodied_preference": 3.9,
  "low_acidity_preference": 3.5,
  "medium_acidity_preference": 3.9,
  "high_acidity_preference": 3.6,
  "country_1_preference": 4.2,
  "country_2_preference": 3.8,
  "country_3_preference": 3.6,
  "country_4_preference": 3.4,
  "country_5_preference": 3.2,
  "grape_1_preference": 4.3,
  "grape_2_preference": 4.0,
  "grape_3_preference": 3.7,
  "grape_4_preference": 3.5,
  "grape_5_preference": 3.4,
  "complexity_preference": 0.5,
  "avg_complexity_tried": 2.1,
  "reserve_preference": 0.3,
  "grand_preference": 0.2,
  "high_rating_proportion": 0.65,
  "low_rating_proportion": 0.08,
  "rating_entropy": 1.25,
  "rating_1_proportion": 0.02,
  "rating_2_proportion": 0.06,
  "rating_3_proportion": 0.27,
  "rating_4_proportion": 0.45,
  "rating_5_proportion": 0.20,
  "rating_range": 4.0,
  "rating_variance": 0.9025,
  "unique_ratings_count": 5,
  "rating_skewness": -0.35,
  "date_range_days": 365,
  "avg_days_between_ratings": 2.43,
  "rating_trend": 0.001,
  "rating_frequency": 0.41
}
```

**Response**:

```json
{
  "wines": ["wine_123", "wine_456", "wine_789"],
  "scores": {
    "wine_123": 0.95,
    "wine_456": 0.87,
    "wine_789": 0.82
  }
}
```

**cURL Example**:

```bash
curl --location 'https://wines-recommender-438750044055.europe-west1.run.app/wines' \
--header 'Content-Type: application/json' \
--data '{
  "rating_mean": 3.8,
  "rating_std": 0.95,
  "rating_count": 150,
  "rating_min": 1.0,
  "rating_max": 5.0,
  "wines_tried": 120,
  "avg_ratings_per_wine": 1.25,
  "coefficient_of_variation": 0.25,
  "red_wine_preference": 4.2,
  "white_wine_preference": 3.5,
  "sparkling_wine_preference": 3.8,
  "rose_wine_preference": 3.3,
  "dessert_wine_preference": 0.0,
  "dessert_port_wine_preference": 0.0,
  "weighted_abv_preference": 13.5,
  "avg_abv_tried": 13.2,
  "high_vs_low_abv_preference": 0.3,
  "very_light_bodied_preference": 0.0,
  "light_bodied_preference": 3.2,
  "medium_bodied_preference": 3.8,
  "full_bodied_preference": 4.1,
  "very_full_bodied_preference": 3.9,
  "low_acidity_preference": 3.5,
  "medium_acidity_preference": 3.9,
  "high_acidity_preference": 3.6,
  "country_1_preference": 4.2,
  "country_2_preference": 3.8,
  "country_3_preference": 3.6,
  "country_4_preference": 3.4,
  "country_5_preference": 3.2,
  "grape_1_preference": 4.3,
  "grape_2_preference": 4.0,
  "grape_3_preference": 3.7,
  "grape_4_preference": 3.5,
  "grape_5_preference": 3.4,
  "complexity_preference": 0.5,
  "avg_complexity_tried": 2.1,
  "reserve_preference": 0.3,
  "grand_preference": 0.2,
  "high_rating_proportion": 0.65,
  "low_rating_proportion": 0.08,
  "rating_entropy": 1.25,
  "rating_1_proportion": 0.02,
  "rating_2_proportion": 0.06,
  "rating_3_proportion": 0.27,
  "rating_4_proportion": 0.45,
  "rating_5_proportion": 0.20,
  "rating_range": 4.0,
  "rating_variance": 0.9025,
  "unique_ratings_count": 5,
  "rating_skewness": -0.35,
  "date_range_days": 365,
  "avg_days_between_ratings": 2.43,
  "rating_trend": 0.001,
  "rating_frequency": 0.41
}
'
```

### POST /wines/legacy (Deprecated)

Legacy endpoint using direct vector conversion (not Two Tower Model).

**Request**:
```json
{
  "type": "Red",
  "body": 4,
  "dryness": 3,
  "abv": 13.5
}
```

### POST /ocr

Extract text from wine label images.

**Request**: Multipart form data with `image` file

**Response**:
```json
{
  "text": "Extracted text from wine label"
}
```

### GET /

Health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "service": "wine-recommender"
}
```




## User Features Guide

The Two Tower Model requires **55 comprehensive user features** organized into 6 categories:

### 1. Basic User Statistics (8 features)
- `rating_mean`: Average rating given by user (0-5)
- `rating_std`: Standard deviation of ratings
- `rating_count`: Total number of ratings
- `rating_min`, `rating_max`: Rating range
- `wines_tried`: Number of unique wines
- `avg_ratings_per_wine`: Ratings per wine
- `coefficient_of_variation`: Normalized rating consistency

### 2. Wine Type Preferences (6 features)
Weighted average ratings for each type:
- `red_wine_preference`
- `white_wine_preference`
- `sparkling_wine_preference`
- `rose_wine_preference`
- `dessert_wine_preference`
- `dessert_port_wine_preference`

### 3. Wine Attribute Preferences (25 features)

#### ABV Preferences (3)
- `weighted_abv_preference`: ABV weighted by ratings
- `avg_abv_tried`: Simple average ABV
- `high_vs_low_abv_preference`: High vs low ABV rating diff

#### Body Type Preferences (5)
- `very_light_bodied_preference` through `very_full_bodied_preference`

#### Acidity Preferences (3)
- `low_acidity_preference`, `medium_acidity_preference`, `high_acidity_preference`

#### Top Country Preferences (5)
- `country_1_preference` through `country_5_preference`
- Weighted ratings for user's top 5 most-rated countries

#### Top Grape Preferences (5)
- `grape_1_preference` through `grape_5_preference`
- Weighted ratings for user's top 5 most-rated grapes

#### Complexity & Quality (4)
- `complexity_preference`: Complex vs simple wine rating diff
- `avg_complexity_tried`: Average complexity level
- `reserve_preference`: Reserve vs non-reserve rating diff
- `grand_preference`: Grand vs non-grand rating diff

### 4. Rating Behavior Patterns (8 features)
- `high_rating_proportion`: Proportion of 4-5 star ratings
- `low_rating_proportion`: Proportion of 1-2 star ratings
- `rating_entropy`: Rating distribution diversity
- `rating_1_proportion` through `rating_5_proportion`: Individual star proportions

### 5. Preference Diversity Metrics (4 features)
- `rating_range`: Max - Min rating
- `rating_variance`: Rating variance
- `unique_ratings_count`: Number of different rating values
- `rating_skewness`: Rating distribution skewness

### 6. Temporal Rating Patterns (4 features)
- `date_range_days`: Days between first and last rating
- `avg_days_between_ratings`: Average temporal spacing
- `rating_trend`: Linear trend over time
- `rating_frequency`: Ratings per day

### Feature Calculation Notes

**Weighted Averages**: All preferences use rating-weighted averages:
```
weighted_avg = Σ(rating × attribute_value) / Σ(rating)
```

**Difference Metrics**: Capture relative preferences:
```
complexity_preference = avg_rating_complex - avg_rating_simple
```

**Top-N Selection**: Countries and grapes ranked by user's rating count, top 5 selected.




## Development

### Project Structure

```
wines-recommender/
├── app.py                      # Entry point with signal handlers
├── app_factory.py              # Flask app factory
├── config.py                   # Environment-based configuration
├── routes/                     # HTTP handlers (Flask blueprints)
├── services/                   # Business logic layer
├── schemas/                    # JSON schema validation
└── utils/                      # Logging, metadata helpers
```

### Adding a New Endpoint

1. **Create a Service** (if needed):
```python
# services/my_service.py
class MyService:
    def __init__(self, client):
        self.client = client
    
    def process(self, data):
        # Business logic here
        return result
```

2. **Create Routes**:
```python
# routes/my_routes.py
from flask import Blueprint, request, jsonify

my_bp = Blueprint('my', __name__, url_prefix='/my')

def create_my_routes(my_service):
    @my_bp.route("", methods=["POST"])
    def endpoint():
        data = request.get_json()
        result = my_service.process(data)
        return jsonify(result)
    
    return my_bp
```

3. **Register in App Factory**:
```python
# app_factory.py
from routes.my_routes import create_my_routes

def create_app():
    # ...
    my_service = MyService(client)
    app.register_blueprint(create_my_routes(my_service))
```

### Environment Variables

Create a `.env` file:

```bash
# Flask Configuration
DEBUG=true
HOST=localhost
PORT=8080

# Vertex AI Vector Search
API_ENDPOINT=1034142878.us-central1-438750044055.vdb.vertexai.goog
INDEX_ENDPOINT=projects/438750044055/locations/us-central1/indexEndpoints/8377172494955577344
DEPLOYED_INDEX_ID=wine_embeddings_1765502080376

# Two Tower Model
MODEL_PROJECT_ID=enhanced-layout-465420-v5
MODEL_LOCATION=us-central1
MODEL_ENDPOINT_ID=4630095141611241472
```

### Local Development with Cloud Code

This project works with [Cloud Code](https://cloud.google.com/code) for VS Code/IntelliJ:

- **Local development**: [VSCode](https://cloud.google.com/code/docs/vscode/developing-a-cloud-run-service) | [IntelliJ](https://cloud.google.com/code/docs/intellij/developing-a-cloud-run-service)
- **Local debugging**: [VSCode](https://cloud.google.com/code/docs/vscode/debugging-a-cloud-run-service) | [IntelliJ](https://cloud.google.com/code/docs/intellij/debugging-a-cloud-run-service)
- **Deploying**: [VSCode](https://cloud.google.com/code/docs/vscode/deploying-a-cloud-run-service) | [IntelliJ](https://cloud.google.com/code/docs/intellij/deploying-a-cloud-run-service)

### Using Invoke Tasks

Install invoke system-wide:

```bash
pip install invoke
```

Available tasks (see `tasks.py`):

```bash
# Start development server with hot reload
invoke dev

# Build container
invoke build

# Deploy to Cloud Run
invoke deploy

# Run tests
invoke test
```

### Best Practices

1. **Type hints** for better IDE support
2. **Log at service layer** for debugging
3. **Validate at route layer** for security
4. **Keep services pure** (no Flask dependencies)
5. **Use dependency injection** for testability
6. **Document with docstrings**
7. **Handle errors gracefully**
8. **Use config for all settings**




## Deployment

### Deploy to Cloud Run

1. **Set Up Environment**:
```bash
export GOOGLE_CLOUD_PROJECT=<YOUR_PROJECT_ID>
export REPOSITORY="samples"
export REGION=us-central1
```

2. **Enable APIs**:
```bash
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  aiplatform.googleapis.com \
  vision.googleapis.com
```

3. **Create Artifact Registry**:
```bash
gcloud artifacts repositories create $REPOSITORY \
  --location $REGION \
  --repository-format docker
```

4. **Configure Docker**:
```bash
gcloud auth configure-docker
```

5. **Build Container**:
```bash
# Using buildpack
invoke build

# Or using Docker
docker build -t gcr.io/$GOOGLE_CLOUD_PROJECT/wine-recommender .
docker push gcr.io/$GOOGLE_CLOUD_PROJECT/wine-recommender
```

6. **Deploy**:
```bash
# Using invoke
invoke deploy

# Or using gcloud directly
gcloud run deploy wine-recommender \
  --image gcr.io/$GOOGLE_CLOUD_PROJECT/wine-recommender \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated
```

### Environment Variables in Cloud Run

Set required environment variables in deployment:

```bash
gcloud run services update wine-recommender \
  --set-env-vars "MODEL_PROJECT_ID=enhanced-layout-465420-v5" \
  --set-env-vars "MODEL_LOCATION=us-central1" \
  --set-env-vars "MODEL_ENDPOINT_ID=4630095141611241472" \
  --set-env-vars "API_ENDPOINT=1034142878.us-central1-438750044055.vdb.vertexai.goog" \
  --region $REGION
```

## Testing

### Unit Tests

1. **Set credentials**:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="[PATH_TO_KEY]"
export GOOGLE_CLOUD_PROJECT=<PROJECT_ID>
```

2. **Run tests**:
```bash
# All tests
invoke test

# Or with pytest directly
pytest test/ -v

# Specific test file
pytest test/test_app.py -v
```

### System Tests

Run end-to-end tests using Cloud Build:

```bash
gcloud builds submit \
  --config test/advance.cloudbuild.yaml \
  --substitutions 'COMMIT_SHA=manual,REPO_NAME=manual'
```

**Required Setup for System Tests**:

1. **Enable APIs**:
```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  iamcredentials.googleapis.com \
  artifactregistry.googleapis.com
```

2. **Set variables**:
```bash
export PROJECT_ID="$(gcloud config get-value project)"
export PROJECT_NUMBER="$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')"
```

3. **Create service account**:
```bash
gcloud iam service-accounts create token-creator

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:token-creator@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountTokenCreator"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:token-creator@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.invoker"
```

4. **Grant Cloud Build permissions**:
```bash
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com" \
  --role="roles/iam.serviceAccountTokenCreator"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com" \
  --role="roles/artifactregistry.repoAdmin"
```

### Manual Testing

Test the deployed service:

```bash
# Health check
curl https://your-service-url.run.app/

# Wine recommendations
curl -X POST https://your-service-url.run.app/wines \
  -H "Content-Type: application/json" \
  -d @sample_user_features.json
```



## Contributing

Please see the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines.

### Code Style

- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Follow PEP 8 conventions
- Add type hints
- Write docstrings for all functions/classes
- Keep functions small and focused

### Submitting Changes

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest test/ -v`
5. Submit a pull request

## Maintenance & Support

This project performs basic periodic testing. Please use the issue tracker for:
- 🐛 Bug reports
- ✨ Feature requests
- 🔧 Pull requests

## License

This library is licensed under Apache 2.0. Full license text is available in [LICENSE](LICENSE).

---

## Additional Resources

### Documentation Files (Archived)

The following standalone documentation files have been merged into this README:
- `API_EXAMPLES.md` → [API Reference](#api-reference)
- `ARCHITECTURE.md` → [Architecture](#architecture)
- `USER_FEATURES_GUIDE.md` → [User Features Guide](#user-features-guide)
- `DEVELOPER_GUIDE.md` → [Development](#development)
- `README_STRUCTURE.md` → [Architecture](#architecture)

### Useful Links

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Two Tower Models](https://developers.google.com/machine-learning/recommendation/dnn/retrieval)
- [Vector Search Documentation](https://cloud.google.com/vertex-ai/docs/vector-search/overview)
- [Flask Documentation](https://flask.palletsprojects.com/)

### Quick Reference Card

```bash
# Local Development
python app.py                          # Start dev server
export DEBUG=true                      # Enable debug mode

# Testing
pytest test/ -v                        # Run all tests
pytest test/test_app.py -v            # Run specific test

# Deployment
invoke build                           # Build container
invoke deploy                          # Deploy to Cloud Run
gcloud run services list              # List services

# Debugging
gcloud run logs read --service=wine-recommender --limit=50
gcloud run services describe wine-recommender

# Configuration
export GOOGLE_CLOUD_PROJECT=<project>
export GOOGLE_APPLICATION_CREDENTIALS=<path>
```
