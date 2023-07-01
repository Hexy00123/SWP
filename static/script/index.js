// Redirects the user to the users page by replacing "locations" in the current URL with "users".
function redirectToUsers() {
    var gfg = window.location.href.replace("locations", "users");
    window.location.replace(gfg)
    document.getElementById("url").innerHTML = gfg;
}

// Opens a specific location by replacing "locations/show" in the current URL with "location/{location_id}".
function openLocation(location_id) {
    var newURL = window.location.href.replace("locations/show", "location/" + location_id);
    console.log(newURL)
    window.location.replace(newURL)
    document.getElementById("url").innerHTML = newURL;
}

// Removes a user by sending a DELETE request to the server with the user ID.
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

// Redirects the user to the locations page by replacing "users" in the current URL with "locations".
function redirectToLocations() {
    var gfg = window.location.href.replace("users", "locations");
    window.location.replace(gfg)
    document.getElementById("url").innerHTML = gfg;
}

// Takes the user back to the locations page by constructing the URL using the current host and "/admin/locations/show".
function backToLocations() {
    var locationsURL = "http://" + window.location.host + "/admin/locations/show";
    document.getElementById("url").innerHTML = locationsURL;
    window.location.replace(locationsURL);
}

// Performs an admin login by sending a GET request to the server with the username and password.
function adminLogin(username, password) {
    fetch('/admin/authorisation?username=' + username.toString() + '&password=' + password.toString(), {
        method: 'GET',
    })
        .then(response => {
            if (response.status === 200) {
                localStorage.setItem('username', username);
                localStorage.setItem('password', password);

                window.location.replace('admin/users/show');
            } else {
                window.location.replace('/admin');
                console.log('Authorisation is prohibited');
            }
        })
        .catch(error => {
            console.log('Error:', error);
        });
}

// Performs admin authorization by sending a GET request to the server with the stored username and password.
// method implemented only for using it for protecting existing moderator pages
function adminAuth() {
    var username = localStorage.getItem('username');
    var password = localStorage.getItem('password');

    fetch('/admin/authorisation?username=' + username.toString() + '&password=' + password.toString(), {
        method: 'GET',
    })
        .then(response => {
            if (response.status === 200) {
            } else {
                window.location.replace('/admin');
                console.log('Authorisation is prohibited');
            }
        })
        .catch(error => {
            console.log('Error:', error);
        });
}
