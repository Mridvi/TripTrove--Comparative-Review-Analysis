#  Trip Trove — Hotel Review Analysis

Trip Trove is an **ML/NLP-based web application** designed to help users make better hotel decisions by analyzing online hotel reviews.

## 🚀 Features

- **Fake Review Detection** — Identifies deceptive and truthful reviews using machine learning.
- **Review Summarization** — Extracts important information from hotel reviews.
- **Hotel Comparison** — Compares hotels based on reviews, ratings, and key aspects.
- **Sentiment Analysis** — Analyzes opinions around aspects such as cleanliness, location, comfort, staff, and price.
- **Recommendations** — Helps users find hotels based on their preferences.
- **Data Visualization** — Displays review insights through charts and visual summaries.

## 🔄 Workflow

```text
Hotel Reviews
      ↓
Data Collection & Preprocessing
      ↓
Fake Review Detection
      ↓
Sentiment & Aspect Analysis
      ↓
Summarization & Comparison
      ↓
Hotel Recommendations



📊 Dataset

The dataset contains 1,600 reviews from 20 hotels, consisting of 800 truthful and 800 deceptive reviews.

Reviews are preprocessed using tokenization, stopword removal, and lemmatization.

🤖 Machine Learning

Trip Trove uses TF-IDF with a Support Vector Machine (SVM) to classify reviews as deceptive or truthful.

📈 Performance

| Metric        |      Score |
| ------------- | ---------: |
| **Accuracy**  | **90.54%** |
| **Precision** | **89.71%** |
| **Recall**    | **89.69%** |
| **F1 Score**  | **89.69%** |



🛠️ Tech Stack
Languages: Python, HTML, CSS, JavaScript
Framework: Flask, Flask-SQLAlchemy
ML/NLP: Scikit-learn, NLTK, TF-IDF, SVM
Data & Visualization: Pandas, Matplotlib, Seaborn, WordCloud
Web Scraping: BeautifulSoup, Requests
Database: SQLite / SQLAlchemy


⚙️ Installation

git clone https://github.com/Mridvi/TripTrove--Comparative-Review-Analysis.git
cd trip-trove
pip install -r requirements.txt
python app.py

📈 Results

The fake-review detection model achieved 90.54% accuracy, while the comparative analysis achieved 91.08% accuracy.

⚠️ Limitations

The system may require updates when review sources, languages, or hotel-related aspects change.

Scaling the system for real-time analysis can also increase computational requirements.

🔮 Future Improvements
Real-time fake review detection
Reviewer behavior analysis
Interactive hotel maps
Improved aspect and sentiment analysis
More advanced recommendation capabilities


📄 Research Paper

“Trip Trove: Comparative Review Analysis”

Published and presented at ICAML 2025.
