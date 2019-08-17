from flask import Flask
import json
import logging

from flask import current_app, Flask, redirect, request, session, url_for, render_template
import httplib2
# [START include]
from oauth2client.contrib.flask_util import UserOAuth2

oauth2 = UserOAuth2()
app = Flask(__name__)
with open('client_secret.json') as f:
    df = json.load(f)
    app.config['SECRET_KEY'] = 'secret'
    app.config['GOOGLE_OAUTH2_CLIENT_ID'] = df['web']['client_id']
    app.config['GOOGLE_OAUTH2_CLIENT_SECRET'] = df['web']['client_secret']

@app.route('/')
def top():
    maillist = []
    if 'access_token' in session and 'profile' in session:
        http = httplib2.Http()
        resp, content = http.request(
            'https://www.googleapis.com/gmail/v1/users/'+ session['profile']['email'] +'/messages?maxResults=3&access_token=' + session['access_token'])
        if resp.status != 200:
            current_app.logger.error(
                "Error gmail api: \n%s: %s", resp, content)
            return None
        conj = json.loads(content.decode('utf-8'))
        #print(conj['messages'][0]['id'])
        for message in conj['messages']:
            resp, content = http.request(
                'https://www.googleapis.com/gmail/v1/users/'+ session['profile']['email'] +'/messages/'+ message['id'] +'?access_token=' + session['access_token'])
            if resp.status != 200:
                current_app.logger.error(
                    "Error gmail api: \n%s: %s", resp, content)
                return None
            conj2 = json.loads(content.decode('utf-8'))
            for x in conj2['payload']['headers']:
                if x['name'] == 'From':
                    print(x['value'])
                    maillist.append(x['value'])
            print(conj2['snippet'])
            maillist.append(conj2['snippet'])
            print('')
    return render_template('top.html', maillist=maillist)

@app.route('/logout')
def logout():
    del session['profile']
    session.modified = True
    oauth2.storage.delete()
    return render_template('top.html')

def _request_user_info(credentials):
    print('**********************_request_user_info start')
    print(dir(credentials))
    print('**********************_request_user_info start2')
    print(credentials.access_token)
    print('**********************_request_user_info end')
    """
    Makes an HTTP request to the Google OAuth2 API to retrieve the user's basic
    profile information, including full name and photo, and stores it in the
    Flask session.
    """
    http = httplib2.Http()
    credentials.authorize(http)
    resp, content = http.request(
        'https://www.googleapis.com/oauth2/v3/userinfo')

    if resp.status != 200:
        current_app.logger.error(
            "Error while obtaining user profile: \n%s: %s", resp, content)
        return None
    session['profile'] = json.loads(content.decode('utf-8'))
    session['access_token'] = credentials.access_token
    print(content.decode('utf-8'))

oauth2.init_app(
        app,
        scopes=['email', 'profile', 'https://www.googleapis.com/auth/gmail.readonly'],
        authorize_callback=_request_user_info)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
