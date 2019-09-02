#encoding:utf-8
from flask import Flask
import json
import logging
from flask import current_app, Flask, redirect, request, session, url_for, render_template
import httplib2
import urllib
import hashlib
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
with open('client_secret.json') as f:
    df = json.load(f)
    app.config['client_id'] = df['client_id']
    app.config['client_secret'] = df['client_secret']

@app.route('/')
def top():
    return render_template('top.html')

@app.route('/login')
def login():
    client_id=app.config['client_id']
    url='https://github.com/login/oauth/authorize'
    redirect_uri = 'http://localhost:8080/oauthgithub'
    state = json.dumps({
        'random_key': hashlib.sha256(os.urandom(1024)).hexdigest(),
        'return_url': redirect_uri
    })
    session['state'] = state
    scope = 'user:email%20repo'
    return redirect(url + '?client_id='+client_id+'&state='+state+'&scope='+scope+'&redirect_uri='+redirect_uri)

@app.route('/logout')
def logout():
    del session['login']
    del session['token']
    session.modified = True
    return redirect('/')

@app.route('/oauthgithub')
def oauthgithub():
    state = request.args['state']
    if 'state' in session and session['state'] == state:
        code = request.args.get('code')
        http = httplib2.Http()
        body = {'client_id': app.config['client_id'], 'client_secret':app.config['client_secret'], 'code':code}
        resp, content = http.request("https://github.com/login/oauth/access_token",
                           method="POST",
                           headers={'Content-type': 'application/x-www-form-urlencoded'},
                           body=urllib.parse.urlencode(body))
        session['token'] = str(content).split('&')[0].split('=')[1]
        session['login'] = getUserInfo()['login']
    if 'state' in session:
        del session['state']
    return redirect('/')

@app.route('/user')
def user():
    if not 'login' in session:
        return redirect('/')
    return render_template('user.html', userInfo=getUserInfo())

def getUserInfo():
    http = httplib2.Http()
    resp, content = http.request('https://api.github.com/user',
                        headers={'Authorization': 'token ' + session['token']})
    return json.loads(content.decode('utf-8'))

@app.route('/repo')
def repo():
    if not 'login' in session:
        return redirect('/')
    http = httplib2.Http()
    resp, content = http.request('https://api.github.com/users/'+session['login']+'/repos',
                        headers={'Authorization': 'token ' + session['token']})
    repoList = json.loads(content.decode('utf-8'))
    return render_template('repo.html', repos=[x['name'] for x in repoList])

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
