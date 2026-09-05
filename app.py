



import os
import matplotlib
from networkx import graph_atlas
matplotlib.use('Agg')  # Switch to the Agg backend for non-interactive plotting

from flask import Flask, flash, jsonify, render_template, request, redirect, url_for, session
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
import joblib
import random
import re
import csv
import secrets
import matplotlib.pyplot as plt
import io
import base64
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import seaborn as sns # type: ignore
from wordcloud import WordCloud # type: ignore

import requests
from bs4 import BeautifulSoup


from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

import string
from nltk.stem import WordNetLemmatizer



# Download NLTK data if not already downloaded
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')

# Initialize Flask application
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

#// DATABASE
# Configuring SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

# Create the database tables
with app.app_context():
    db.create_all()

#//////
# Load the dataset
file_path = 'deceptive-opinion.csv'
df = pd.read_csv(file_path)

# Load the hotel_reviews.csv for comparison logic
hotel_data_file = 'hotel_reviews.csv'
hotel_df = pd.read_csv(hotel_data_file)




# Preprocess the data for fake review detection
vectorizer = TfidfVectorizer(stop_words='english')
X = vectorizer.fit_transform(df['text'])
y = df['deceptive']

# Train the classifier
classifier = SVC(kernel='linear')
classifier.fit(X, y)

# Save the trained classifier and vectorizer
joblib.dump(classifier, 'classifier.pkl')
joblib.dump(vectorizer, 'vectorizer.pkl')

# Function to parse the CSV file and extract hotel reviews
def parse_csv(file_path):
    hotel_reviews = {}
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            hotel = row['hotel']
            review = {
                'deceptive': row['deceptive'],
                'polarity': row['polarity'],
                'source': row['source'],
                'text': row['text']
            }
            if hotel in hotel_reviews:
                hotel_reviews[hotel].append(review)
            else:
                hotel_reviews[hotel] = [review]
    return hotel_reviews

# Load hotel reviews from the CSV file
hotel_reviews = parse_csv(file_path)



# Define routes for the Flask application
@app.route('/')
def home():
    return redirect(url_for('login'))


# // Database
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Check if password and confirm password match
        if password != confirm_password:
            flash('Passwords do not match', 'error')  # Flash error message
            return redirect(url_for('signup'))

        # Check if username or email already exists
        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()

        # Debugging output
        print(f"Checking username: {username}, email: {email}")
        print("Existing User:", existing_user)
        print("Existing Email:", existing_email)



        if existing_user:
            flash('Username already exists', 'error')  # Flash error message
            return redirect(url_for('signup'))
        if existing_email:
            flash('Email already exists', 'error')  # Flash error message
            return redirect(url_for('signup'))

        # Hash the password
        password_hash = generate_password_hash(password)

        # Create a new user
        new_user = User(username=username, email=email, password_hash=password_hash)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! Please log in.', 'success')  # Flash success message
        return redirect(url_for('login'))
    
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the user exists
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['logged_in'] = True
            session['username'] = username
            flash('Logged in successfully!', 'success')  # Flash success message
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials, please try again.', 'error')  # Flash error message
            return redirect(url_for('login'))
    
    return render_template('login.html')

#////

@app.route('/index')
def index():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/hotel_reviews')
def show_hotel_reviews():
    hotel_amenities = {}
    for hotel_name, reviews in hotel_reviews.items():
        review_texts = [review['text'] for review in reviews]
        polarities = [review['polarity'] for review in reviews]
       
        # Check for amenities based on the reviews
        amenities_present = check_amenities_in_reviews(review_texts, amenities_keywords)
       
        hotel_amenities[hotel_name] = amenities_present
   
    return render_template('hotel_reviews.html', hotel_reviews=hotel_reviews, hotel_amenities=hotel_amenities)


# Clean up the data (strip whitespaces and convert to lowercase for easier matching)
hotel_df['Hotel Name'] = hotel_df['Hotel Name'].str.strip().str.lower()


