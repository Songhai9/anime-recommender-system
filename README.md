# Anime Recommender System (ML + MLOps)

## Overview

This project implements an end-to-end machine learning recommender system for anime, combining **collaborative filtering** and **content-based filtering** into a hybrid neural network architecture. The system is trained on a real-world dataset of over 5 million user ratings, deployed as a Flask web application, and supported by a full MLOps infrastructure.
The model is not very accurate and that is intended, as I use 5M rows out of the 70M initially in the dataset.

## Key Components

The architecture includes:

- **RecommenderNet** — custom neural network with 128-dimensional user & anime embedding layers
- **Hybrid Prediction Pipeline** — combines collaborative filtering (cosine similarity in embedding space) and content-based filtering (synopsis/genre embeddings)
- **Google Cloud Storage** — remote data storage and versioning via DVC
- **Comet ML** — experiment tracking (loss, val_loss, MAE, MSE per epoch)
- **Flask Web Application** — user-facing interface served on port 5001
- **Docker + Kubernetes (GKE)** — containerized deployment
- **Jenkins CI/CD** — automated pipeline: test → build → push → deploy

## Model Architecture

The recommender is built around a neural collaborative filtering approach:

1. **Embedding Layers** — separate 128-dim embeddings for users and anime IDs
2. **Dot Product** — L2-normalized dot product to compute affinity scores
3. **Dense Layer** — with batch normalization and sigmoid activation
4. **Loss / Optimizer** — Binary crossentropy + Adam with learning rate scheduling

**Training configuration:**

| Parameter         | Value                           |
|-------------------|---------------------------------|
| Embedding size    | 128 dimensions                  |
| Batch size        | 10,000                          |
| Epochs            | 20 (early stopping, patience=3) |
| Learning rate     | Ramp-up (5 epochs) + decay ×0.8 |
| Train/test split  | All rows except last 1,000      |
| Loss function     | Binary crossentropy             |
| Optimizer         | Adam                            |
| Metrics           | MSE, MAE                        |

## Dataset

**Source:** [Anime Recommendation Database 2020 — Kaggle](https://www.kaggle.com/datasets/hernan4444/anime-recommendation-database-2020)

**Cloud bucket:** `anime-recommender-data05042026` (Google Cloud Storage)

The project uses three data files:

| File                      | Description                                      |
|---------------------------|--------------------------------------------------|
| `anime.csv`               | Metadata: IDs, titles, genres, scores, episodes  |
| `anime_with_synopsis.csv` | Plot summaries for content-based filtering       |
| `animelist.csv`           | ~5M user–anime ratings (filtered for quality)   |

**Preprocessing steps:**
- Users filtered to a minimum of 400 ratings
- Rating values normalized to [0, 1]
- User and anime IDs encoded to sequential indices

## Recommendation Performance

**Hybrid recommendation weights (default):**

| Signal                   | Weight |
|--------------------------|--------|
| User preference (CF)     | 50%    |
| Content similarity (CB)  | 50%    |
| Similar users considered | 10     |
| Similar anime considered | 10     |
| Recommendations returned | 10     |

**Recommendation pipeline:**

1. Find 10 most similar users (cosine similarity over user embeddings)
2. Extract preferences of the input user (top-rated anime by percentile)
3. Collect anime liked by similar users that the input user hasn't watched
4. Score candidate anime by content similarity (synopsis + genre embeddings)
5. Compute weighted hybrid score → return top 10

## MLOps Pipeline

The project implements a production-grade MLOps stack:

**CI/CD (Jenkinsfile):**
- Pull latest data with DVC from GCS
- Run unit tests (`tester.py`)
- Build and push Docker image
- Deploy to Google Kubernetes Engine (GKE)

**Experiment tracking (Comet ML):**
- Logs training loss and validation loss per epoch
- Stores model hyperparameters and run metadata

**Data versioning (DVC + GCS):**
- Raw and processed data tracked via DVC
- Remote storage on Google Cloud Storage

**Deployment:**
- Containerized via Docker (Python 3.8-slim base)
- Orchestrated via Kubernetes (`deployment.yaml`)
- Flask app exposed on port 5001

## Use the project

**Prerequisites:** Python 3.8+, Google Cloud credentials, Comet ML API key

```bash
# 1. Install dependencies
pip install -e .

# 2. Configure environment variables
cp .env.example .env
# Fill in: COMET_API_KEY, COMET_PROJECT_NAME, COMET_WORKSPACE

# 3. (Optional) Pull data with DVC
dvc pull

# 4. Run the training pipeline
python pipeline/training_pipeline.py

# 5. Launch the web application
python application.py
# → Navigate to http://localhost:5001
```

**Docker:**

```bash
docker build -t anime-recommender .
docker run -p 5001:5001 anime-recommender
```

**Kubernetes:**

```bash
kubectl apply -f deployment.yaml
```

## Key Findings

The hybrid approach consistently outperforms pure collaborative filtering for users with limited rating history, where content similarity bridges cold-start limitations. Filtering users to a minimum of 400 ratings significantly improved embedding quality and reduced noise in similarity computations. The learning rate ramp-up schedule stabilized early training and led to faster convergence compared to a fixed learning rate baseline.
