#encoding:utf-8
from flask import Flask
import json
import logging
from flask import current_app, Flask, redirect, request, session, url_for, render_template
import httplib2
import urllib

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
    id=app.config['client_id']
    url='https://github.com/login/oauth/authorize'
    scope = 'user:email%20repo'
    return redirect(url + '?client_id='+id+'&state=aabbcc&scope='+scope+'&redirect_uri=http://localhost:8080/oauthgithub')

@app.route('/logout')
def logout():
    del session['profile']
    del session['login']
    del session['token']
    session.modified = True
    return redirect('/')

@app.route('/oauthgithub')
def oauthgithub():
    code = request.args.get('code')
    state = request.args['state'].encode('utf-8')
    http = httplib2.Http()
    body = {'client_id': app.config['client_id'], 'client_secret':app.config['client_secret'], 'code':code}
    resp, content = http.request("https://github.com/login/oauth/access_token",
                       method="POST",
                       headers={'Content-type': 'application/x-www-form-urlencoded'},
                       body=urllib.parse.urlencode(body))
    token = str(content).split('&')[0].split('=')[1]
    session['token'] = token
    resp, content = http.request('https://api.github.com/user',
                        headers={'Authorization': 'token ' + token})
    aa = json.loads(content.decode('utf-8'))
    session['login'] = aa['login']
    session['profile'] = 'aa'
    return redirect('/')

@app.route('/user')
def user():
    http = httplib2.Http()
    token = session['token']
    resp, content = http.request('https://api.github.com/users/'+session['login'],
                        headers={'Authorization': 'token ' + token})
    userInfo = json.loads(content.decode('utf-8'))
    return render_template('user.html', userInfo=userInfo)

@app.route('/repo')
def token1():
    http = httplib2.Http()
    token = session['token']
    resp, content = http.request('https://api.github.com/users/'+session['login']+'/repos',
                        headers={'Authorization': 'token ' + token})
    repoList = json.loads(content.decode('utf-8'))
    #repos = []
    #for x in repoList:
    #    repos.append(x['name'])
    return render_template('repo.html', repos=[x['name'] for x in repoList])

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
