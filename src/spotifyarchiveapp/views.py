import configparser
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.http import HttpResponse
import spotipy
import spotipy.util as util
from spotipy import oauth2

config = configparser.ConfigParser()
config.read('config.cfg')
SPOTIPY_CLIENT_ID = config.get('SPOTIFY', 'CLIENT_ID')
SPOTIPY_CLIENT_SECRET = config.get('SPOTIFY', 'CLIENT_SECRET')

SPOTIPY_REDIRECT_URI = 'http://localhost:8000/dashboard/'
SCOPE = 'user-library-read'
CACHE = '.spotipyoauthcache'

sp_oauth = oauth2.SpotifyOAuth(
	client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET,
	redirect_uri=SPOTIPY_REDIRECT_URI, scope=SCOPE, cache_path=CACHE
)

def error404(request, exception):
    return render(request,'spotifyarchiveapp/error404.html')

def home(request):
    if(request.method == 'POST'):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    return render(request, 'spotifyarchiveapp/home.html')

def dashboard(request):
    token_info = sp_oauth.get_access_token(code)
    access_token = token_info['access_token']
    sp = spotipy.Spotify(access_token)
    user = sp.current_user()
    #args = {}
    #args["display_name"] = user["display_name"]
    #args["avi_url"] = user["images"]["url"] 
    return render(request, 'spotifyarchiveapp/dashboard.html',user)

