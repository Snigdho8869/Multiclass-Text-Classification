from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_mail import Mail, Message
import smtplib
import tensorflow
import re
import nltk
import numpy as np
import pandas as pd
import joblib
import json
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from textblob import Word


app = Flask(__name__, template_folder='templates', static_folder='static')


model = joblib.load('Text_LR.pkl')
count_vec = joblib.load('count_vect.pkl')
transformer = joblib.load('transformer.pkl')



@app.route('/')
def home():
    return render_template('index.html')

@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/contact.html')
def contact():
    return render_template('contact.html')

@app.route('/about.html')
def about():
    return render_template('about.html')

@app.route('/resources.html')
def resources():
    return render_template('resources.html')


@app.route('/suicide-ideation', methods=['POST'])
def predict():
    data = request.get_json(force=True)
    text = data['text']
    
    text_df = pd.DataFrame({'text': [text]})
    text_df['lower_case'] = text_df['text'].apply(lambda x: x.lower().strip().replace('\n', ' ').replace('\r', ' '))
    text_df['alphabetic'] = text_df['lower_case'].apply(lambda x: re.sub(r'[^a-zA-Z\']', ' ', x)).apply(lambda x: re.sub(r'[^\x00-\x7F]+', '', x))
    tokenizer = RegexpTokenizer(r'\w+')
    text_df['special_word'] = text_df.apply(lambda row: tokenizer.tokenize(row['alphabetic']), axis=1)
    stop = [word for word in stopwords.words('english') if word not in ["my","haven't"]]
    text_df['stop_words'] = text_df['special_word'].apply(lambda x: [item for item in x if item not in stop])
    text_df['stop_words'] = text_df['stop_words'].astype('str')
    text_df['short_word'] = text_df['stop_words'].str.findall('\w{2,}')
    text_df['text'] = text_df['short_word'].str.join(' ')
    text_df['text'] = text_df['text'].apply(lambda x: " ".join([Word(word).lemmatize() for word in x.split()]))

    text = count_vec.transform([text_df['text'][0]])
    text_vec = transformer.transform(text)
    prediction = model.predict(text_vec)
    prediction_list = prediction.tolist()
    response_dict = {'category': prediction_list}
    response_json = json.dumps(response_dict)
    response = app.response_class(response=response_json, status=200, mimetype='application/json')
    
    return response


@app.route('/send-email', methods=['POST'])
def send_email():

    name = request.form['name']
    email = request.form['email']
    message = request.form['message']
    
    subject = 'Contact Form Submission from ' + name
    body = 'Name: ' + name + '\nEmail: ' + email + '\nMessage: ' + message

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('zahidulislam2225@gmail.com', 'valb mmmn awhg snpd')
    
    server.sendmail('zahidulislam2225@gmail.com', 'rafin3600@gmail.com', subject + '\n\n' + body)
    server.quit()
    
    return render_template('thank-you.html')


if __name__ == '__main__':
    app.run(debug=True)