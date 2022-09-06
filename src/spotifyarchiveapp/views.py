from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import spotipy
from spotipy import oauth2
from spotipy.oauth2 import SpotifyClientCredentials
import os
from .models import User
import datetime

# configure Spotipy API for either client credentials or authorization depending on flow
def initSpotipy(flow):
    SPOTIPY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
    SPOTIPY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
    if flow == "authorization":
        SPOTIPY_REDIRECT_URI = os.environ.get("SPOTIFY_REDIRECT_URI")
        SCOPE = "user-read-private playlist-modify-private"
        CACHE = ".spotipyoauthcache"
        global sp_oauth
        sp_oauth = oauth2.SpotifyOAuth(
            client_id=SPOTIPY_CLIENT_ID,
            client_secret=SPOTIPY_CLIENT_SECRET,
            redirect_uri=SPOTIPY_REDIRECT_URI,
            scope=SCOPE,
            cache_path=CACHE,
            show_dialog=True,
        )
    elif flow == "client-credentials":
        global client
        client = SpotifyClientCredentials(
            client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET
        )

# view for 404 page
def page_not_found(request, exception):
    if "error-redirect" in request.POST:
        return redirect(home)
    return render(request, "errors/404.html", {})

# view for 500 page
def error(request, exception=None):
    if "error-redirect" in request.POST:
        # remove any existing cache
        if os.path.exists(".spotipyoauthcache"):
            os.remove(".spotipyoauthcache")
        initSpotipy("client-credentials")
        request.session["fake_login"] = "True"
        return redirect(dashboard)
    return render(request, "errors/500.html", {})

# view for website home
def home(request):
    # remove any existing cache
    if os.path.exists(".spotipyoauthcache"):
        os.remove(".spotipyoauthcache")
    if os.path.exists(".cache"):
        os.remove(".cache")
    # handle login redirect
    if "log-in" in request.POST:
        if "fake_login" in request.session:
            request.session.pop("fake_login", None)
        initSpotipy("authorization")
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    # handle no login redirect
    if "no-log-in" in request.POST:
        initSpotipy("client-credentials")
        request.session["fake_login"] = "True"
        return redirect(dashboard)
    return render(request, "spotifyarchiveapp/home.html")

# view for website dashboard
def dashboard(request):
    global sp
    args = {}
    # handle dropdown http requests
    if "dashboard" not in request.POST:
        http = dropdownHTTP(request)
        if http is not None:
            return http
    # handle dashboard http requests
    http = dashboardHTTP(request, args)
    if http is not None:
        return http
    # handle non-login case
    if "fake_login" in request.session:
        args["fake_login"] = True
        sp = spotipy.Spotify(auth_manager=client)
    else:
        # handle login cases
        if request.GET.get("code"):
            sp_oauth.get_access_token(request.GET.get("code"))
            sp = spotipy.Spotify(auth_manager=sp_oauth)
        else:
            sp = spotipy.Spotify(auth_manager=sp_oauth)
    user = None
    if "fake_login" not in request.session:
        # get user info
        user = sp.current_user()
    # occurs during AJAX request
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return dashboardAJAX(request, user)
    # fill args dict with user info to be displayed in top right
    dashboardFillArgs(request, user, args)
    return render(request, "spotifyarchiveapp/dashboard.html", args)