@app.route('/compare', methods=['POST'])
def compare_hotels():
    selected_hotels = request.form.getlist('hotel')
   
    # Clean up the selected hotel names (strip whitespaces and convert to lowercase)
    selected_hotels = [hotel.strip().lower() for hotel in selected_hotels]
   
    # Fetch data for the selected hotels from the modified dataframe
    comparison_data = hotel_df[hotel_df['Hotel Name'].isin(selected_hotels)]

    # Generate hotel summaries and additional star ratings
    hotel_summaries, additional_star_ratings = generate_hotel_summaries(hotel_aspect_ratings_additional)

   
    # Initialize comparison table for aspects and star ratings
    comparison_table = {}
    star_ratings = {}  # Store star ratings
    pie_charts = {}    # Store pie charts for each hotel
    additional_star_ratings_selected = {}  # New additional star ratings

    for hotel in selected_hotels:
        hotel_info = comparison_data[comparison_data['Hotel Name'] == hotel]

        if not hotel_info.empty:
            # Initialize a dictionary to store the positive/negative count for each aspect
            aspects = {
                'price': {'positive': 0, 'negative': 0},
                'location': {'positive': 0, 'negative': 0},
                'comfort': {'positive': 0, 'negative': 0},
                'cleanliness': {'positive': 0, 'negative': 0},
                'staff': {'positive': 0, 'negative': 0}
            }

            # Filter only truthful reviews
            truthful_reviews = hotel_reviews[hotel] if hotel in hotel_reviews else []
            truthful_reviews = [review for review in truthful_reviews if review['deceptive'] == 'truthful']

            # Count positive and negative reviews for each aspect
            for review in truthful_reviews:
                polarity = review['polarity'].lower()
                for aspect in aspects.keys():
                    if aspect in review['text'].lower():
                        if polarity == 'positive':
                            aspects[aspect]['positive'] += 1
                        else:
                            aspects[aspect]['negative'] += 1

            # Calculate star ratings based on the proportion of positive reviews for each aspect
            star_scores = {}
            for aspect, counts in aspects.items():
                total_reviews = counts['positive'] + counts['negative']
                if total_reviews > 0:
                    proportion_positive = counts['positive'] / total_reviews
                    star_scores[aspect] = proportion_positive * 5  # Scale proportion to a 5-star rating
                else:
                    star_scores[aspect] = 0  # No reviews for this aspect

            # Store the star representation and pie charts for each hotel
            stars_url = create_star_representation(star_scores)
            star_ratings[hotel] = stars_url

            # Generate pie chart data for each aspect
            review_data = [sum(counts['positive'] for counts in aspects.values()),
                           sum(counts['negative'] for counts in aspects.values())]
            review_labels = ['Positive Reviews', 'Negative Reviews']
            pie_chart_url = create_pie_chart(review_data, review_labels, f'Review Sentiment Distribution for {hotel}')
            pie_charts[hotel] = pie_chart_url

            # Store the aspects for the table
            comparison_table[hotel] = {
                'price': hotel_info['Price'].values[0],
                'location': hotel_info['Location'].values[0],
                'comfort': hotel_info['Comfort'].values[0],
                'cleanliness': hotel_info['Cleanliness'].values[0],
                'staff': hotel_info['Staff'].values[0]
            }
             # Add additional star ratings
            additional_star_ratings_selected[hotel] = additional_star_ratings.get(hotel, {})
        else:
            # Handle the case where no matching hotel is found
            comparison_table[hotel] = {
                'price': 'N/A',
                'location': 'N/A',
                'comfort': 'N/A',
                'cleanliness': 'N/A',
                'staff': 'N/A'
            }
            star_ratings[hotel] = None
            pie_charts[hotel] = None
            additional_star_ratings_selected[hotel] = {}

    return render_template('compare.html', comparison_table=comparison_table,
                           selected_hotels=selected_hotels,
                           star_ratings=star_ratings,
                           pie_charts=pie_charts,additional_star_ratings=additional_star_ratings_selected,hotel_summaries=hotel_summaries)





@app.route('/reviews/<hotel_name>')
def show_reviews(hotel_name):
    reviews = hotel_reviews.get(hotel_name)
    if reviews is None:
        return "Hotel not found", 404
   
    filters = {
        'deceptive': ['truthful', 'deceptive'],
        'polarity': ['positive', 'negative'],
        'source': ['TripAdvisor', 'Web', 'MTurk']
    }
   
    return render_template('reviews.html', hotel_name=hotel_name, reviews=reviews, filters=filters)


#////
# Function for advanced text preprocessing
def preprocess_text(review_text):
    # Convert to lowercase
    review_text = review_text.lower()
   
    # Remove punctuation
    review_text = review_text.translate(str.maketrans('', '', string.punctuation))
   
    # Tokenize
    tokens = word_tokenize(review_text)
   
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]
   
    # Lemmatization
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(token) for token in tokens]
   
    # Join tokens back to a single string
    return ' '.join(tokens)

