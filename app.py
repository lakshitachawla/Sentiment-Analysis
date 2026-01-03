import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, flash, session, g, jsonify
from werkzeug.security import generate_password_hash, check_password_hash 
from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE 
import re
from functools import wraps
import random 
import joblib 
import string 
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# NLTK Resources Check
try:
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    print("NLP tools (Stopwords, Lemmatizer) initialized.")
except Exception as e:
    print(f"Warning: NLTK resources might not be available. Please check environment. {e}")
    stop_words = set()
    lemmatizer = None

# Main Application
app = Flask(__name__)
app.secret_key = 'admin240825' 

# Database Connection
def get_db():
    if 'db_conn' not in g:
        try:
            g.db_conn = mysql.connector.connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DATABASE
            )
        except mysql.connector.Error as err:
            print(f"Database connection error: {err}")
            flash('Database connection failed.', 'error')
            return None
    return g.db_conn

#Loading the trained model and vectorizer once when the app starts
try:
    LOADED_VECTORIZER = joblib.load('model_training\\tfidf_vectorizer.joblib')
    LOADED_MODEL = joblib.load('model_training\\sentiment_model.joblib')
    print("ML Model and Vectorizer loaded successfully.")
except FileNotFoundError:
    LOADED_VECTORIZER = None
    LOADED_MODEL = None
    print("WARNING: Model artifacts (joblib files) not found. Sentiment analysis will use mock data.")


# NLP PreProcessing Function for Model
def clean_text_for_prediction(text):
    if not isinstance(text, str):
        return ''
    
    text = text.lower()
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = re.sub(r'\d+', '', text)
    
    tokens = nltk.word_tokenize(text)

    cleaned_tokens = [
        lemmatizer.lemmatize(token)
        for token in tokens
        if token.isalpha() and token not in stop_words
    ]
    
    return ' '.join(cleaned_tokens)

@app.teardown_appcontext
def close_db(e=None):
    conn = g.pop('db_conn', None)
    if conn is not None:
        conn.close()


# Decorator to check if a user is logged in before accessing a route 
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('You need to log in to access this page.', 'warning')
            return redirect(url_for('serve_login'))
        return f(*args, **kwargs)
    return decorated_function

#Mock Data for Initial Request to the Dashboard
def get_sentiment_data():
    data = {
        'positive_count': random.randint(300, 600),
        'negative_count': random.randint(50, 200),
        'neutral_count': random.randint(100, 300),
        'latest_score': round(random.uniform(0.65, 0.95), 2),
        'recent_comments': [
            {'text': 'The product update is fantastic and seamless!', 'sentiment': 'Positive'},
            {'text': 'I encountered a major bug during checkout, very frustrating.', 'sentiment': 'Negative'},
            {'text': 'The interface is fine, nothing particularly new or exciting.', 'sentiment': 'Neutral'},
            {'text': 'Exceptional customer service—they solved my issue immediately.', 'sentiment': 'Positive'},
        ]
    }
    data['total_count'] = data['positive_count'] + data['negative_count'] + data['neutral_count']
    return data

# Routes for the Website
@app.route('/', methods=['GET'])

# Main Home Page Route
@app.route('/index', methods=['GET'])
def serve_index():
    return render_template('index.html')

# User Registration Route 
@app.route('/register', methods=['GET', 'POST'])
def serve_register():
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        phone = request.form.get('phone')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not all([name, username, email, password, confirm_password]):
            flash('All fields marked * are required.', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')
        
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address format.', 'error')
            return render_template('register.html')

        conn = get_db()
        if conn is None:
            return render_template('register.html')
            
        cursor = conn.cursor(dictionary=True)
        check_query = "SELECT * FROM users WHERE email = %s OR username = %s"
        cursor.execute(check_query, (email, username))
        existing_user = cursor.fetchone()
        
        if existing_user:
            if existing_user['email'] == email:
                flash('An account with this email already exists.', 'error')
            elif existing_user['username'] == username:
                flash('This username is already taken.', 'error')
            cursor.close()
            return render_template('register.html')
            
        hashed_password = generate_password_hash(password)
        insert_query = """
        INSERT INTO users (name, username, phone, email, password_hash)
        VALUES (%s, %s, %s, %s, %s)
        """
        user_data = (name, username, phone, email, hashed_password)
        
        try:
            cursor.execute(insert_query, user_data)
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('serve_login'))
        except mysql.connector.Error as err:
            flash(f"Database error during registration: {err.msg}", 'error')
            return render_template('register.html')
        finally:
            cursor.close()

    return render_template('register.html')