# view for website success page
def success(request):
    # handle dropdown http requests
    http = dropdownHTTP(request)
    if http is not None:
        return http
    if "create-another" in request.POST:
        return redirect(dashboard)
    # create playlist in user's Spotify library
    if "playlist-tracks" in request.session:
        # generate playlist description
        description = "Playlist created using Spotify Archive. Seed Tracks: "
        for ind, t in enumerate(request.session["selected-tracks"]):
            if ind == len(request.session["selected-tracks"]) - 1:
                description += t["name"] + " by " + \
                    t["artists"][0]["name"] + "."
            else:
                description += t["name"] + " by " + \
                    t["artists"][0]["name"] + ", "
        # check if user provides playlist name, else use default name
        if "playlist-name" in request.session:
            playlist = sp.user_playlist_create(
                sp.current_user()["id"],
                request.session["playlist-name"],
                public=False,
                collaborative=False,
                description=description,
            )
        else:
            playlist = sp.user_playlist_create(
                sp.current_user()["id"],
                "Spotify Archive Playlist",
                public=False,
                collaborative=False,
                description=description,
            )
        # add tracks to playlist
        tracks = [t["id"] for t in request.session["playlist-tracks"]]
        sp.user_playlist_add_tracks(
            sp.current_user()["id"], playlist["id"], tracks, position=None
        )

        # add user to db if dne or if user exists add new playlist id to current list
        try:
            stats = User.objects.get(user_name=sp.current_user()["id"])
            stats.playlists.append(playlist["id"])
            stats.save()
        except User.DoesNotExist:
            User.objects.create(user_name=sp.current_user()[
                                "id"], join_date=datetime.date.today(), playlists=[playlist["id"]])
        # clear session vars
        request.session.flush()
    # needed in case user tries to access success page too early (redirects home in this case)
    try:
        # prepare args so that user icon and name is displayed in top right
        args = {}
        user = sp.current_user()
        args["display_name"] = user["display_name"]
        # check if any avi exists
        if len(user["images"]) > 0:
            args["avi_url"] = user["images"][0]["url"]
        return render(request, "spotifyarchiveapp/success.html", args)
    except:
        return redirect(home)

# view for website stats page
def stats(request):
    # handle dropdown http requests
    if "stats" not in request.POST:
        http = dropdownHTTP(request)
        if http is not None:
            return http
    # handle dashboard redirect button
    if "dashboard-redirect" in request.POST:
        return redirect(dashboard)
    # needed in case user tries to access success page too early (redirects home in this case)
    try:
        # prepare args so that user icon and name is displayed in top right
        args = {}
        user = sp.current_user()
        args["display_name"] = user["display_name"]
        # check if any avi exists
        if len(user["images"]) > 0:
            args["avi_url"] = user["images"][0]["url"]
        # check if user exists in db (this means user has created playlists with app before)
        try:
            # fetch user from db
            stats = User.objects.get(user_name=user["id"])
            args["user_exists"] = True
            args["join_date"] = stats.join_date.strftime("%B %d, %Y")
            # store playlist objects for args
            playlists = []
            # store existing playist id's to update user object in database
            updatedPlaylistIds = []
            # store tracks in set to count unique number of songs
            tracks = set()
            # iterate through playlists id's user has created
            for playlist in stats.playlists:
                # try to fetch playlist by id, if unable to it means playlist has been deleted
                try:
                    curr = sp.playlist(playlist)
                    playlists.append(curr)
                    updatedPlaylistIds.append(playlist)
                    for track in curr["tracks"]["items"]:
                        tracks.add(track["track"]["id"])
                except:
                    # playlist dne remove
                    pass
            # update db with existing playlists
            stats.playlists = updatedPlaylistIds
            stats.save()
            # fill args
            args["num_songs"] = len(tracks)
            args["num_playlists"] = len(updatedPlaylistIds)
            args["playlists"] = playlists
        except User.DoesNotExist:
            # prepare arg for html to use if user dne
            args["user_exists"] = False
        return render(request, "spotifyarchiveapp/stats.html", args)
    except:
        return redirect(home)

# function to that performs logout
def logout(request):
    # remove cache and session vars
    if os.path.exists(".spotipyoauthcache"):
        os.remove(".spotipyoauthcache")
    request.session.flush()
    # return to home page
    return redirect(home)

