# 🏨 Trip Trove — Hotel Review Analysis

## 📘 Abstract

**Trip Trove** is a **machine learning** and **natural language processing** -based web application developed to help users make informed hotel booking decisions by analyzing large collections of online hotel reviews. Since online reviews can contain misleading or deceptive content, the project focuses on identifying fake reviews while extracting meaningful insights from genuine customer feedback.


The system uses NLP techniques such as HTML and special-character removal, tokenization, lowercasing, stopword removal, and lemmatization to preprocess hotel reviews. **TF-IDF** is used to convert reviews into numerical features, which are then classified using an **SVM** model for fake review detection.


Beyond **fake review detection**, Trip Trove analyzes genuine reviews to identify opinions on aspects such as cleanliness, comfort, location, staff, and price. It provides **review summaries**, sentiment insights, **hotel comparisons**, ratings, **visualizations**, and **recommendations** to make hotel reviews easier to understand.



## 🚀 Features

- **Fake Review Detection** — Identifies deceptive and truthful reviews using machine learning.
- **Review Summarization** — Extracts important information from hotel reviews.
- **Hotel Comparison** — Compares hotels based on reviews, ratings, and key aspects.
- **Sentiment Analysis** — Analyzes opinions around cleanliness, location, comfort, staff, and price.
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
```
## 📊 Dataset

The project uses a dataset of **1,600 hotel reviews collected from 20 different hotels**, equally divided into **800 truthful and 800 deceptive reviews**. The dataset was used to train and evaluate the fake review detection model.

Each review contains information such as:
- **Hotel Name**
- **Sentiment Polarity**
- **Review Source**
- **Relevant Metadata**

### 🔄 Data Preprocessing

The reviews undergo several preprocessing steps before analysis:

**HTML & Symbol Removal → Tokenization → Lowercasing → Stopword Removal → Lemmatization**

This helps remove noise and convert the reviews into a consistent format suitable for machine learning and NLP analysis.

## 🤖 Machine Learning

Trip Trove uses **TF-IDF feature extraction and a Support Vector Machine (SVM)** to classify reviews as **truthful or deceptive**.

The research also evaluated several other machine learning and deep learning approaches, including **LSTM, Bi-LSTM, CNN, CNN-LSTM, GRU-CNN, CNN-BiLSTM, Logistic Regression, and Random Forest**. Among the evaluated models, **SVM achieved the strongest overall accuracy**.

### 📈 Model Performance

| Metric | Score |
|---|---:|
| **Accuracy** | **90.54%** |
| **Precision** | **89.71%** |
| **Recall** | **89.69%** |
| **F1 Score** | **89.69%** |

The model demonstrated consistent performance in distinguishing deceptive reviews from genuine reviews, helping ensure that subsequent review analysis focuses on more reliable content.

## 🛠️ Tech Stack

- **Languages:** Python, HTML, CSS, JavaScript
- **Framework:** Flask, Flask-SQLAlchemy
- **ML/NLP:** Scikit-learn, NLTK, TF-IDF, SVM
- **Data & Visualization:** Pandas, Matplotlib, Seaborn, WordCloud
- **Web Scraping:** BeautifulSoup, Requests
- **Database:** SQLite / SQLAlchemy

## ⚙️ Installation

```bash
git clone https://github.com/Mridvi/TripTrove--Comparative-Review-Analysis.git
cd TripTrove--Comparative-Review-Analysis
pip install -r requirements.txt
python app.py
```


## 📈 Results

The fake-review detection model achieved **90.54% accuracy**, with **89.71% precision, 89.69% recall, and 89.69% F1-score**.

The comparative analysis component achieved **91.08% accuracy**, demonstrating the effectiveness of combining review analysis with hotel comparison.

## ⚠️ Limitations

- **Generalization:** Models trained on a specific domain or language may not perform equally well across different hotel domains, languages, or types of reviews.
- **Scalability & Real-Time Processing:** Processing large volumes of reviews and continuously updating models can increase computational requirements, making real-time detection challenging.
- **Dynamic Content:** Customer preferences and important hotel aspects can change over time. The system therefore requires periodic updates to aspect keywords and training data.

## 🔮 Future Improvements

- **Reviewer Behavior Analysis** — Identify suspicious patterns using review frequency, language patterns, and other reviewer behavior.
- **Interactive Maps** — Add location-based maps showing hotels and nearby points of interest.
- **Real-Time Fake Review Detection** — Develop streaming-based monitoring to detect suspicious reviews as they are submitted.
- **Improved NLP Models** — Enhance aspect and sentiment analysis using newer NLP and deep learning approaches.


### Home Page
![Fake review detection](images/fake review detection ss.png)

### Fake Review Detection
![Fake Review Detection](images/fake-review.png)

### Hotel Comparison
![Hotel Comparison](images/hotel-comparison.png)
  
## 📄 Research Paper

**“Trip Trove: Comparative Review Analysis”**

Published and presented at **ICAML 2025**.
