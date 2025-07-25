from flask import Flask, render_template, request
import numpy as np
import joblib
import random

# Load files
popular_df = joblib.load(open('popular.pkl', 'rb'))
pt = joblib.load(open('pt.pkl', 'rb'))
books = joblib.load(open('books.pkl', 'rb'))
similarity_scores = joblib.load(open('similarity_score.pkl', 'rb'))

dummy_genres = ['Fiction', 'Fantasy', 'Romance', 'Science Fiction', 'Mystery', 'Thriller', 'Non-Fiction', 'Biography', 'Self-Help', 'History']

if 'Genre' not in popular_df.columns:
    popular_df['Genr    e'] = [random.choice(dummy_genres) for _ in range(len(popular_df))]

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html',
                           book_name=list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df.get('num_ratings', [0]*len(popular_df))),
                           rating=[round(r, 2) for r in popular_df.get('avg_rating', [0]*len(popular_df))]
                           )

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html',
                           book_name=list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values))


@app.route('/recommend_books', methods=['POST'])
def recommend():
    user_input = request.form.get('user_input')

    try:
        index = np.where(pt.index == user_input)[0][0]
        similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]

        data = []
        for i in similar_items:
            item = []
            temp_df = books[books['Book-Title'] == pt.index[i[0]]]
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
            data.append(item)

        return render_template('recommend.html', data=data, book_name=list(pt.index))

    except IndexError:
        return render_template('recommend.html', data=[], book_name=list(pt.index), error="Book not found in index.")

@app.route("/trending")
def trending():
    book_name = list(popular_df['Book-Title'].values)
    author = list(popular_df['Book-Author'].values)
    rating = list(map(float, popular_df['avg_rating'].values))  # correct key
    image = list(popular_df['Image-URL-M'].values)
    votes = list(popular_df['num_ratings'].values)

    return render_template('trending.html',
                           book_name=book_name,
                           author=author,
                           rating=rating,
                           image=image,
                           votes=votes)


@app.route('/contact')
def contact():
    return render_template("contact.html")

if __name__ == '__main__':
    app.run()
