from flask import Flask, render_template, request
from model import recommend_products

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    print("✅ index route hit")
    recommendations = None
    error = None

    if request.method == 'POST':
        try:
            reviews_username = int(request.form['reviews_username'])
            recommendations = recommend_products(reviews_username)
            if not recommendations:
                error = "No recommendations found or user not found."
        except Exception as e:
            error = f"Error: {e}"

    return render_template("index.html", recommendations=recommendations, error=error)

if __name__ == "__main__":
    app.run(debug=True)
