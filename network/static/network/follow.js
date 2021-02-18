document.addEventListener('DOMContentLoaded', function () {
    follow_onclick();
});

function follow_onclick() {
    const follow_button = document.getElementById('follow-user');
    const followers = document.getElementById('profile-follower');
    if (follow_button !== null) {
        follow_button.onclick = function () {
            fetch("/follow", {
                method: 'PUT',
                body: JSON.stringify({
                    action: follow_button.innerText,
                    id: follow_button.dataset.userId
                })
            })
                .then(response => response.json()
                    .then(data => {
                        if (data.action == "Follow") {
                            follow_button.innerText = "Unfollow";
                        } else {
                            follow_button.innerText = "Follow";
                        }
                        followers.innerText =  + data.followers + " Followers";
                    })
                )
                .catch((error) => console.log(error));
        }
    }
};