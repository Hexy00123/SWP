function redirectToUsers() {
    var gfg = window.location.href.replace("locations", "users");
    window.location.replace(gfg)
    document.getElementById("url").innerHTML = gfg;
}

function openLocation(location_id) {
    var newURL = window.location.href.replace("locations/show", "location/" + location_id);
    console.log(newURL)
    window.location.replace(newURL)
    document.getElementById("url").innerHTML = newURL;
}

function removeUser(userId) {
    var route = window.location.href.replace("users/show", "/user?id=" + userId);
    fetch(route, {
        method: 'DELETE',
    })
        .then(response => {
            if (response.ok) {
                console.log('User ' + userId + ' deleted successfully');
                window.location.reload()
            } else {
                console.log('Error deleting user');
            }
        })
        .catch(error => {
            console.log('Error:', error);
        });
}

function redirectToLocations() {
    var gfg = window.location.href.replace("users", "locations");
    window.location.replace(gfg)
    document.getElementById("url").innerHTML = gfg;
}

function backToLocations() {
    var locationsURL = "http://" + window.location.host + "/admin/locations/show";
    document.getElementById("url").innerHTML = locationsURL;
    window.location.replace(locationsURL);
}