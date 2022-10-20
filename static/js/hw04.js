////
//// Display Posts
////
const post2Html = post => {
    return `
        <div class="card">
            <div class="card-top">
                <h3>${ post.user.username }</h3>
                <i class="fas fa-ellipsis-h"></i>
            </div>

            <img src="${ post.image_url }" alt="${ post.user.username }'s post"/>

            <div class="card-icons">
                <div>
                    <button 
                        id="like-icon-${ post.id }"
                        class="icon-button like-post"
                        aria-label="liked"
                        aria-checked="false"
                        data-post-id="${ post.id }" 
                        onclick="toggleLikePost(event)"><i class="far fa-heart"></i></button>
                    <button class="icon-button"><i class="far fa-comment"></i></button>
                    <button class="icon-button"><i class="far fa-paper-plane"></i></button>
                </div>
                <button
                    id="bookmark-icon-${ post.id }"
                    class="icon-button bookmark-post"
                    aria-label="bookmarked"
                    aria-checked="false"
                    data-post-id="${ post.id }" 
                    onclick="toggleBookmarkPost(event)"><i class="far fa-bookmark"></i></button>
            </div>

            <p id="like-count-${ post.id }" class="card-text-bold">${ post.likes.length } likes</p>

            <p><span class="card-text-bold">${ post.user.username }</span> ${ post.caption }.. <a href="#">more</a></p>
            
            <p id="comment-count-${ post.id }"></p>
            
            <p id="first-comment-${ post.id }"></p>

            <p class="post-date"><span>${ post.display_time }</span></p>
            
            <div class="card-add-comment">
                <div>
                    <input id="comment-text-${ post.id }" type="text" title="Add comment box" placeholder="Add a comment...">
                    <button
                        id="post-comment-${ post.id }"
                        data-post-id="${ post.id }" 
                        onclick="postComment(event)">Post</button>
                </div>
                
            </div>
        </div>
    `
};

const includeCommentsHtml = post => {
    if (post.comments.length > 1) {
        document.querySelector('#comment-count-' + post.id).innerHTML = `<button id="view-more-comments-${ post.id }" 
                                                                            class="view-more-comments" 
                                                                            data-post-id="${ post.id }" 
                                                                            onclick="openModal(event)">View all ${ post.comments.length } comments</button>`;
    }
    if (post.comments.length > 0) {
        document.querySelector('#first-comment-' + post.id).innerHTML = `<span class="card-text-bold">${ post.comments[0].user.username }</span> ${ post.comments[0].text }`;
    }
};

const iconStates = post => {
    likePostId = post.current_user_like_id;
    bookmarkPostId = post.current_user_bookmark_id;
    if (likePostId) {
        element = document.querySelector('#like-icon-' + post.id);
        element.innerHTML = '<i class="fas fa-heart"></i>';
        element.classList.add('unlike-post');
        element.classList.remove('like-post');
        element.setAttribute('aria-checked', 'true');
        element.setAttribute('data-like-post-id', likePostId);
    }
    if (bookmarkPostId) {
        element = document.querySelector('#bookmark-icon-' + post.id);
        element.innerHTML = '<i class="fas fa-bookmark"></i>';
        element.classList.add('unbookmark-post');
        element.classList.remove('bookmark-post');
        element.setAttribute('aria-checked', 'true');
        element.setAttribute('data-bookmark-post-id', bookmarkPostId);
    }

};

const updateLikes = postId => {
    fetch(`/api/posts/${ postId }`)
        .then(response => response.json())
        .then(post => {
            document.querySelector('#like-count-' + postId).innerHTML = `${ post.likes.length } likes`;
        });
};

const updateComments = (postId, commentId) => {
    fetch(`/api/posts/${ postId }`)
        .then(response => response.json())
        .then(post => {
            if (post.comments.length > 1) {
                document.querySelector('#comment-count-' + post.id).innerHTML = `<button id="view-more-comments-${ post.id }" 
                                                                                    class="view-more-comments" 
                                                                                    data-post-id="${ post.id }" 
                                                                                    onclick="openModal(event)">View all ${ post.comments.length } comments</button>`;
            }
            if (post.comments.length > 0) {
                post.comments.forEach(comment => {
                    if (comment.id === commentId) {
                        document.querySelector('#first-comment-' + post.id).innerHTML = `<span class="card-text-bold">${ comment.user.username }</span> ${ comment.text }`;
                    }
                });
            }
        });
};

const displayPosts = () => {
    fetch('/api/posts/?limit=10')
        .then(response => response.json())
        .then(posts => {
            const html = posts.map(post2Html).join('\n');
            document.querySelector('#posts').innerHTML = html;
            posts.forEach(includeCommentsHtml);
            posts.forEach(iconStates);
        });
};

