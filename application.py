import pandas as pd
from flask import Flask, render_template, request
from pipeline.prediction_pipeline import hybrid_recommendation
from utils.helpers import getAnimeFrame, getSynopsis
from config.paths_config import DF_PATH, SYNOPSIS_DF

app = Flask(__name__)


def enrich_recommendations(anime_names):
    enriched = []
    for i, anime_name in enumerate(anime_names, 1):
        try:
            frame = getAnimeFrame(anime_name, DF_PATH)
            anime_id = int(frame['anime_id'].values[0])
            genres_raw = frame['Genres'].values[0]
            genres = genres_raw if isinstance(genres_raw, str) else 'Unknown'
            synopsis = getSynopsis(anime_id, SYNOPSIS_DF)
            if not isinstance(synopsis, str):
                synopsis = 'No synopsis available.'
        except Exception:
            genres = 'Unknown'
            synopsis = 'No synopsis available.'

        enriched.append({
            'rank': i,
            'name': anime_name,
            'genres': [g.strip() for g in genres.split(',')] if genres != 'Unknown' else [],
            'synopsis': synopsis,
        })
    return enriched


@app.route('/', methods=['GET', 'POST'])
def home():
    recommendations = None
    error = None
    user_id = None

    if request.method == 'POST':
        try:
            user_id = int(request.form['userID'])
            raw = hybrid_recommendation(user_id)
            recommendations = enrich_recommendations(raw)
        except ValueError:
            error = 'Please enter a valid numeric User ID.'
        except Exception as e:
            error = f'Could not generate recommendations. Make sure the User ID exists in the dataset.'
            print(f'Error: {e}')

    return render_template('index.html', recommendations=recommendations, error=error, user_id=user_id)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
