from audioop import reverse
import configparser
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.http import HttpResponse
import spotipy
import spotipy.util as util
from spotipy import oauth2
import os

config = configparser.ConfigParser()
config.read('config.cfg')
SPOTIPY_CLIENT_ID = config.get('SPOTIFY', 'CLIENT_ID')
SPOTIPY_CLIENT_SECRET = config.get('SPOTIFY', 'CLIENT_SECRET')

SPOTIPY_REDIRECT_URI = 'http://localhost:8000/dashboard/'
SCOPE = 'user-library-read'
CACHE = '.spotipyoauthcache'

sp_oauth = oauth2.SpotifyOAuth(
	client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET,
	redirect_uri=SPOTIPY_REDIRECT_URI, scope=SCOPE, cache_path=CACHE, 
    show_dialog=True
)

sp = spotipy.Spotify(auth_manager=sp_oauth)

def error404(request, exception):
    return render(request,'spotifyarchiveapp/error404.html')

def home(request):
    if(request.method == 'POST'):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    return render(request, 'spotifyarchiveapp/home.html')

def dashboard(request):
    if(request.GET.get('code')):
        token = sp_oauth.get_access_token(request.GET.get('code'))
    if('logout' in request.POST):
        os.remove('.spotipyoauthcache')
        try:
            del request.session['selected-tracks']
        except KeyError:
            pass
        return render(request, 'spotifyarchiveapp/home.html')
    if('submitButton' in request.POST):
        return redirect(playlist)
    user = sp.current_user()
    args = {}
    args["display_name"] = user["display_name"]
    args["avi_url"] = user["images"][0]["url"] 
    query = request.GET.get('search')
    if(query):
        results = sp.search(q=query, limit=10, type='track')
        args["results"]=results
    #if(request.method == 'POST'):
    if('trackSelect' in request.POST):
        trackID = request.POST.get("track-id")
        track = sp.track(track_id=trackID)
        if('selected-tracks' in request.session):
            if(track not in request.session['selected-tracks']):
                request.session['selected-tracks'].insert(0,track)
                if(len(request.session['selected-tracks']) > 5):
                    request.session['selected-tracks'].pop()
        else:
            request.session['selected-tracks'] = [track]
        request.session.modified = True
    if('selected-tracks' in request.session):
        args["selected"]= request.session['selected-tracks']
    return render(request, 'spotifyarchiveapp/dashboard.html', args)

def playlist(request):
    print('HERE')
    if('logout' in request.POST):
        os.remove('.spotipyoauthcache')
        try:
            del request.session['selected-tracks']
        except KeyError:
            pass
        return render(request, 'spotifyarchiveapp/home.html')
    #if('createButton' in request.POST):
        #create playlist
    user = sp.current_user()
    args = {}
    args["display_name"] = user["display_name"]
    args["avi_url"] = user["images"][0]["url"]
    tracks = []
    for track in request.session['selected-tracks']:
        tracks.append(track["id"])
    recs = sp.recommendations(seed_tracks=tracks, limit=100)
    args["results"] = recs['tracks']
    return render(request, 'spotifyarchiveapp/playlist.html', args)