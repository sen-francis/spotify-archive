//function to handle dropdown menu in top right
function dropdown() {
    //if menu already open
    if (document.getElementById("drop-arrow").textContent == "\u25B2") {
        document.getElementById("drop-arrow").innerHTML = "&#9660";
        document.getElementById("drop-content").style.display = "none";
    } else {
        document.getElementById("drop-arrow").innerHTML = "&#9650";
        document.getElementById("drop-content").style.display = "block";
    }
}

//debounce function
function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction() {
        let context = this;
        let args = arguments;
        let later = function () {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        let callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

//search function, sends AJAX GET request to python code to fetch search results
//declare global variable to track if there is a previously active AJAX request
let searchRequest = null;
function search() {
	if(static){
		return;
	}
	let query = document.getElementById("search-bar").value;
	searchRequest = $.ajax({
		method: "GET",
		url: "/dashboard/",
		data: {
			search: query,
			action: "search",
		},
		beforeSend: function () {
			//NOTE: this block executes before the request.
			//if there is a previous request, abort and continue with the current request
			if (searchRequest != null) {
				searchRequest.abort();
				searchRequest = null;
			}
		},
		success: function (data) {
			document.getElementById("search-tracklist").innerHTML = "";
			if (query == "") {
				return;
			}
			for (track of data.results.tracks.items) {
				trackCreate(track, "searchTrack");
			}
		},
		error: function (error) {
			console.log("[ERROR]: " + error);
		},
	});
}

//calls search function with 275ms debounce, used as oninput function for search bar
const processSearch = debounce(search, 275);


//track select function, sends AJAX GET request to python code to retrieve the track object
function trackSelect(element) {
    let selectedTrackID = element.firstElementChild.value;
    $.ajax({
        method: "GET",
        url: "/dashboard/",
        data: { selectedTrackID: selectedTrackID, action: "track-select" },
        success: function (data) {
            track = data.track;
            if (!track) {
                return;
            }
            //add track object to selected tracks div
            trackCreate(track, "selectTrack");
            //fetch a new recommendation playlist with updated tracks
            if (!static) {
                getPlaylist();
            } else {
                playlistChanged = true;
            }
        },
        error: function (error) {
            console.log("[ERROR]: " + error);
        },
    });
}

//track de-select function, sends AJAX POST request to python code to deselect the track from session vars
function trackDeselect(element) {
    let trackID = element.firstElementChild.value;
    const csrftoken = document.querySelector("[name=csrfmiddlewaretoken]").value;
    $.ajax({
        method: "POST",
        url: "/dashboard/",
        data: {
            trackDeselectID: trackID,
            action: "track-deselect",
            csrfmiddlewaretoken: csrftoken,
        },
        success: function (data) {
            //remove track from html
            document.getElementById("selected-tracklist").removeChild(element);
            //if there are still selected tracks, fetch a new recommendation playlist
            if (document.getElementById("selected-tracklist").childElementCount > 0) {
                if (!static) {
                    getPlaylist();
                } else {
                    playlistChanged = true;
                }
            } else {
                //clear recommended playlist section
                let playlist = document.getElementById("playlist-tracklist");
                while (playlist.hasChildNodes()) {
                    playlist.removeChild(playlist.firstChild);
                }
            }
        },
        error: function (error) {
            console.log("[ERROR]: " + error);
        },
    });
}

//function to create a track in HMTL
//trackType var dictates where in DOM track is added and what function the onclick event points to
function trackCreate(track, trackType) {
    //create button
    let trackButton = document.createElement("button");
    //give class based on type of track
    if (trackType == "playlistTrack") {
        trackButton.classList.add("playlist-track");
    } else {
        trackButton.classList.add("track");
    }
    trackButton.type = "submit";
    //give onclick function based on type of track
    if (trackType == "selectTrack") {
        trackButton.onclick = function () {
            trackDeselect(this);
        };
    } else if (trackType == "searchTrack") {
        trackButton.onclick = function () {
            trackSelect(this);
        };
    }
    //put track id in a hidden element so can be accessed via javascript
    let hiddenTrackID = document.createElement("input");
    hiddenTrackID.type = "hidden";
    hiddenTrackID.name = "track-id";
    hiddenTrackID.id = "track-id";
    hiddenTrackID.value = track["id"];
    trackButton.appendChild(hiddenTrackID);

    //create track attributes: image, title and artists
    let trackIMG = document.createElement("img");
    trackIMG.classList.add("track-img");
    trackIMG.src = track["album"]["images"][0]["url"];
    trackButton.appendChild(trackIMG);
    let trackTitle = document.createElement("div");
    trackTitle.classList.add("track-title");
    trackButton.appendChild(trackTitle);
    let trackName = document.createElement("p");
    trackName.appendChild(document.createTextNode(track["name"]));
    trackTitle.appendChild(trackName);
    let trackArtists = document.createElement("div");
    trackArtists.classList.add("track-artists");
    trackTitle.appendChild(trackArtists);
    let i = 0;
    for (artist of track["artists"]) {
        if (i == track["artists"].length - 1) {
            let trackArtist = document.createElement("p");
            trackArtist.appendChild(document.createTextNode(artist["name"]));
            trackArtists.appendChild(trackArtist);
        } else {
            let trackArtist = document.createElement("p");
            trackArtist.appendChild(document.createTextNode(artist["name"] + ",\u00A0"));
            trackArtists.appendChild(trackArtist);
        }
        i++;
    }
    //determine what div track is added to based on trackType
    if (trackType == "selectTrack") {
        let selectedTracklist = document.getElementById("selected-tracklist");
        selectedTracklist.prepend(trackButton);
        //if more than 5 selected tracks, remove one
        if (selectedTracklist.childElementCount > 5) {
            selectedTracklist.removeChild(selectedTracklist.lastElementChild);
        }
    } else if (trackType == "searchTrack") {
        document.getElementById("search-tracklist").appendChild(trackButton);
    } else if (trackType == "playlistTrack") {
        document.getElementById("playlist-tracklist").appendChild(trackButton);
    }
}

//function updates recommended playlist in HTML DOM
function updatePlaylist(data) {
    //clear old playlist
    let playlist = document.getElementById("playlist-tracklist");
    while (playlist.hasChildNodes()) {
        playlist.removeChild(playlist.firstChild);
    }
    //add new tracks to playlist
    for (track of data.playlist.tracks) {
        trackCreate(track, "playlistTrack");
    }
}

//function called when recommended playlist needs to be updated
//sends AJAX GET request to python code to get a new recommendation playlist based on new playlist details
//declare global variable to track if there is a previously active AJAX request
let getPlaylistRequest = null;
function getPlaylist() {
    //only execute if there are selected tracks
    if (document.getElementById("selected-tracklist").childElementCount > 0) {
        //create dictionary object
        dict = createFilterDict();
        dict["action"] = "get-playlist";
        getPlaylistRequest = $.ajax({
            method: "GET",
            url: "/dashboard/",
            data: dict,
            beforeSend: function () {
                //NOTE: this block executes before the request
                //if there is a previous request, abort and continue with the current request
                if (getPlaylistRequest != null) {
                    getPlaylistRequest.abort();
                    getPlaylistRequest = null;
                }
                //make loading spinner visible and change opacity of track list (shows playlist is being updated)
                document.getElementById("loading-spinner").style.display = "inline-block";
                document.getElementById("playlist-tracklist").style.opacity = "0.5";
                //allow no pointer events while playlist updating
                document.body.style.pointerEvents = "none";
            },
            success: function (data) {
                updatePlaylist(data);
                //once playlist is done updating, revert tracklist opacity and hide loading spinner
                //allow pointer events again
                document.getElementById("loading-spinner").style.display = "none";
                document.getElementById("playlist-tracklist").style.opacity = "1";
                document.body.style.pointerEvents = "auto";
				playlistChanged = false;
            },
            error: function (error) {
                console.log("[ERROR]: " + error);
            },
        });
    }
}

//function create dictionary with playlist details and tunable track attribute values (if checked)
function createFilterDict() {
    dict = {};
    dict["limit"] = document.getElementById("numTracksInput").value;
    if (document.getElementById("acousticCheck").checked) {
        dict["target_acousticness"] = document.getElementById("acousticInput").value;
    }
    if (document.getElementById("danceCheck").checked) {
        dict["target_danceability"] = document.getElementById("danceInput").value;
    }
    if (document.getElementById("energyCheck").checked) {
        dict["target_energy"] = document.getElementById("energyInput").value;
    }
    if (document.getElementById("instrumentalCheck").checked) {
        dict["target_intrumentalness"] = document.getElementById("instrumentalInput").value;
    }
    if (document.getElementById("keyCheck").checked) {
        dict["target_key"] = document.getElementById("keyInput").value;
    }
    if (document.getElementById("liveCheck").checked) {
        dict["target_liveness"] = document.getElementById("liveInput").value;
    }
    if (document.getElementById("modeCheck").checked) {
        dict["target_mode"] = document.getElementById("modeInput").value;
    }
    if (document.getElementById("popularCheck").checked) {
        dict["target_popularity"] = document.getElementById("popularInput").value;
    }
    if (document.getElementById("speechCheck").checked) {
        dict["target_speechiness"] = document.getElementById("speechInput").value;
    }
    if (document.getElementById("tempoCheck").checked) {
        dict["target_tempo"] = document.getElementById("tempoInput").value;
    }
    if (document.getElementById("timeSigCheck").checked) {
        dict["target_time_signature"] = document.getElementById("timeSigInput").value;
    }
    if (document.getElementById("valenceCheck").checked) {
        dict["target_valence"] = document.getElementById("valenceInput").value;
    }
    return dict;
}

//calls getPlaylist function with 275ms debounce, used as onchange funnction for numTracks
const processNumTracksChange = debounce(numTracksChange, 275);

function numTracksChange(){
    if (!static) {
        getPlaylist();
    } else {
        playlistChanged = true;
    }
}

//function called when a tunable track attribute is enabled or diasbled
//changes color of range input and calls getPlaylist() to update playlist
function tunableTrackStatusChange(element) {
    if (element.checked) {
        element.parentElement.parentElement.lastElementChild.firstElementChild.style.background = "green";
    } else {
        element.parentElement.parentElement.lastElementChild.firstElementChild.style.background = "darkgrey";
    }
    if (!static) {
        getPlaylist();
    } else {
        playlistChanged = true;
    }
}

//function called when tunable track input range slider or number input changes
//if the attribute is enabled, then update playlist via getPlaylist()
function tunableTrackInputChange(element) {
    if (element.parentElement.parentElement.firstElementChild.lastElementChild.checked) {
        if (!static) {
            getPlaylist();
        } else {
            playlistChanged = true;
        }
    }
}

//calls tunableTrackInputChange function with 275ms debounce, used as onchange funnction for tunableTrackInput (number and range)
const processTunableTrackInputChange = debounce(tunableTrackInputChange, 275);

//function sends a AJAX POST request to python code to update playlist name is session var
//declare global variable to track if there is a previously active AJAX request
let playlistNameChangeRequest = null;
function playlistNameChange() {
    let playlistName = document.getElementById("playlistName").value;
    const csrftoken = document.querySelector("[name=csrfmiddlewaretoken]").value;
    playlistNameChangeRequest = $.ajax({
        method: "POST",
        url: "/dashboard/",
        data: {
            playlistName: playlistName,
            action: "playlist-name-change",
            csrfmiddlewaretoken: csrftoken,
        },
        beforeSend: function () {
            //NOTE: this block executes before the request.
            //if there is a previous request, abort and continue with the current request
            if (playlistNameChangeRequest != null) {
                playlistNameChangeRequest.abort();
                playlistNameChangeRequest = null;
            }
        },
        error: function (error) {
            console.log("[ERROR]: " + error);
        },
    });
}

//calls playlistNameChange function with 275ms debounce, used as oninput funnction for playlistName
const processPlaylistNameChange = debounce(playlistNameChange, 275);

let static = true;

let playlistChanged = false;

function staticClick() {
	const csrftoken = document.querySelector("[name=csrfmiddlewaretoken]").value;
    $.ajax({
        method: "POST",
        url: "/dashboard/",
        data: {
            mode: "static",
            action: "mode-change",
            csrfmiddlewaretoken: csrftoken,
        },
		beforeSend: function () {
			//allow no pointer events while playlist updating
			document.getElementById("mode-buttons-div").style.pointerEvents = "none";
		},
        success: function (data) {
			document.getElementById("static-button").style.color = "green";
			document.getElementById("dynamic-button").style.color = "white";
			static = true;

			document.getElementById("mode-buttons-div").style.pointerEvents = "auto";
        },
        error: function (error) {
            console.log("[ERROR]: " + error);
        },
    });
}

function dynamicClick() {
	const csrftoken = document.querySelector("[name=csrfmiddlewaretoken]").value;
    $.ajax({
        method: "POST",
        url: "/dashboard/",
        data: {
            mode: "dynamic",
            action: "mode-change",
            csrfmiddlewaretoken: csrftoken,
        },
		beforeSend: function () {
			//allow no pointer events while playlist updating
			document.getElementById("mode-buttons-div").style.pointerEvents = "none";
		},
        success: function (data) {
			document.getElementById("dynamic-button").style.color = "green";
			document.getElementById("static-button").style.color = "white";
			static = false;

			document.getElementById("mode-buttons-div").style.pointerEvents = "auto";
        },
        error: function (error) {
            console.log("[ERROR]: " + error);
        },
    });
}
