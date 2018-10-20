#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime
from flask_cors import CORS
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import math
# from flask.ext.sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from forms import *
import os

import io

# Imports the Google Cloud client library
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

# Instantiates a client
client = speech.SpeechClient()

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
CORS(app)
app.config.from_object('config')
#db = SQLAlchemy(app)

# Automatically tear down SQLAlchemy.
'''
@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()
'''

# Login required decorator.
'''
def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap
'''

# Create list of calls
calls = [
    {
        'time': str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        'text': 'Help!',
        'sentiment': 7, 
        'confidence': 8
    },
    {
        'time': str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        'text': 'I\'m lonely.',
        'sentiment': 5, 
        'confidence': 9
    }
]
#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def home():
    calls.sort(key = lambda x: x['sentiment'], reverse = True)
    return render_template('pages/placeholder.home.html', calls_data = calls)


@app.route('/about')
def about():
    return render_template('pages/placeholder.about.html')


@app.route('/login')
def login():
    form = LoginForm(request.form)
    return render_template('forms/login.html', form=form)


@app.route('/register')
def register():
    form = RegisterForm(request.form)
    return render_template('forms/register.html', form=form)


@app.route('/forgot')
def forgot():
    form = ForgotForm(request.form)
    return render_template('forms/forgot.html', form=form)

@app.route('/recorder')
def recorder():
    form = ForgotForm(request.form)
    return render_template("Recorderjs-master/examples/example_simple_exportwav.html", form=form)

# Error handlers.


@app.errorhandler(500)
def internal_error(error):
    #db_session.rollback()
    return render_template('errors/500.html'), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# List for request from client

@app.route('/api/newcall', methods = ['POST'])
def create_call():
    
    # if not request.json:
    #     abort(400)
        
    # return redirect(url_for('login'))

    blob = request.files['audio_data'].read()
    # blob.save(os.path.join())
    text = transcribe(blob)
    print(text.transcript)
    print(text.confidence)

    analyzer = SentimentIntensityAnalyzer()
    vs = analyzer.polarity_scores(text.transcript)
    print("{:-<65} {}".format(text.transcript, str(vs)))
    
    
    call = {
        'id': str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        'text': text.transcript,
        'sentiment': round(10*vs['neg']),
        'confidence': round(10*text.confidence)
    }
    calls.append(call)

    return jsonify({'call': call}), 201

def transcribe(blob):
    
    client = speech.SpeechClient()
    content = blob
    audio = types.RecognitionAudio(content=content)

    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=48000,
        language_code='en-US')

    # Detects speech in the audio file
    response = client.recognize(config, audio)

    for result in response.results:
        print(result)
        print('Transcript: {}'.format(result.alternatives[0].transcript))

    return(result.alternatives[0])
#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
# if __name__ == '__main__':
#     app.run()

# Or specify port manually:

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)

