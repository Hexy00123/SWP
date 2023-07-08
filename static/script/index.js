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

function openTicket(ticket_id) {
    var newURL = window.location.href.replace("tickets", "ticket/" + ticket_id);
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

function backToTickets() {
    var locationsURL = "http://" + window.location.host + "/admin/tickets";
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

    if (username === null || password === null) {
        window.location.replace('/admin');
        console.log('Authorisation is prohibited');
        return;
    }

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

function putImage(ll) {
    console.log(ll)
    var container = document.getElementById('mapContainer');

// Create an image element
    var image = new Image();

// Specify the API parameters
    var apiParams = {
        apikey: '33b156f1-7891-48be-a9b1-ade66a6b9f70',
        lang: 'en',
        l: 'map',
        ll: ll,
        z: 17,
        pt: ll + ',pm2rdm'
    };

// Construct the query string from the API parameters
    var queryString = Object.keys(apiParams)
        .map(key => key + '=' + encodeURIComponent(apiParams[key]))
        .join('&');

// Construct the URL with the API endpoint and the query string
    var apiUrl = 'https://static-maps.yandex.ru/1.x/?' + queryString;

// Make the request to Yandex.StaticMaps API using Fetch API
    fetch(apiUrl)
        .then(response => response.blob())
        .then(blob => {
            // Create an object URL for the blob
            // Set the image source to the object URL
            image.src = URL.createObjectURL(blob);

            // Add the image to the container element
            container.appendChild(image);
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function acceptTicket(ticket_id) {
    let ids = ["name", "description", "tags", "location"];
    let updates = {};

    for (let i = 0; i < ids.length; i++) {
        const el = document.getElementById(ids[i]);
        if (el) {
            updates[ids[i]] = el.checked;
        }
    }

    fetch(origin + '/admin/ticket?id=' + ticket_id, {method: "PUT", body: JSON.stringify(updates)});
    backToTickets();
}

function rejectTicket(ticket_id) {
    fetch(origin + '/admin/ticket?id=' + ticket_id, {method: "DELETE"});
    backToTickets();
}