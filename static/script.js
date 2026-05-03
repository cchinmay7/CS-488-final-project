function callApi(url, onDone) {
    let req = new XMLHttpRequest();
    req.onload = function() {
        if (req.status != 200) {
            console.log("Error");
        } else {
            onDone(req.response);
        }
    };

    req.open("GET", url);
    req.send();
}

function makeDeleteButton(postId) {
    return '<button class="btnDelete" onclick="removePost(\'' + postId + '\');" title="Delete">&#128465;</button> ';
}

function drawPosts(responseText, canDelete) {
    let payload = JSON.parse(responseText);
    let posts = payload["results"];
    let html = "";

    if (posts.length == 0) {
        document.getElementById("postList").innerHTML = "No blog entries yet.";
        return;
    }

    for (let i = 0; i < posts.length; i++) {
        html += '<div class="postCard">';
        if (canDelete) {
            html += makeDeleteButton(posts[i]["entryID"]);
        }
        html += '<div class="postTitle">' + posts[i]["title"] + "</div>";
        html += '<div class="postDate">' + posts[i]["date"] + "</div>";
        html += '<div class="postText">' + posts[i]["text"] + "</div>";
        html += "</div>";
    }

    document.getElementById("postList").innerHTML = html;
}

function initHomePage() {
    callApi("/listentries", handleHomePosts);
}

function handleHomePosts(responseText) {
    drawPosts(responseText, false);
}

function initEditorPage() {
    callApi("/listentries", function(responseText) {
        drawPosts(responseText, true);
    });
}

function submitLogin() {
    let emailValue = document.getElementById("email").value;
    let passwordValue = document.getElementById("password").value;

    if (emailValue == "" || passwordValue == "") {
        alert("Email and password are required");
        return;
    }

    let loginUrl = "/login?email=" + encodeURIComponent(emailValue) + "&password=" + encodeURIComponent(passwordValue);
    callApi(loginUrl, handleLoginResult);
}

function handleLoginResult(responseText) {
    let payload = JSON.parse(responseText);
    if (payload["result"] != "OK") {
        alert(payload["result"]);
    } else {
        window.location.replace("/editor.html");
    }
}

function doLogout() {
    callApi("/logout", handleLogoutResult);
}

function handleLogoutResult(responseText) {
    window.location.replace("/login.html");
}

function addPost() {
    let titleValue = document.getElementById("title").value;
    let textValue = document.getElementById("text").value;

    let addUrl = "/addentry?title=" + encodeURIComponent(titleValue) + "&text=" + encodeURIComponent(textValue);
    callApi(addUrl, handleAddPostResult);
}

function handleAddPostResult(responseText) {
    let payload = JSON.parse(responseText);
    if (payload["result"] != "OK") {
        alert(payload["result"]);
        return;
    }

    document.getElementById("title").value = "";
    document.getElementById("text").value = "";
    callApi("/listentries", function(responseText) {
        drawPosts(responseText, true);
    });
}

function removePost(postId) {
    let removeUrl = "/deleteentry?id=" + encodeURIComponent(postId);
    callApi(removeUrl, handleRemovePostResult);
}

function handleRemovePostResult(responseText) {
    let payload = JSON.parse(responseText);
    if (payload["result"] != "OK") {
        alert(payload["result"]);
        return;
    }

    callApi("/listentries", function(responseText) {
        drawPosts(responseText, true);
    });
}
