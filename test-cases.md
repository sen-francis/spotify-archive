# Test Cases

## Test Case 1
**Test:** Use top right log in button on home page.  
**Expected Result:** Spotify log in page appears. After user enters credentials, dashboard page is fetched. Top right shows user profile information. 

## Test Case 2
**Test:** Use middle log in button on home page.  
**Expected Result:** Spotify log in page appears. After user enters credentials, dashboard page is fetched. Top right shows user profile information. 

## Test Case 3
**Test:**  Use continue without log in button on home page.  
**Expected Result:** Dashboard page is shown for fake log in.

## Test Case 4
**Test:**  Use Github button on home page.  
**Expected Result:** User is redirected to Github repository. 

## Test Case 5
**Test:**  While in static mode, write a search query in the search bar and press enter.  
**Expected Result:** Before user presses enter, no results show up. After pressing enter, 10 search results appear for users query.

## Test Case 6
**Test:**  While in static mode, select some tracks.   
**Expected Result:** Selected tracks show up in Current Selection section. Indicator that playlist is not updated appears.

## Test Case 7
**Test:**  While in static mode, when playlist is not updated indicator is visible, generate the playlist.  
**Expected Result:** After clicking generate button, playlist is generated and indicator that playlist is not updated disappears.

## Test Case 8
**Test:**  While in static mode, when playlist is not updated indicator is hidden, modify the tunable track attributes.  
**Expected Result:** Indicator that playlist is not updated appears.  

## Test Case 9
**Test:**  While in static mode, when playlist is not updated indicator is hidden, modify the playlist length.  
**Expected Result:** Indicator that playlist is not updated appears.  

## Test Case 10
**Test:**  While in dynamic mode, write a search query in the search bar.  
**Expected Result:** Search results should appear and update while user is typing.

## Test Case 11
**Test:**  While in dynamic mode, select some tracks.   
**Expected Result:** Selected tracks show up in Current Selection section. Generated playlist should update accordingly.

## Test Case 12
**Test:**  While in dynamic mode, click the regenerate playlist button.  
**Expected Result:** Playlist is regenerated.  

## Test Case 13
**Test:**  While in dynamic mode, modify the tunable track attributes.  
**Expected Result:** Generated playlist should update accordingly. 

## Test Case 14
**Test:**  While in dynamic mode, modify the playlist length.  
**Expected Result:** Generated playlist should update accordingly. 

## Test Case 15
**Test:**  Create a playlist with 4 seed songs with no name.  
**Expected Result:** Playlist should appear in user's Spotify library as "Spotify Archive". Description of playlist should include seed track names. Success page is shown.  

## Test Case 16
**Test:**  Create a playlist with 5 seed songs with name.  
**Expected Result:** Playlist should appear in user's Spotify library as chosen name. Description of playlist should include seed track names. Success page is shown.  

## Test Case 17
**Test:**  Create a 100 song playlist.  
**Expected Result:** 100 song playlist should appear in user's Spotify library. Success page is shown.  

## Test Case 18
**Test:**  Create a playlist with various tunable track attributes enabled.  
**Expected Result:** Playlist should appear in user's Spotify library. Success page is shown.  

## Test Case 19
**Test:**  Log in as user who has previously created playlists using application and navigate to stats page.  
**Expected Result:** User's stats should appear on page along with the previous playlists they have made.

## Test Case 20
**Test:**  Log in as user who has not used application before and navigate to stats page.  
**Expected Result:** User should be notified that they have to use application to access stats page.  