# User Login Route 
@app.route('/login', methods=['GET', 'POST'])
def serve_login():
    if request.method == 'POST':
        identifier = request.form.get('identifier') 
        password = request.form.get('password')

        if not identifier or not password:
            flash('Both username/email and password are required.', 'error')
            return render_template('login.html')

        conn = get_db()
        if conn is None:
            return render_template('login.html') 

        cursor = conn.cursor(dictionary=True)
        query = "SELECT id, name, username, email, password_hash FROM users WHERE username = %s OR email = %s"
        cursor.execute(query, (identifier, identifier))
        user = cursor.fetchone()
        cursor.close()

        if user and check_password_hash(user['password_hash'], password):
            session['logged_in'] = True 
            session['user_id'] = user['id']
            session['name'] = user['name'] 
            session['username'] = user['username']

            flash(f'Welcome back, {user["name"]}!', 'success')
            return redirect(url_for('serve_dashboard'))
        else:
            flash('Invalid username/email or password.', 'error')
            return render_template('login.html')

    return render_template('login.html') 

# Dashboard Page Route
@app.route('/dashboard', methods=['GET'])
@login_required
def serve_dashboard():
    data = get_sentiment_data()
    analysis_data = None
    
    #Analysis results are temporarily stored in 'g' (from the POST /analyze route)
    if hasattr(g, 'results'):
        analysis_data = {
            'analysis_text': getattr(g, 'analysis_text', ''),
            'results': g.results
        }
    
    return render_template('dashboard.html', data=data, analysis_data=analysis_data)

# Analyze Sentiments Route 
@app.route('/analyze', methods=['POST'])
@login_required
#Analyzes Sentiments using the ML Model
def analyze_sentiment():
    analysis_text = request.form.get('analysis_text', '').strip()

    if not analysis_text:
        flash('Please enter text to analyze.', 'warning')
        return redirect(url_for('serve_dashboard'))
    
    MODEL_CLASSES = ['negative', 'neutral', 'positive'] 
    if LOADED_MODEL is None or LOADED_VECTORIZER is None:
        flash('Error: ML model failed to load. Using mock analysis.', 'error')
        positive_pct = 30.0
        neutral_pct = 40.0
        negative_pct = 30.0
        main_sentiment = 'Neutral'
        keywords = []

    else:
        cleaned_text = clean_text_for_prediction(analysis_text)
        text_tfidf = LOADED_VECTORIZER.transform([cleaned_text])
        predicted_label = LOADED_MODEL.predict(text_tfidf)[0]

        probabilities = LOADED_MODEL.predict_proba(text_tfidf)[0]
        proba_dict = dict(zip(MODEL_CLASSES, probabilities))

        tokens = cleaned_text.split()
        word_counts = {}
        for word in tokens:
            word_counts[word] = word_counts.get(word, 0) + 1

        sorted_keywords = sorted(word_counts.items(), key=lambda item: item[1], reverse=True)
        keywords = [item[0] for item in sorted_keywords[:5]]

        #Dynamic Percentage Formatting (using actual probabilities)
        positive_pct = round(proba_dict.get('positive', 0.0) * 100, 2)
        neutral_pct = round(proba_dict.get('neutral', 0.0) * 100, 2)
        negative_pct = round(proba_dict.get('negative', 0.0) * 100, 2)
        main_sentiment = predicted_label.capitalize()

        # Storing results and original text in Flask's 'g' object
        g.analysis_text = analysis_text
        g.results = {
            'positive': positive_pct,
            'neutral': neutral_pct,
            'negative': negative_pct,
            'main_sentiment': main_sentiment,
            'keywords': keywords
        }

    flash('Sentiment analysis complete!', 'success')
    return serve_dashboard()

# Use Cases Page Route
@app.route('/use_cases', methods=['GET'])
def serve_use_cases():
    return render_template('use_cases.html')

# Help Page Route
@app.route('/help', methods=['GET'])
def serve_help():
    """Renders the Help page (help.html)."""
    return render_template('help.html')

#Logging Out User and Clearing the Session 
@app.route('/logout')
def logout_user():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    session.pop('name', None)
    session.pop('username', None)
    flash('You have been successfully logged out.', 'info')
    return redirect(url_for('serve_index'))

# Status of User for Navbar of Pages
@app.route('/api/userinfo')
def api_userinfo():
    if session.get('logged_in'):
        return jsonify({
            'logged_in': True,
            'name': session.get('name'),
            'username': session.get('username')
        })
    return jsonify({'logged_in': False})


if __name__ == '__main__':
    app.run(debug=True)