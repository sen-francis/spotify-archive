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