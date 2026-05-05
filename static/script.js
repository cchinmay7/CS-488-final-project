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

function signup() {
    let email = document.getElementById("email");
    let username = document.getElementById("username");
    let password = document.getElementById("password");

    if (email.value == "") {
        alert("Email cannot be blank");
        return;
    }

    if (email.value.indexOf("@") == -1 || email.value.indexOf(".") == -1) {
        alert("Email must include @ and .");
        return;
    }

    if (username.value == "") {
        alert("UserName cannot be blank");
        return;
    }

    if (password.value == "") {
        alert("Password cannot be blank");
        return;
    }

    let url = "/signup?email=" + encodeURIComponent(email.value);
    url += "&username=" + encodeURIComponent(username.value);
    url += "&password=" + encodeURIComponent(password.value);

    loadDoc(url, signup_response);
}

function signup_response(response) {
    let data = JSON.parse(response);
    let result = data["result"];
    if (result != "OK") {
        alert(result);
    } else {
        window.location.replace("/account.html");
    }
}

console.log("Script Loaded!");
