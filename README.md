# Senti.co | Advanced Sentiment Intelligence Platform

**Senti.co** is a professional-grade web application designed to transform unstructured text into quantitative emotional data. By utilizing Machine Learning and Natural Language Processing (NLP), Senti.co provides businesses and developers with a deep understanding of linguistic sentiment.

---

## 🛠 Tech Stack

* **Backend:** Python / Flask
* **Security:** Werkzeug (PBKDF2 Password Hashing)
* **Machine Learning:** Scikit-Learn (TF-IDF Vectorization & Classification)
* **Frontend:** Tailwind CSS (Modern, Responsive UI)
* **Data Handling:** NLP-based text preprocessing

---

## 📋 Core Modules

The platform is architected around four primary user experiences:

### 1. **Home**

The landing interface that introduces users to the Senti.co ecosystem, highlighting the importance of sentiment intelligence in the modern digital landscape.

### 2. **Analytics Dashboard**

The engine of the application. Users can input large blocks of text to receive:

* **Sentiment Distribution:** A precise percentage breakdown of **Positive**, **Neutral**, and **Negative** tones.
* **Dominant Sentiment:** The primary emotional classification calculated by the ML model.
* **Keyword Extraction:** Identification of the most influential tokens (terms) based on the **TF-IDF Vectorizer**.

### 3. **Use Cases**

An interactive library of flashcards demonstrating real-world applications, including:

* Customer Feedback Analysis
* Social Media Brand Monitoring
* Market Research Trends

### 4. **Support & Help**

A streamlined communication channel for user inquiries and technical support.

---

## 🔒 Security & Authentication

Senti.co implements enterprise-standard security protocols:

* **User Authentication:** Full Register/Login flow.
* **Password Protection:** Passwords are never stored in plain text; they are hashed using **Werkzeug's** cryptographic security primitives to ensure data privacy.

---

## 🚀 Getting Started

### Prerequisites

* Python 3.x
* Pip (Python Package Manager)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/lakshitachawla/sentiment-analysis.git
cd sentiment-analysis

```


2. **Set up Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

```


3. **Install Dependencies**
```bash
pip install -r requirements.txt

```


4. **Launch the Application**
```bash
flask run

```


*Navigate to `http://127.0.0.1:5000` in your browser.*

---

## 📂 Project Structure

```text
├── app.py              # Main Flask application logic
├── setup_db.py         # MYSQL DataBase Setup
├── config.py       
├── model_training/     # Pre-trained ML models & TF-IDF Vectorizer
├── static/             # Tailwind CSS & static assets
├── templates/          # Jinja2 HTML templates (Home, Dashboard, etc.)
└── requirements.txt    # Project dependencies

---