const toggleLikePost = event => {
    const element = event.currentTarget;
    console.log(element.dataset.postId)
    if (element.getAttribute('aria-checked') === 'false') {
        likePost(element.dataset.postId, element);
    } else {
        unlikePost(element.dataset.postId, element.dataset.likePostId, element);
    }
};

const likePost = (postId, element) => {
    const postData = {
        'post_id': parseInt(postId)
    };
    fetch('/api/posts/likes', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-TOKEN': getCookie('csrf_access_token')
        },
        body: JSON.stringify(postData)
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        element.innerHTML = '<i class="fas fa-heart"></i>';
        element.classList.add('unlike-post');
        element.classList.remove('like-post');
        element.setAttribute('aria-checked', 'true');
        // Used for unlike functionality
        element.setAttribute('data-like-post-id', data.id);
        updateLikes(postId);
    });
};

const unlikePost = (postId, likePostId, element) => {
    fetch(`/api/posts/likes/${ likePostId }`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-TOKEN': getCookie('csrf_access_token')
        },
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        element.innerHTML = '<i class="far fa-heart"></i>';
        element.classList.add('like-post');
        element.classList.remove('unlike-post');
        element.setAttribute('aria-checked', 'false');
        // Used for unlike functionality
        element.removeAttribute('data-like-post-id');
        updateLikes(postId);
    });
};

const toggleBookmarkPost = event => {
    const element = event.currentTarget;
    console.log(element.dataset.postId)
    if (element.getAttribute('aria-checked') === 'false') {
        bookmarkPost(element.dataset.postId, element);
    } else {
        unbookmarkPost(element.dataset.postId, element.dataset.bookmarkPostId, element);
    }
};

const bookmarkPost = (postId, element) => {
    const postData = {
        'post_id': parseInt(postId)
    };
    fetch('/api/bookmarks', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-TOKEN': getCookie('csrf_access_token')
        },
        body: JSON.stringify(postData)
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        element.innerHTML = '<i class="fas fa-bookmark"></i>';
        element.classList.add('unbookmark-post');
        element.classList.remove('bookmark-post');
        element.setAttribute('aria-checked', 'true');
        // Used for unlike functionality
        element.setAttribute('data-bookmark-post-id', data.id);
        updateLikes(postId);
    });
};

const unbookmarkPost = (postId, bookmarkPostId, element) => {
    fetch(`/api/bookmarks/${ bookmarkPostId }`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-TOKEN': getCookie('csrf_access_token')
        },
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        element.innerHTML = '<i class="far fa-bookmark"></i>';
        element.classList.add('bookmark-post');
        element.classList.remove('unbookmark-post');
        element.setAttribute('aria-checked', 'false');
        // Used for unlike functionality
        element.removeAttribute('data-bookmark-post-id');
        updateLikes(postId);
    });
};

const postComment = event => {
    const element = event.currentTarget;
    console.log(element.dataset.postId);

    const postId = element.dataset.postId
    commentText = document.querySelector('#comment-text-' + postId).value;
    const postData = {
        post_id: parseInt(postId),
        text: commentText
    };
    fetch('/api/comments', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-TOKEN': getCookie('csrf_access_token')
        },
        body: JSON.stringify(postData)
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        document.querySelector('#comment-text-' + postId).value = '';
        updateComments(postId, data.id);
        document.querySelector('#comment-text-' + postId).focus();
    });
};


////
//// Display Stories
////
const story2Html = story => {
    return `
        <div>
            <img src="${ story.user.thumb_url }" class="pic" alt="profile pic for ${ story.user.username }" />
            <p>${ story.user.username }</p>
        </div>
    `;
};

const displayStories = () => {
    fetch('/api/stories')
        .then(response => response.json())
        .then(stories => {
            const html = stories.map(story2Html).join('\n');
            document.querySelector('.stories').innerHTML = html;
        });
};


////
//// Display Profile
////
const profile2Html = user => {
    return `
        <div id="user">
            <div>
                <img src="${ user.image_url }" alt="${ user.username }'s profile picture" id="user-pic" />
            </div>
            <h2>${ user.username }</h2>
        </div>
    `;
};

const displayProfile = () => {
    fetch('api/profile')
        .then(response => response.json())
        .then(profile => {
            const html = profile2Html(profile);
            document.querySelector('#user-profile-suggestions').innerHTML = html;
        });
};


////
//// Display Suggestions
////
const suggestion2Html = suggestion => {
    return `
        <section class="suggestion">
            <img class="pic" src="${ suggestion.thumb_url }"/>
            <div>
                <p>${ suggestion.username }</p>
                <p>suggested for you</p>
            </div>
            <div>
                <button 
                    class="follow" 
                    aria-label="follow"
                    aria-checked="false"
                    data-user-id="${ suggestion.id }" 
                    onclick="toggleFollow(event)">follow</button>
            </div>
        </section>
    `;
};