@app.route('/detect_fake_review', methods=['POST'])
def detect_fake_review():
    review_text = request.form['review_text']
   
    # Advanced Preprocessing
    processed_review = preprocess_text(review_text)
   
    # Load the trained classifier and vectorizer
    classifier = joblib.load('classifier.pkl')
    vectorizer = joblib.load('vectorizer.pkl')
   
    # Convert the review text into TF-IDF vectors
    review_tfidf = vectorizer.transform([processed_review])
   
    # Predict using the trained classifier
    prediction = classifier.predict(review_tfidf)
   
    # Return the prediction
    if prediction[0] == 'deceptive':
        result = 'This review is deceptive.'
        truthfulness = "deceptive"
    else:
        result = 'This review is truthful.'
        truthfulness = "truthful"
   
    return render_template('index.html', result=result, truthfulness=truthfulness)





aspect_keywords = {
    'price': ['price', 'cost', 'expensive', 'affordable'],
    'staff': ['staff', 'service', 'reception', 'concierge'],
    'location': ['location', 'nearby', 'distance', 'transport'],
    'comfort': ['comfort', 'bed', 'pillow', 'sleep'],
    'cleanliness': ['clean', 'dirty', 'smell', 'stain', 'tidy'],
    'privacy': ['privacy', 'quiet', 'noise', 'interruption'],
}




    # Keywords for amenities
amenities_keywords = {
        'swimming_pool': ['pool', 'swimming', 'swimming pool'],
        'gym': ['gym', 'fitness', 'workout'],
        'wifi': ['wifi', 'internet', 'wi-fi', 'wireless']
    }


def check_amenities_in_reviews(reviews, amenities_keywords):
    amenities_present = {amenity: False for amenity in amenities_keywords.keys()}
   
    for review in reviews:
        for amenity, keywords in amenities_keywords.items():
            if any(keyword in review.lower() for keyword in keywords):
                amenities_present[amenity] = True
               
    return amenities_present




def preprocess_text(text):
    return text.lower()

def rephrase_sentence(sentence):
    sentence = re.sub(r'\bi\b', 'the guest', sentence)
    sentence = re.sub(r'\bmy\b', 'the guest\'s', sentence)
    sentence = re.sub(r'\bme\b', 'the guest', sentence)
    sentence = re.sub(r'\bwe\b', 'the guests', sentence)
    sentence = re.sub(r'\bour\b', 'the guests\'', sentence)
    sentence = re.sub(r'\bus\b', 'the guests', sentence)
    return sentence

def filter_sentences(sentences):
    filtered_sentences = []
    for sentence in sentences:
        if any(char.isdigit() for char in sentence) or len(sentence.split()) < 5:
            continue
        sentence = rephrase_sentence(sentence)
        filtered_sentences.append(sentence)
    return filtered_sentences


def summarize_reviews(reviews, polarities, aspect_keywords,amenities_keywords):
    aspect_opinions = {aspect: {'positive': [], 'negative': []} for aspect in aspect_keywords.keys()}
    other_opinion = {'positive': [], 'negative': []}

    # Keywords for amenities
    amenities_keywords = {
        'swimming_pool': ['pool', 'swimming', 'swimming pool'],
        'gym': ['gym', 'fitness', 'workout'],
        'wifi': ['wifi', 'internet', 'wi-fi', 'wireless']
    }
    amenities_present = {'swimming_pool': False, 'gym': False, 'wifi': False}


    for review, polarity in zip(reviews, polarities):
        sentences = review.split('.')
        for sentence in sentences:
            sentiment = polarity.strip().lower()
           
            # Check for aspects (price, comfort, etc.)
            for aspect, keywords in aspect_keywords.items():
                if any(keyword in sentence for keyword in keywords):
                    aspect_opinions[aspect][sentiment].append(sentence.strip())
                    break
            else:
                other_opinion[sentiment].append(sentence.strip())


            for amenity, keywords in amenities_keywords.items():
                if any(keyword in sentence.lower() for keyword in keywords):
                    amenities_present[amenity] = True


           

    for aspect in aspect_opinions.keys():
        aspect_opinions[aspect]['positive'] = filter_sentences(aspect_opinions[aspect]['positive'])
        aspect_opinions[aspect]['negative'] = filter_sentences(aspect_opinions[aspect]['negative'])
    other_opinion['positive'] = filter_sentences(other_opinion['positive'])
    other_opinion['negative'] = filter_sentences(other_opinion['negative'])

    return aspect_opinions, other_opinion, amenities_present