# function to handle AJAX requests for dashboard view
def dashboardAJAX(request, user):
    # handle AJAX search request
    if request.GET.get("action") == "search":
        # get search query if exists and use spotipy search call to get results
        query = request.GET.get("search", None)
        if query:
            results = sp.search(q=query, limit=10, type="track,artist")
            return JsonResponse({"results": results})
        else:
            return JsonResponse({"results": []})
    # handle AJAX track select request
    if request.GET.get("action") == "track-select":
        # get id of track to be selected
        trackID = request.GET.get("selectedTrackID", None)
        # use spotipy track call to get track object
        track = sp.track(track_id=trackID)
        # make selected-tracks key in request.session if not already made
        if "selected-tracks" in request.session:
            # insert track if not already selected
            if track not in request.session["selected-tracks"]:
                request.session["selected-tracks"].insert(0, track)
                # if there are more than 5 tracks, remove the first one
                if len(request.session["selected-tracks"]) > 5:
                    request.session["selected-tracks"].pop()
            else:
                return JsonResponse({"track": None})
        else:
            request.session["selected-tracks"] = [track]
        request.session.modified = True
        return JsonResponse({"track": track})
    # handle AJAX track deselect request
    if request.POST.get("action") == "track-deselect":
        # get track id and remove it from dict
        trackID = request.POST.get("trackDeselectID", None)
        request.session["selected-tracks"] = [
            i for i in request.session["selected-tracks"] if i["id"] != trackID
        ]
        # return None if there are not any selected tracks, True if there are tracks
        # this value is used to determine if a new recommended playlist needs to be fetched
        if len(request.session["selected-tracks"]) == 0:
            request.session.modified = True
            return JsonResponse({"success": None})
        return JsonResponse({"sucess": True})
    # handle AJAX new recommendation playlist request
    if request.GET.get("action") == "get-playlist":
        # create dict with all filter values
        dict = {}
        for key, value in request.GET.items():
            dict[key] = value
        # action value should not be used in recommend function
        dict.pop("action", None)
        if user is not None:
            dict["country"] = user["country"]
        else:
            dict["country"] = "US"
        # insert all selected track ids to a list for seed_tracks
        tracks = []
        for t in request.session["selected-tracks"]:
            tracks.append(t["id"])
        dict["seed_tracks"] = tracks
        # call spotipy recommendation function with our dict values
        recs = sp.recommendations(**dict)
        # populate session playlist-tracks var and return recs to javascript
        request.session["playlist-tracks"] = []
        for t in recs["tracks"]:
            request.session["playlist-tracks"].append(t)
        request.session.modified = True
        return JsonResponse({"playlist": recs})
    # handle AJAX playlist name change request
    if request.POST.get("action") == "playlist-name-change":
        request.session["playlist-name"] = request.POST.get(
            "playlistName", None)
        return HttpResponse("")
    # handle AJAX website mode change request
    if request.POST.get("action") == "mode-change":
        request.session["mode"] = request.POST.get("mode")
        return HttpResponse("")

# function to handle HTTP requests for dashboard view
def dashboardHTTP(request, args):
    # handle login
    if "log-in" in request.POST:
        if "fake_login" in request.session:
            request.session.pop("fake_login", None)
        initSpotipy("authorization")
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    # handle create playlist
    if "submitButton" in request.POST:
        if "playlist-tracks" in request.session and len(request.session["playlist-tracks"]) != 0:
            return redirect(success)
    # handle static search
    if "search" in request.GET:
        # get search query if exists and use spotipy search call to get results
        query = request.GET.get("search", None)
        if query:
            results = sp.search(q=query, limit=10, type="track,artist")
            args["results"] = results
            args["search_query"] = query
        return None

# function to fill args dict for dashboard view
def dashboardFillArgs(request, user, args):
    if user is not None:
        args["display_name"] = user["display_name"]
        # check if any avi exists
        if len(user["images"]) > 0:
            args["avi_url"] = user["images"][0]["url"]
    # update below args if tracks are selected
    if "selected-tracks" in request.session:
        if len(request.session["selected-tracks"]) != 0:
            # update selected tracks in args
            args["selected"] = request.session["selected-tracks"]
            # update playlist tracks in args
            if "playlist-tracks" in request.session:
                # when session has selected tracks variable (e.g on refresh) generate a new playlist
                tracks = []
                for t in request.session["selected-tracks"]:
                    tracks.append(t["id"])
                if user is not None:
                    recs = sp.recommendations(
                        seed_tracks=tracks, limit=50, country=user["country"]
                    )
                else:
                    recs = sp.recommendations(
                        seed_tracks=tracks, limit=50, country="US"
                    )
                request.session["playlist-tracks"] = []
                for t in recs["tracks"]:
                    request.session["playlist-tracks"].append(t)
                args["playlist"] = request.session["playlist-tracks"]
    # handle website mode in args
    if "mode" in request.session:
        args["mode"] = request.session["mode"]
    else:
        args["mode"] = "static"

# function to handle HTTP requests in dropdown menu
def dropdownHTTP(request):
    # handle dashboard
    if "dashboard" in request.POST:
        return redirect(dashboard)
    # handle stats
    if "stats" in request.POST:
        return redirect(stats)
    # handle logout
    if "logout" in request.POST:
        return logout(request)
    # return None if not handling any of above requests
    return None
