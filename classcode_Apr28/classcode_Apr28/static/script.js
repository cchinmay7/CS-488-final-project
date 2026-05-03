function loadDoc(url, func) {
    let xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        if (xhttp.status != 200) {
            console.log("Error");
        } else {
            func(xhttp.response);
        }
    }

    xhttp.open("GET", url);
    xhttp.send();
}

////////////////////////////////////////////////////////////////////////////////

function login() {
    let email = document.getElementById("email");
    let password = document.getElementById("password");

    if (email.value == "" || password.value == "") {
        alert("Email and password are required!");
        return;
    }

    let url = "/login?email=" + email.value + "&password=" + password.value;

    let remember = document.getElementById("remember");
    if (remember.checked) {
        url += "&remember=yes";
    } else {
        url += "&remember=no";
    }

    loadDoc(url, login_response);
}

function login_response(response) {
    let data = JSON.parse(response);
    let result = data["result"];
    if (result != "OK") {
        alert(result);
    } else {
        window.location.replace("/account.html");
    }
}

////////////////////////////////////////////////////////////////////////////////

function upload_file() {
    let xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        if (xhttp.status != 200) {
            console.log("Error");
        } else {
            upload_file_response(xhttp.response);
        }
    }

    xhttp.open("POST", "/uploadfile", true);

    var formData = new FormData();
    formData.append("file", document.getElementById("file").files[0]);
    // Hint for project 4: you can add more form elements here

    xhttp.send(formData);
}

function upload_file_response(response) {
    location.reload();
}

////////////////////////////////////////////////////////////////////////////////

function list_files() {
    loadDoc('/listfiles', list_files_response);
}

function list_files_response(response) {
    let data = JSON.parse(response);
    let items = data["items"];
    let url = data["url"];
    let divResults = document.getElementById("divResults");

    let temp = "";
    for (let i = 0; i < items.length; i++) {
        temp += "<a href=\"" + url + items[i] + "\">" + items[i] + "</a><br/>";
    }

    divResults.innerHTML = temp;

}



function course_search() {
    let txtSearch = document.getElementById("txtSearch");
    let URL = "/search?s=" + txtSearch.value;
    loadDoc(URL, course_search_response);
}

function course_search_response(response) {
    let data = JSON.parse(response);
    let results = data["results"];
    let divResults = document.getElementById("divResults");

    let temp = "";

    for (let i = 0; i < results.length; i++) {
        temp += "<div class=\"course_container\">";
        temp += "<div class=\"course_name\">" + results[i]["name"] + "</div>";
        temp += "<div class=\"course_description\">" + results[i]["description"] + "</div>";
        temp += "</div>";
    }

    divResults.innerHTML = temp;
}


function liststudents() {
    loadDoc("/liststudents", liststudents_response);
}

function liststudents_response(response) {
    let data = JSON.parse(response);
    let items = data["results"];

    let temp = "";

    for (let i = 0; i < items.length; i++) {
        temp += items[i]["FirstName"] + " " + items[i]["LastName"] + " " + items[i]["Email"] + "<br/>";
    }

    document.getElementById("divResults").innerHTML = temp;
}







console.log("Script Loaded!");
