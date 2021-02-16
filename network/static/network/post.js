document.addEventListener('DOMContentLoaded', function () {
    initialze_like_onclick();
});

function initialze_like_onclick() {
    const like_buttons = document.getElementsByClassName('post-like');
    for (let i = 0; i < like_buttons.length; i++)
        like_buttons[i].onclick = function (e) {
            console.log("Action: " + e.target.dataset.action + " - Post ID: " + e.target.dataset.postId);
            fetch(`like`, {
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