def format_summaries(hotel_name, aspect_opinions, other_opinion, max_sentences=2):
    formatted_summary = f"Hotel: {hotel_name}\n"
   
    for aspect, opinions in aspect_opinions.items():
        formatted_summary += f"{aspect.capitalize()}:\n"
        if opinions['positive']:
            positive_summary = ' '.join(random.sample(opinions['positive'], min(max_sentences, len(opinions['positive']))))
            formatted_summary += "Positive: " + positive_summary + '.\n'
        if opinions['negative']:
            negative_summary = ' '.join(random.sample(opinions['negative'], min(max_sentences, len(opinions['negative']))))
            formatted_summary += "Negative: " + negative_summary + '.\n'
        if not opinions['positive'] and not opinions['negative']:
            formatted_summary += "- Not mentioned\n"
        formatted_summary += "\n"
   
    if other_opinion['positive'] or other_opinion['negative']:
        formatted_summary += "Other Opinions:\n"
        if other_opinion['positive']:
            positive_summary = ' '.join(random.sample(other_opinion['positive'], min(max_sentences, len(other_opinion['positive']))))
            formatted_summary += "Positive: " + positive_summary + '.\n'
        if other_opinion['negative']:
            negative_summary = ' '.join(random.sample(other_opinion['negative'], min(max_sentences, len(other_opinion['negative']))))
            formatted_summary += "Negative: " + negative_summary + '.\n'
        formatted_summary += "\n"
   
    return formatted_summary

