function loadDoc(url, func) {
    let xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        if (xhttp.status != 200) {
            console.log('Error');
        } else {
            func(xhttp.response);
        }
    };

    xhttp.open('GET', url);
    xhttp.send();
}

function escapeText(value) {
    let temp = value;
    temp = temp.replaceAll('&', '&amp;');
    temp = temp.replaceAll('<', '&lt;');
    temp = temp.replaceAll('>', '&gt;');
    return temp;
}

function postCardHtml(post, showReplyLink) {
    let html = '<div class="postCard">';
    html += '<div class="postHeader"><a href="/u/' + encodeURIComponent(post['authorUsername']) + '">@' + escapeText(post['authorUsername']) + '</a></div>';
    html += '<div class="postDate">' + escapeText(post['date']) + '</div>';
    html += '<div class="postText">' + escapeText(post['text']) + '</div>';
    if (showReplyLink) {
        html += '<div><a href="/post.html?id=' + encodeURIComponent(post['entryID']) + '">[ reply ]</a></div>';
    }
    html += '</div>';
    return html;
}

function submitLogin() {
    let login = document.getElementById('login').value;
    let password = document.getElementById('password').value;

    let url = '/login?login=' + encodeURIComponent(login) + '&password=' + encodeURIComponent(password);
    loadDoc(url, submitLoginResponse);
}

function submitLoginResponse(responseText) {
    let data = JSON.parse(responseText);
    if (data['result'] != 'OK') {
        alert(data['result']);
        return;
    }
    window.location.replace('/feed.html');
}

function submitSignup() {
    let email = document.getElementById('email').value;
    let username = document.getElementById('username').value;
    let password = document.getElementById('password').value;

    let url = '/signup?email=' + encodeURIComponent(email);
    url += '&username=' + encodeURIComponent(username);
    url += '&password=' + encodeURIComponent(password);

    loadDoc(url, submitSignupResponse);
}

function submitSignupResponse(responseText) {
    let data = JSON.parse(responseText);
    if (data['result'] != 'OK') {
        alert(data['result']);
        return;
    }
    window.location.replace('/feed.html');
}

function doLogout() {
    loadDoc('/logout', doLogoutResponse);
}

function doLogoutResponse(responseText) {
    window.location.replace('/login.html');
}

function initFeedPage() {
    loadDoc('/feedposts', initFeedPageResponse);
}

function initFeedPageResponse(responseText) {
    let data = JSON.parse(responseText);
    let posts = data['results'];
    let html = '';

    for (let i = 0; i < posts.length; i++) {
        html += postCardHtml(posts[i], true);
    }

    if (html == '') {
        html = 'No posts yet.';
    }

    document.getElementById('divFeed').innerHTML = html;
}

function initProfilePage(username) {
    loadDoc('/profileinfo?username=' + encodeURIComponent(username), initProfileInfoResponse);
    loadDoc('/userposts?username=' + encodeURIComponent(username), initProfilePostsResponse);
}

function initProfileInfoResponse(responseText) {
    let data = JSON.parse(responseText);
    if (data['result'] != 'OK') {
        alert(data['result']);
        return;
    }

    document.getElementById('profileImage').src = data['photo'];
    document.getElementById('profileUsername').innerHTML = '@' + escapeText(data['username']);
}

function initProfilePostsResponse(responseText) {
    let data = JSON.parse(responseText);
    let posts = data['results'];
    let html = '';

    for (let i = 0; i < posts.length; i++) {
        html += postCardHtml(posts[i], true);
    }

    if (html == '') {
        html = 'No posts yet.';
    }

    document.getElementById('divProfilePosts').innerHTML = html;
}

function createProfilePost() {
    let txtPost = document.getElementById('txtPost');
    let url = '/createpost?text=' + encodeURIComponent(txtPost.value);
    loadDoc(url, createProfilePostResponse);
}

function createProfilePostResponse(responseText) {
    let data = JSON.parse(responseText);
    if (data['result'] != 'OK') {
        alert(data['result']);
        return;
    }

    let username = document.getElementById('profilePageUsername').value;
    document.getElementById('txtPost').value = '';
    loadDoc('/userposts?username=' + encodeURIComponent(username), initProfilePostsResponse);
}

function uploadProfilePhoto() {
    let xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        if (xhttp.status != 200) {
            console.log('Error');
        } else {
            uploadProfilePhotoResponse(xhttp.response);
        }
    };

    xhttp.open('POST', '/uploadphoto', true);

    let formData = new FormData();
    let fileControl = document.getElementById('photoFile');
    if (fileControl.files.length == 0) {
        alert('Please choose a photo first');
        return;
    }
    formData.append('file', fileControl.files[0]);
    xhttp.send(formData);
}

function uploadProfilePhotoResponse(responseText) {
    let data = JSON.parse(responseText);
    if (data['result'] != 'OK') {
        alert(data['result']);
        return;
    }
    document.getElementById('profileImage').src = data['url'];
}

function initPostPage(entryID) {
    loadDoc('/post?id=' + encodeURIComponent(entryID), initPostPageResponse);
}

function initPostPageResponse(responseText) {
    let data = JSON.parse(responseText);
    if (data['result'] != 'OK') {
        alert(data['result']);
        return;
    }

    let html = postCardHtml(data['post'], false);
    document.getElementById('divPost').innerHTML = html;

    let replies = data['replies'];
    let replyHtml = '';
    for (let i = 0; i < replies.length; i++) {
        replyHtml += postCardHtml(replies[i], false);
    }

    if (replyHtml == '') {
        replyHtml = 'No replies yet.';
    }

    document.getElementById('divReplies').innerHTML = replyHtml;
}

function createReply() {
    let entryID = document.getElementById('entryID').value;
    let text = document.getElementById('txtReply').value;
    let url = '/createpost?text=' + encodeURIComponent(text) + '&parent=' + encodeURIComponent(entryID);
    loadDoc(url, createReplyResponse);
}

function createReplyResponse(responseText) {
    let data = JSON.parse(responseText);
    if (data['result'] != 'OK') {
        alert(data['result']);
        return;
    }

    let entryID = document.getElementById('entryID').value;
    document.getElementById('txtReply').value = '';
    loadDoc('/post?id=' + encodeURIComponent(entryID), initPostPageResponse);
}