const displaySuggestions = () => {
    fetch('/api/suggestions/')
        .then(response => response.json())
        .then(suggestions => {
            const html = suggestions.map(suggestion2Html).join('\n');
            document.querySelector('.suggestions div').innerHTML = html;
        });
};

const toggleFollow = event => {
    const element = event.currentTarget;
    console.log(element.dataset.userId)
    if (element.getAttribute('aria-checked') === 'false') {
        followUser(element.dataset.userId, element);
    } else {
        unfollowUser(element.dataset.followingId, element);
    }
};

const followUser = (followingId, element) => {
    const postData = {
        'user_id': parseInt(followingId)
    };
    fetch('/api/following/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-TOKEN': getCookie('csrf_access_token')
        },
        body: JSON.stringify(postData)
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        element.innerHTML = 'unfollow';
        element.classList.add('unfollow');
        element.classList.remove('follow');
        element.setAttribute('aria-checked', 'true')
        // Used for unfollow functionality
        element.setAttribute('data-following-id', data.id);
    });
};

const unfollowUser = (followingId, element) => {
    fetch(`/api/following/${ followingId }`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-TOKEN': getCookie('csrf_access_token')
        },
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        element.innerHTML = 'follow';
        element.classList.add('follow');
        element.classList.remove('unfollow');
        element.setAttribute('aria-checked', 'false')
        // Used for unfollow functionality
        element.removeAttribute('data-following-id');
    });
};


////
//// Modal
////
const modal2Html = post => {
    return `
        <div class="modal-bg" role="dialog">
            <section class="modal">
                <button class="close" aria-label="Close the modal window" data-post-id="${ post.id }" onclick="closeModal(event);">X</button>
                <div class="modal-body">
                    <img class="modal-pic" src="${ post.image_url }"/>
                    <div class="modal-comments">
                        <div class="post-profile">
                            <img src="${ post.user.thumb_url }" class="post-profile-image" alt="profile pic for ${ post.user.username }" />
                            <p>${ post.user.username }</p>
                        </div>
                        <div class="row">
                            <div>
                                <img class="modal-profile-pics" src="${ post.user.thumb_url }"/>
                                <p><span class="card-text-bold">${ post.user.username }</span> ${ post.caption }</p>
                            </div>
                            <button class="icon-button"><i class="far fa-heart"></i></button>
                        </div>
                        ${ displayModalComments(post) }
                    </div>
                </div>
            </section>
        </div>
    `;
};

const modalComment2Html = comment => {
    return `
    <div class="row">
        <div>
            <img class="modal-profile-pics" src="${ comment.user.thumb_url }"/>
            <p><span class="card-text-bold">${ comment.user.username }</span> ${ comment.text }</p>
        </div>
        <button class="icon-button"><i class="far fa-heart"></i></button>
    </div>
    `;
};

const displayModalComments = post => {
    return `
        ${ post.comments.map(modalComment2Html).join('\n') }
    `;
};

const modalElement = document.querySelector('#modal');

const openModal = event => {
    const element = event.currentTarget;
    const postId = element.dataset.postId;
    fetch(`/api/posts/${ postId }`)
        .then(response => response.json())
        .then(post => {
            const html = modal2Html(post);
            document.querySelector('#modal').innerHTML = html;
            console.log('open!');
            modalElement.classList.remove('hidden');
            modalElement.setAttribute('aria-hidden', 'false');
            document.querySelector('.close').focus();
            document.querySelector('body').classList.add('stop-scroll');
        });
};

const closeModal = event => {
    const element = event.currentTarget;
    const postId = element.dataset.postId;
    console.log('close!');
    modalElement.classList.add('hidden');
    modalElement.setAttribute('aria-hidden', 'true');
    document.querySelector(`#view-more-comments-${ postId }`).focus();
    document.querySelector('body').classList.remove('stop-scroll');
};

document.addEventListener('focus', function(event) {
    console.log('focus');
    if (modalElement.getAttribute('aria-hidden') === 'false' && !modalElement.contains(event.target)) {
        console.log('back to top!');
        event.stopPropagation();
        document.querySelector('.close').focus();
    }
}, true);


const initPage = () => {
    displayPosts();
    displayStories();
    displaySuggestions();
    displayProfile();
};

// invoke init page to display stories:
initPage();


const getCookie = key => {
    let name = key + "=";
    let decodedCookie = decodeURIComponent(document.cookie);
    let ca = decodedCookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
};
