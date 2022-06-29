from audioop import reverse
import configparser
from random import seed
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.http import HttpResponse, JsonResponse
import spotipy
import spotipy.util as util
from spotipy import oauth2
import os

config = configparser.ConfigParser()
config.read('config.cfg')
SPOTIPY_CLIENT_ID = config.get('SPOTIFY', 'CLIENT_ID')
SPOTIPY_CLIENT_SECRET = config.get('SPOTIFY', 'CLIENT_SECRET')

SPOTIPY_REDIRECT_URI = 'http://localhost:8000/dashboard/'
SCOPE = 'user-read-private playlist-modify-private'
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
    args = {}
    if(request.GET.get('code')):
        token = sp_oauth.get_access_token(request.GET.get('code'))
    if('logout' in request.POST):
        return logout(request)
    if('submitButton' in request.POST):
        if len(request.session['selected-tracks']) == 0: 
            args["error"]= True
        else:
            return redirect(playlist)
    user = sp.current_user()
    args["display_name"] = user["display_name"]
    args["avi_url"] = user["images"][0]["url"] 
    if(request.headers.get('X-Requested-With') == 'XMLHttpRequest'):
        if(request.GET.get('action') == 'search'):
            query = request.GET.get('search', None)
            if(query):
                results = sp.search(q=query, limit=10, type='track,artist')
                return JsonResponse({'results':results})
            else:
                return JsonResponse({'results': []})
        if(request.GET.get('action') == 'track-select'):
            trackID = request.GET.get('selectedTrackID', None)
            track = sp.track(track_id=trackID)
            if('selected-tracks' in request.session):
                if(track not in request.session['selected-tracks']):
                    request.session['selected-tracks'].insert(0,track)
                    if(len(request.session['selected-tracks']) > 5):
                        request.session['selected-tracks'].pop()
                else:
                    return JsonResponse({'track': None})
            else:
                request.session['selected-tracks'] = [track]
            request.session.modified = True
            return JsonResponse({'track':track})
        if(request.POST.get('action') == 'track-deselect'):
            trackID = request.POST.get("trackDeselectID", None)
            request.session['selected-tracks'] = [i for i in request.session['selected-tracks'] if i['id'] != trackID]
            request.session['playlist-tracks'] = []
            if(len(request.session['selected-tracks']) == 0):
                request.session.modified = True
                return JsonResponse({'success': None})
            return JsonResponse({'sucess': True})
        if(request.GET.get('action') == 'get-playlist'):
            dict = {}
            for key, value in request.GET.items():
                dict[key] = value
            dict.pop('action', None)
            dict['country'] = user['country']
            tracks = []
            for t in request.session['selected-tracks']:
                tracks.append(t["id"])
            dict['seed_tracks'] = tracks
            recs = sp.recommendations(**dict)
            request.session['playlist-tracks'] = []
            print(len(recs['tracks']))
            for t in recs['tracks']:
                request.session['playlist-tracks'].append(t)
            request.session.modified = True
            return JsonResponse({'playlist':recs})
    if('selected-tracks' in request.session):
        args["selected"] = request.session['selected-tracks']
    if('playlist-tracks' in request.session):
        tracks = []
        for t in request.session['selected-tracks']:
            tracks.append(t["id"])
        recs = sp.recommendations(seed_tracks=tracks, limit=50, country=user['country'])
        request.session['playlist-tracks'] = []
        print(len(recs['tracks']))
        for t in recs['tracks']:
            request.session['playlist-tracks'].append(t)
        args["playlist"] = request.session['playlist-tracks']
    return render(request, 'spotifyarchiveapp/dashboard.html', args)

def playlist(request):
    if('logout' in request.POST):
        del request.session['playlist-tracks']
        del request.session['selected-tracks']
    if('editButton' in request.POST):
        return redirect(dashboard)
    if('createButton' in request.POST):
        playlist = sp.user_playlist_create(sp.current_user()["id"], "Spotify Archive Playlist", public=False, collaborative=False, description='Playlist created using Spotify Archive.')
        sp.user_playlist_add_tracks(sp.current_user()["id"], playlist["id"], request.session['playlist-tracks'], position=None)
        del request.session['playlist-tracks']
        del request.session['selected-tracks']
        return redirect(success)
    user = sp.current_user()
    args = {}
    args["display_name"] = user["display_name"]
    args["avi_url"] = user["images"][0]["url"]
    tracks = []
    for track in request.session['selected-tracks']:
        tracks.append(track["id"])
    recs = sp.recommendations(seed_tracks=tracks, limit=100, market=user["country"])
    request.session['playlist-tracks'] = []
    for track in recs['tracks']:
        request.session['playlist-tracks'].append(track['id'])
    request.session.modified = True
    args["results"] = recs['tracks']
    return render(request, 'spotifyarchiveapp/playlist.html', args)

def success(request):
    if('logout' in request.POST):
        return logout(request)
    if('create-another' in request.POST):
        return redirect(dashboard)
    user = sp.current_user()
    args = {}
    args["display_name"] = user["display_name"]
    args["avi_url"] = user["images"][0]["url"]
    return render(request, 'spotifyarchiveapp/success.html', args)

def logout(request):
    os.remove('.spotipyoauthcache')
    try:
        del request.session['selected-tracks']
    except KeyError:
        pass
    return redirect(home)