from flask import Flask, render_template, request
import pickle
import requests
import gzip

app = Flask(__name__)

# Add zip to Jinja2 environment
app.jinja_env.filters['zip'] = zip

# Load the pre-saved data
movies = pickle.load(open('movies.pkl', 'rb'))

# Decompress and load similarity.pkl.gz
with gzip.open('similarity.pkl.gz', 'rb') as f:
    similarity = pickle.load(f)

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get('poster_path')
    if poster_path:
        full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
        return full_path
    return "https://via.placeholder.com/500"

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)
    return recommended_movie_names, recommended_movie_posters

@app.route('/')
def index():
    movie_list = movies['title'].values
    return render_template('index.html', movie_list=movie_list)

@app.route('/recommend', methods=['POST'])
def recommend_movies():
    selected_movie = request.form['movie']
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
    return render_template('recommend.html', 
                           movie=selected_movie,
                           recommended_movie_names=recommended_movie_names,
                           recommended_movie_posters=recommended_movie_posters)

if __name__ == '__main__':
    app.run(debug=True)
