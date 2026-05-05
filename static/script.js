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
        window.location.replace("/u/" + encodeURIComponent(data["username"]));
    }
}

////////////////////////////////////////////////////////////////////////////////

function login() {
    let loginValue = document.getElementById("login");
    let password = document.getElementById("password");

    if (loginValue.value == "") {
        alert("Email or UserName cannot be blank");
        return;
    }

    if (password.value == "") {
        alert("Password cannot be blank");
        return;
    }

    let url = "/login?login=" + encodeURIComponent(loginValue.value);
    url += "&password=" + encodeURIComponent(password.value);

    loadDoc(url, login_response);
}

function login_response(response) {
    let data = JSON.parse(response);
    let result = data["result"];
    if (result != "OK") {
        alert(result);
    } else {
        window.location.replace("/u/" + encodeURIComponent(data["username"]));
    }
}

////////////////////////////////////////////////////////////////////////////////

function init_feed() {
    loadDoc("/feedposts", feedposts_response);
}

function feedposts_response(response) {
    let data = JSON.parse(response);
    if (data["result"] != "OK") {
        alert(data["result"]);
        return;
    }

    let posts = data["posts"];
    let temp = "";
    for (let i = 0; i < posts.length; i++) {
        temp += "<div>";
        temp += "<b><a href=\"/u/" + encodeURIComponent(posts[i]["authorusername"]) + "\">@" + posts[i]["authorusername"] + "</a></b><br/>";
        temp += posts[i]["text"] + "<br/>";
        temp += "<small>" + posts[i]["createdat"] + "</small><br/>";
        temp += "<a href=\"/reply.html?id=" + encodeURIComponent(posts[i]["postid"]) + "\">reply</a>";
        temp += "</div><hr/>";
    }

    document.getElementById("divFeedPosts").innerHTML = temp;
}

////////////////////////////////////////////////////////////////////////////////

let profile_user = "";

function init_own_profile(username) {
    profile_user = username;
    let url = "/profileinfo?username=" + encodeURIComponent(username);
    loadDoc(url, profileinfo_response);

    let postsURL = "/userposts?username=" + encodeURIComponent(username);
    loadDoc(postsURL, userposts_response);
}

function init_user_profile(username) {
    profile_user = username;
    let url = "/profileinfo?username=" + encodeURIComponent(username);
    loadDoc(url, profileinfo_response);

    let postsURL = "/userposts?username=" + encodeURIComponent(username);
    loadDoc(postsURL, userposts_response);
}

function profileinfo_response(response) {
    let data = JSON.parse(response);
    if (data["result"] != "OK") {
        alert(data["result"]);
        return;
    }

    document.getElementById("hTitle").innerHTML = data["username"] + " Profile";
    document.getElementById("divUserName").innerHTML = "@" + data["username"];
    document.getElementById("imgPhoto").src = data["photo"];
}

function userposts_response(response) {
    let data = JSON.parse(response);
    if (data["result"] != "OK") {
        alert(data["result"]);
        return;
    }

    let posts = data["posts"];
    let temp = "";
    for (let i = 0; i < posts.length; i++) {
        temp += "<div>";
        temp += "<b>@" + posts[i]["authorusername"] + "</b><br/>";
        temp += posts[i]["text"] + "<br/>";
        temp += "<small>" + posts[i]["createdat"] + "</small><br/>";
        temp += "<a href=\"/reply.html?id=" + encodeURIComponent(posts[i]["postid"]) + "\">reply</a>";
        temp += "</div><hr/>";
    }

    document.getElementById("divPosts").innerHTML = temp;
}

function create_top_post() {
    let txtPost = document.getElementById("txtPost");
    if (txtPost.value.trim() == "") {
        alert("Post text cannot be blank");
        return;
    }

    let url = "/createpost?text=" + encodeURIComponent(txtPost.value);
    url += "&parent=";
    loadDoc(url, create_top_post_response);
}

function create_top_post_response(response) {
    let data = JSON.parse(response);
    if (data["result"] != "OK") {
        alert(data["result"]);
        return;
    }

    document.getElementById("txtPost").value = "";
    let postsURL = "/userposts?username=" + encodeURIComponent(profile_user);
    loadDoc(postsURL, userposts_response);
}

////////////////////////////////////////////////////////////////////////////////

function upload_photo() {
    let fileInput = document.getElementById("filePhoto");
    if (fileInput.files.length == 0) {
        alert("Please choose a file");
        return;
    }

    let xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        if (xhttp.status != 200) {
            console.log("Error");
        } else {
            upload_photo_response(xhttp.response);
        }
    }

    xhttp.open("POST", "/uploadphoto", true);

    let formData = new FormData();
    formData.append("file", fileInput.files[0]);
    xhttp.send(formData);
}

function upload_photo_response(response) {
    let data = JSON.parse(response);
    if (data["result"] != "OK") {
        alert(data["result"]);
        return;
    }

    document.getElementById("imgPhoto").src = data["url"];
}

////////////////////////////////////////////////////////////////////////////////

let reply_post_id = "";

function init_reply(postid) {
    reply_post_id = postid;
    let url = "/post?id=" + encodeURIComponent(postid);
    loadDoc(url, post_response);
}

function post_response(response) {
    let data = JSON.parse(response);
    if (data["result"] != "OK") {
        alert(data["result"]);
        return;
    }

    let post = data["post"];
    let temp = "";
    temp += "<b>@" + post["authorusername"] + "</b><br/>";
    temp += post["text"] + "<br/>";
    temp += "<small>" + post["createdat"] + "</small>";
    document.getElementById("divMainPost").innerHTML = temp;

    let replies = data["replies"];
    let tempReplies = "";
    for (let i = 0; i < replies.length; i++) {
        tempReplies += "<div>";
        tempReplies += "<b>@" + replies[i]["authorusername"] + "</b><br/>";
        tempReplies += replies[i]["text"] + "<br/>";
        tempReplies += "<small>" + replies[i]["createdat"] + "</small>";
        tempReplies += "</div><hr/>";
    }
    document.getElementById("divReplies").innerHTML = tempReplies;
}

function reply_to_post() {
    let txtReply = document.getElementById("txtReply");
    if (txtReply.value.trim() == "") {
        alert("Reply cannot be blank");
        return;
    }

    let url = "/createpost?text=" + encodeURIComponent(txtReply.value);
    url += "&parent=" + encodeURIComponent(reply_post_id);
    loadDoc(url, reply_to_post_response);
}

function reply_to_post_response(response) {
    let data = JSON.parse(response);
    if (data["result"] != "OK") {
        alert(data["result"]);
        return;
    }

    document.getElementById("txtReply").value = "";
    let url = "/post?id=" + encodeURIComponent(reply_post_id);
    loadDoc(url, post_response);
}

console.log("Script Loaded!");
