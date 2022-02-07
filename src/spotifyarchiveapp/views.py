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

SPOTIPY_REDIRECT_URI = 'http://localhost:8000/home'
SCOPE = 'user-library-read'
CACHE = '.spotipyoauthcache'

sp_oauth = oauth2.SpotifyOAuth(
	SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET,
	SPOTIPY_REDIRECT_URI, scope=SCOPE, cache_path=CACHE
)

def login(request):
    #sp_oauth = oauth2.SpotifyOAuth(scope=scope,client_id=client_id,client_secret=client_secret,redirect_uri=redirect_uri,cache_path=cache)
    auth_url = sp_oauth.get_authorize_url()
    return render(request, 'spotifyarchiveapp/home.html', {'auth_url': auth_url})

def home(request):
    access_token = ""
    token_info = sp_oauth.get_cached_token()
    if token_info:
        print ("Found cached token!")
        access_token = token_info['access_token']
    #url = sp_oauth.get_authorize_url()
    #code = sp_oauth.parse_response_code(url)
    code = request.GET.get("code")
    #print('Code: ', code)
    token_info = sp_oauth.get_access_token(code)
    access_token = token_info['access_token']
    #print('Token Info: ',token_info)
    #print('Access Token: ',access_token)

    sp = spotipy.Spotify(auth=access_token)
    user = sp.current_user()
    print(user)
    return HttpResponse("Signed in!")

'''
def login(request):
    access_token = ""

    token_info = sp_oauth.get_cached_token()

    if token_info:
        print ("Found cached token!")
        access_token = token_info['access_token']
    else:
        #url = sp_oauth.get_authorize_url()
        #code = sp_oauth.parse_response_code(url)
        code = request.GET.get("code")
        if code:
            print ("Found Spotify auth code in Request URL! Trying to get valid access token...")
            token_info = sp_oauth.get_access_token(code)
            access_token = token_info['access_token']

    if access_token:
        print ("Access token available! Trying to get user information...")
        sp = spotipy.Spotify(access_token)
        results = sp.current_user()
        return HttpResponse("Found user: %s." % results)
        #return results
        #return render(request, 'pages/sign-in.html', {'results': tracks})
    #return HttpResponse("Could not find user")
    else:
        #return tmp()
        auth_url = getSPOauthURI()
        #print('hi')
        print(auth_url)
        return redirect(auth_url)
        #return HttpResponseRedirect(auth_url)
        #return HttpResponse("<a href='" + auth_url + "'>Login to Spotify</a>")


def getSPOauthURI():
    auth_url = sp_oauth.get_authorize_url()
    return auth_url
'''
