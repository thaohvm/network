document.addEventListener("DOMContentLoaded", function () {
    initialize_like_onclick();
    initialize_edit_onclick();
});

function flip_post_edit(postId, enableEdit, saveEdit) {
    // Flip buttons
    document.getElementById("post-edit-" + postId).style.display = enableEdit ? "none" : "inline-block";
    document.getElementById("post-edit-save-" + postId).style.display = enableEdit ? "inline-block" : "none";
    document.getElementById("post-edit-cancel-" + postId).style.display = enableEdit ? "inline-block" : "none";
    // Flip text-area
    let content = document.getElementById("post-content-" + postId);
    let contentEdit = document.getElementById("post-content-edit-" + postId)
    if (enableEdit) {
        contentEdit.value = content.innerText;
    }

    if (saveEdit) {
        content.innerText = contentEdit.value;
    }

    content.style.display = enableEdit ? "none" : "inline-block";
    contentEdit.style.display = enableEdit ? "inline-block" : "none";
}

function initialize_like_onclick() {
    const like_buttons = document.getElementsByClassName("post-like");
    for (let i = 0; i < like_buttons.length; i++)
        like_buttons[i].onclick = function (e) {
            console.log("Action: " + e.target.dataset.action + " - Post ID: " + e.target.dataset.postId);
            fetch("like", {
                method: 'PUT',
                body: JSON.stringify({
                    action: e.target.dataset.action,
                    id: e.target.dataset.postId
                })
            })
                .then(response => response.json()
                    .then(data => {
                        if (data.action == "like") {
                            e.target.dataset.action = "unlike";
                            e.target.innerText = "Unlike " + data.likes;
                        } else {
                            e.target.dataset.action = "like";
                            e.target.innerText = "Like " + data.likes;
                        }
                    })
                )
                .catch((error) => console.log(error));
        }
};

function initialize_edit_onclick() {
    // Edit buttons
    const editButtons = document.getElementsByClassName("post-edit");
    for (let i = 0; i < editButtons.length; i++) {
        editButtons[i].onclick = function (e) {
            let postId = e.target.dataset.postId;
            flip_post_edit(postId, true, false);
        }
    }
    // Cancel buttons
    const cancelButtons = document.getElementsByClassName("post-edit-cancel");
    for (let i = 0; i < cancelButtons.length; i++) {
        cancelButtons[i].onclick = function (e) {
            let postId = e.target.dataset.postId;
            flip_post_edit(postId, false, false);
        }
    }
    // Save buttons
    const saveButtons = document.getElementsByClassName("post-edit-save");
    for (let i = 0; i < saveButtons.length; i++) {
        saveButtons[i].onclick = function (e) {
            let postId = e.target.dataset.postId;
            let content = document.getElementById("post-content-edit-" + postId).value;
            fetch("post", {
                method: 'PUT',
                body: JSON.stringify({
                    id: postId,
                    content: content
                })
            })
                .then(response => response.json()
                    .then(data => {
                        flip_post_edit(data.id, false, true);
                    })
                )
                .catch((error) => console.log(error));
        }
    }
}