# Generate pie chart for review distribution
def create_pie_chart(data, labels, title):
    fig, ax = plt.subplots()
    ax.pie(data, labels=labels, autopct='%1.1f%%', colors=['#2ECC71', '#E74C3C'], startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title(title)
   
    # Save the plot to a BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
   
    # Encode the image in base64
    chart_url = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close()
   
    return chart_url

# Generate star representation
def create_star_representation(aspect_scores):
    fig, ax = plt.subplots(figsize=(6, 1))
    ax.axis('off')
   
    for i, (aspect, score) in enumerate(aspect_scores.items()):
        num_stars = int(score)  # Count of filled stars
        star_str = '★' * num_stars + '☆' * (5 - num_stars)  # Create star string
        ax.text(0.5, 1.0 - 0.1 * i, f"{aspect.capitalize()}: {star_str}", ha='center', va='top', fontsize=12)
        ax.text(0.5, 1.0 - 0.1 * i - 0.02, f"({score:.1f}/5)", ha='center', va='top', fontsize=10)  # Display score with one decimal
   
    # Save the plot to a BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
   
    # Encode the image in base64
    stars_url = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close()
   
    return stars_url

#////


@app.route('/summarize_reviews/<hotel_name>', methods=['GET'])

def summary(hotel_name):
    reviews = [review['text'] for review in hotel_reviews.get(hotel_name, [])]
    polarities = [review['polarity'] for review in hotel_reviews.get(hotel_name, [])]
   
    aspect_opinions, other_opinion, amenities_present = summarize_reviews(reviews, polarities, aspect_keywords, amenities_keywords)
   
    formatted_summary = format_summaries(hotel_name, aspect_opinions, other_opinion)
   
    # Calculate review statistics
    total_reviews = len(reviews)
    positive_reviews = sum(polarity == 'positive' for polarity in polarities)
    negative_reviews = total_reviews - positive_reviews
   
    # Generate pie charts
    review_data = [positive_reviews, negative_reviews]
    review_labels = ['Positive Reviews', 'Negative Reviews']
    pie_chart_url = create_pie_chart(review_data, review_labels, 'Review Sentiment Distribution')
   
    aspect_counts = {aspect: sum(aspect in review for review in reviews) for aspect in aspect_keywords}
    aspect_data = list(aspect_counts.values())
    aspect_labels = list(aspect_counts.keys())
    aspect_pie_chart_url = create_pie_chart(aspect_data, aspect_labels, 'Aspect Distribution')
   
    # Calculate aspect scores for star representation
    aspect_scores = {}
    for aspect, opinions in aspect_opinions.items():
        total_aspect_reviews = len(opinions['positive']) + len(opinions['negative'])
        if total_aspect_reviews > 0:
            aspect_scores[aspect] = len(opinions['positive']) / total_aspect_reviews * 5  # Score from 0 to 5
        else:
            aspect_scores[aspect] = 0  # No reviews for this aspect
   
    # Generate additional star ratings for the specific hotel
    additional_stars = additional_star_ratings.get(hotel_name, {})

    
    # Pass aspect scores to the template
    stars_url = create_star_representation(aspect_scores)

    
   
    return render_template(
        'summary.html',
        summary=formatted_summary,
        pie_chart_url=pie_chart_url,
        aspect_pie_chart_url=aspect_pie_chart_url,
        aspect_scores=aspect_scores,  # Pass aspect scores to the template
        stars_url=stars_url,  # Pass the star representation URL
        additional_star_ratings=additional_stars  # Pass the additional star ratings
    
    )


# Integrate the additional star rating logic
# Define additional aspect_keywords if not already defined
aspect_keywords_additional = {
    'price': ['price', 'cost', 'value', 'expensive', 'cheap'],
    'staff': ['staff', 'service', 'personnel', 'employees'],
    'location': ['location', 'proximity', 'distance', 'nearby'],
    'comfort': ['comfort', 'comfortable', 'cozy', 'spacious'],
    'cleanliness': ['clean', 'cleanliness', 'hygiene', 'dirty', 'spotless'],
    'food': ['food', 'breakfast', 'dining', 'restaurant', 'meal']
}

# Filter truthful reviews only
truthful_reviews = df[df['deceptive'] == 'truthful']

# Check unique hotels in the dataset
hotels = truthful_reviews['hotel'].unique()

# Initialize a dictionary to store the aspect ratings for each hotel
hotel_aspect_ratings_additional = {
    hotel: {aspect: {'positive': 0, 'total': 0} for aspect in aspect_keywords_additional}
    for hotel in hotels
}

# Analyze reviews for each aspect and hotel
for index, row in truthful_reviews.iterrows():
    hotel = row['hotel']
    polarity = row['polarity']
    review_text = row['text'].lower()

    # Check for each aspect in the review text
    for aspect, keywords in aspect_keywords_additional.items():
        if any(keyword in review_text for keyword in keywords):
            hotel_aspect_ratings_additional[hotel][aspect]['total'] += 1
            if polarity == 'positive':
                hotel_aspect_ratings_additional[hotel][aspect]['positive'] += 1

# Now calculate star ratings for each aspect of each hotel
additional_star_ratings = {}

for hotel, aspects in hotel_aspect_ratings_additional.items():
    additional_star_ratings[hotel] = {}
    for aspect, counts in aspects.items():
        total = counts['total']
        positive = counts['positive']

        # Calculate the percentage of positive reviews
        if total > 0:
            positive_percentage = (positive / total) * 100
        else:
            positive_percentage = 0

        # Assign star ratings based on the positive percentage
        if positive_percentage >= 81:
            stars = 5
        elif positive_percentage >= 61:
            stars = 4
        elif positive_percentage >= 41:
            stars = 3
        elif positive_percentage >= 21:
            stars = 2
        else:
            stars = 1

        additional_star_ratings[hotel][aspect] = stars


#/////
def generate_hotel_summaries(hotel_aspect_ratings):
    hotel_summaries = {}
    additional_star_ratings = {}

    for hotel, aspects in hotel_aspect_ratings.items():
        positive_aspects = []
        negative_aspects = []
        stars = {}

        # Analyze positive and negative aspects for each hotel
        for aspect, counts in aspects.items():
            total = counts['total']
            positive = counts['positive']
            if total > 0:
                positive_percentage = (positive / total) * 100
                if positive_percentage >= 50:
                    positive_aspects.append(aspect)
                    stars[aspect] = 5  # 5 stars for positive aspects
                else:
                    negative_aspects.append(aspect)
                    stars[aspect] = 2  # 2 stars for negative aspects

        # Create a summary
        positive_summary = f"Positive feedback on {', '.join(positive_aspects)}." if positive_aspects else "No significant positive feedback."
        negative_summary = f"Needs improvement in {', '.join(negative_aspects)}." if negative_aspects else "No significant negative feedback."

        hotel_summaries[hotel] = f"{positive_summary} {negative_summary}"
        additional_star_ratings[hotel] = stars

    return hotel_summaries, additional_star_ratings



# Function to generate sentiment-based summary for an aspect
def generate_aspect_summary(reviews, aspect):
    positive_count = 0
    negative_count = 0
    neutral_count = 0

    # Evaluate each review for the current aspect
    for review in reviews:
        review_lower = review.lower()

        # Check for positive or negative sentiment words (basic heuristic)
        if any(word in review_lower for word in ['good', 'great', 'excellent', 'positive', 'satisfactory']):
            positive_count += 1
        elif any(word in review_lower for word in ['bad', 'poor', 'terrible', 'negative', 'unsatisfactory']):
            negative_count += 1
        else:
            neutral_count += 1

    # Generate an opinion-based summary
    total_reviews = len(reviews)
    if total_reviews == 0:
        return f"No significant feedback on {aspect}."

    positive_percentage = (positive_count / total_reviews) * 100 if total_reviews else 0
    negative_percentage = (negative_count / total_reviews) * 100 if total_reviews else 0
    neutral_percentage = (neutral_count / total_reviews) * 100 if total_reviews else 0

    # Formulate the summary based on the distribution of sentiment
    summary = f"Aspect: {aspect.capitalize()}. "

    if positive_percentage > negative_percentage:
        summary += f"Most guests found the {aspect} satisfactory, with {positive_percentage:.1f}% mentioning positive experiences."
    elif negative_percentage > positive_percentage:
        summary += f"Many guests had concerns about the {aspect}, with {negative_percentage:.1f}% reporting negative feedback."
    else:
        summary += f"The feedback on {aspect} is mixed, with similar positive ({positive_percentage:.1f}%) and negative ({negative_percentage:.1f}%) opinions."

    if neutral_percentage > 0:
        summary += f" Around {neutral_percentage:.1f}% of reviews were neutral or did not emphasize {aspect}."

    return summary

# Function to generate aspect summaries and compare two hotels
def generate_meaningful_comparison(hotel1_name, hotel2_name, df, aspects):
    comparisons = {}

    # Filter reviews for both hotels
    hotel1_reviews = df[df['hotel'] == hotel1_name]['text']
    hotel2_reviews = df[df['hotel'] == hotel2_name]['text']

    # Compare reviews for each aspect
    for aspect in aspects:
        # Filter reviews for the current aspect in both hotels
        hotel1_reviews_filtered = hotel1_reviews[hotel1_reviews.str.contains('|'.join(aspect_keywords[aspect]), case=False)]
        hotel2_reviews_filtered = hotel2_reviews[hotel2_reviews.str.contains('|'.join(aspect_keywords[aspect]), case=False)]

        # Generate sentiment-based summaries for each hotel and aspect
        hotel1_summary = f"{hotel1_name}: " + generate_aspect_summary(hotel1_reviews_filtered.tolist(), aspect)
        hotel2_summary = f"{hotel2_name}: " + generate_aspect_summary(hotel2_reviews_filtered.tolist(), aspect)

        # Store the comparison for this aspect
        comparisons[aspect] = {
            hotel1_name: hotel1_summary,
            hotel2_name: hotel2_summary
        }

    return comparisons



#     # Render the statistics.html template with the summary statistics
#     return render_template('statistics.html', statistics_results=statistics_results, selected_hotels=selected_hotels)


# Initialize a dictionary to store the aspect ratings for each hotel
hotel_aspect_ratings = {hotel: {aspect: {'positive': 0, 'total': 0} for aspect in aspect_keywords} for hotel in hotels}

# Analyze reviews for each aspect and hotel
for index, row in truthful_reviews.iterrows():
    hotel = row['hotel']
    polarity = row['polarity']
    review_text = row['text'].lower()

    # Check for each aspect in the review text
    for aspect, keywords in aspect_keywords.items():
        if any(keyword in review_text for keyword in keywords):
            hotel_aspect_ratings[hotel][aspect]['total'] += 1
            if polarity == 'positive':
                hotel_aspect_ratings[hotel][aspect]['positive'] += 1


#/////
@app.route('/overall_statistics', methods=['POST'])
def overall_statistics():
    selected_hotels = request.form.getlist('hotel')  # Get the list of selected hotels
    if len(selected_hotels) < 2:
        flash('Please select at least two hotels for overall statistics.')
        return redirect(url_for('hotel_reviews'))

    aspects = ['price', 'location', 'staff', 'comfort', 'cleanliness', 'privacy']
    statistics_results = {}  # Initialize a dictionary for statistics results

    # If hotels are selected, gather statistics for each hotel
    for hotel in selected_hotels:
        hotel_reviews_data = hotel_reviews.get(hotel, [])
        if isinstance(hotel_reviews_data, list) and all(isinstance(review, dict) for review in hotel_reviews_data):
            hotel_reviews_data = [review['text'] for review in hotel_reviews_data if 'text' in review]

        statistics_results[hotel] = {
            aspect: generate_aspect_summary(hotel_reviews_data, aspect) for aspect in aspects
        }

    # Initialize a dictionary to store the summary for each hotel
    hotel_summaries = {}

    for hotel, aspects in hotel_aspect_ratings.items():
        positive_aspects = []
        negative_aspects = []

        # Analyze positive and negative aspects for each hotel
        for aspect, counts in aspects.items():
            total = counts['total']
            positive = counts['positive']

            if total > 0:
                positive_percentage = (positive / total) * 100
                if positive_percentage >= 50:
                    positive_aspects.append(aspect)
                else:
                    negative_aspects.append(aspect)

        # Create a two-line summary
        positive_summary = f"Positive feedback on {', '.join(positive_aspects)}." if positive_aspects else "No significant positive feedback."
        negative_summary = f"Needs improvement in {', '.join(negative_aspects)}." if negative_aspects else "No significant negative feedback."

        hotel_summaries[hotel] = f"{positive_summary} {negative_summary}"

    # Generate comparison graphs
    comparison_graph = generate_comparison_graph(selected_hotels, hotel_aspect_ratings, aspects)

    # Render the statistics.html template with the summary statistics, hotel summaries, and graph
    return render_template('statistics.html', statistics_results=statistics_results, selected_hotels=selected_hotels, hotel_summaries=hotel_summaries, comparison_graph=comparison_graph)


def generate_comparison_graph(selected_hotels, hotel_aspect_ratings, aspects):
    aspect_labels = aspects
    hotel_scores = {hotel: [] for hotel in selected_hotels}

    # Collect the aspect ratings for all selected hotels
    for hotel in selected_hotels:
        for aspect in aspect_labels:
            hotel_total = hotel_aspect_ratings[hotel][aspect]['total']
            hotel_positive = hotel_aspect_ratings[hotel][aspect]['positive']
            hotel_scores[hotel].append((hotel_positive / hotel_total) * 100 if hotel_total > 0 else 0)

    # Generate a grouped bar chart comparing all selected hotels
    fig, ax = plt.subplots(figsize=(12, 8))
    index = range(len(aspect_labels))
    bar_width = 0.8 / len(selected_hotels)  # Adjust the bar width based on the number of hotels

    for i, hotel in enumerate(selected_hotels):
        ax.bar([j + i * bar_width for j in index], hotel_scores[hotel], bar_width, label=hotel)

    ax.set_xlabel('Aspect')
    ax.set_ylabel('Positive Feedback (%)')
    ax.set_title(f'Hotel Comparison: {" vs ".join(selected_hotels)}')
    ax.set_xticks([i + (len(selected_hotels) - 1) * bar_width / 2 for i in index])
    ax.set_xticklabels(aspect_labels)
    ax.legend()

    # Save the graph to a PNG image
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    # Encode the image in base64 for embedding in HTML
    graph_base64 = base64.b64encode(image_png).decode('utf-8')

    return graph_base64


#////CHATBOT 


# Define the aspect star ratings and hotels
star_ratings = {
    'conrad': {'price': 2, 'staff': 3, 'location': 4, 'comfort': 3, 'cleanliness': 5, 'food': 4},
    'hyatt': {'price': 3, 'staff': 2, 'location': 3, 'comfort': 4, 'cleanliness': 4, 'food': 3},
    'omni': {'price': 4, 'staff': 3, 'location': 4, 'comfort': 5, 'cleanliness': 2, 'food': 4},
    'fairmont': {'price': 2, 'staff': 3, 'location': 4, 'comfort': 3, 'cleanliness': 2, 'food': 3},
    'sheraton': {'price': 3, 'staff': 4, 'location': 4, 'comfort': 4, 'cleanliness': 4, 'food': 4},
    'knickerbocker': {'price': 3, 'staff': 4, 'location': 3, 'comfort': 5, 'cleanliness': 4, 'food': 3},
    'homewood': {'price': 3, 'staff': 3, 'location': 3, 'comfort': 5, 'cleanliness': 4, 'food': 4},
    'swissotel': {'price': 4, 'staff': 3, 'location': 4, 'comfort': 3, 'cleanliness': 4, 'food': 3},
    'ambassador': {'price': 2, 'staff': 4, 'location': 4, 'comfort': 3, 'cleanliness': 3, 'food': 3},
    'affinia': {'price': 2, 'staff': 3, 'location': 4, 'comfort': 3, 'cleanliness': 3, 'food': 3},
    'hardrock': {'price': 2, 'staff': 3, 'location': 3, 'comfort': 5, 'cleanliness': 3, 'food': 3},
    'talbott': {'price': 2, 'staff': 3, 'location': 4, 'comfort': 4, 'cleanliness': 3, 'food': 4},
    'hilton': {'price': 4, 'staff': 3, 'location': 4, 'comfort': 3, 'cleanliness': 3, 'food': 3},
    'james': {'price': 2, 'staff': 3, 'location': 4, 'comfort': 4, 'cleanliness': 4, 'food': 3},
    'monaco': {'price': 4, 'staff': 3, 'location': 3, 'comfort': 4, 'cleanliness': 3, 'food': 4},
    'sofitel': {'price': 4, 'staff': 3, 'location': 3, 'comfort': 4, 'cleanliness': 4, 'food': 4},
    'palmer': {'price': 3, 'staff': 3, 'location': 4, 'comfort': 5, 'cleanliness': 2, 'food': 4},
    'intercontinental': {'price': 3, 'staff': 3, 'location': 4, 'comfort': 4, 'cleanliness': 4, 'food': 4},
    'allegro': {'price': 3, 'staff': 4, 'location': 2, 'comfort': 3, 'cleanliness': 3, 'food': 4},
    'amalfi': {'price': 3, 'staff': 3, 'location': 3, 'comfort': 4, 'cleanliness': 3, 'food': 4}
}

# Define the questions corresponding to each aspect
questions = {
    'main_preference': "Could you please share your primary criteria when selecting a hotel?",
    'comfort': "Would you prefer a hotel with spacious and well-appointed rooms?",
    'food': "Would you prefer a hotel with exceptional restaurant options?",
    'staff': "Are you looking for a hotel with professional and courteous staff?",
    'location': "Would you prefer a property situated near major attractions or in a central area?",
}


# Define the flow of questions
question_order = ['main_preference', 'comfort', 'food', 'staff', 'location']


@app.route('/chatbot')
def chatbot():
    # Initialize session to store user preferences and state
    session['preferences'] = {aspect: None for aspect in question_order}
    session['current_question'] = 0
    # Render chatbot.html
    return render_template('chatbot.html')

@app.route('/chatbot', methods=['POST'])
def handle_chat():
    user_message = request.json.get('message').lower()
    response = process_user_message(user_message)

    user_message=f"👤💬 {user_message}"
    response=f"🤖💬 {response}"

    return jsonify({"user_message": user_message, "response": response})

def process_user_message(message):
    preferences = session.get('preferences', {aspect: None for aspect in question_order})
    current_question_idx = session.get('current_question', 0)

    # Start the conversation when 'start_conversation' message is received
    if message == 'start_conversation':
        session['current_question'] = 0
        return "Hello! I need to ask you some questions to understand your preference. Let's begin 😊"

    # Process the user's response to the current question
    if 'yes' in message or 'okay' in message:
        aspect = question_order[current_question_idx]
        preferences[aspect] = True
    elif 'no' in message:
        aspect = question_order[current_question_idx]
        preferences[aspect] = False

    session['preferences'] = preferences

    # Move to the next question
    current_question_idx += 1
    session['current_question'] = current_question_idx

    # If all questions have been asked, recommend hotels
    if current_question_idx >= len(question_order):
        return recommend_hotels(preferences)

    # Otherwise, ask the next question
    next_question = questions[question_order[current_question_idx]]
    return next_question

def recommend_hotels(preferences):
    hotels_recommended = []

    for hotel, ratings in star_ratings.items():
        match = True
        if preferences['comfort'] and ratings['comfort'] < 4:
            match = False
        if preferences['food'] and ratings['food'] < 4:
            match = False
        if preferences['staff'] and ratings['staff'] < 4:
            match = False
        if preferences['location'] and ratings['location'] < 4:
            match = False

        if match:
            hotels_recommended.append(hotel)

    if hotels_recommended:
        return f"Based on your preferences, here are some recommended hotels: {', '.join(hotels_recommended)}"
    else:
        return "I'm sorry, I couldn't find any hotels that match your preferences."
    


if __name__ == '__main__':
    app.run(debug=True)





