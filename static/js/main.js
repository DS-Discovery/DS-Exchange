// Function for resizing fill-page divs
const fillPageQuery = ".fill-page"
const bottomFillOffset = 10;
function fillPage() {
    if ($(fillPageQuery).length == 1) {
        var el = $(fillPageQuery);
        el.height($(window).height() - el.offset().top - bottomFillOffset);
    }
}

// Function for getting cookie value
// from https://docs.djangoproject.com/en/3.1/ref/csrf/#ajax
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Function for adding an alert with a timeout
function sendAlert(message, timeout) {
    var msgElem = $(`<div class="alert alert-info my-2" id="hiya">${ message }</div>`);
    $("div#messages").append(msgElem);
    fillPage();
    setTimeout(() => {
        msgElem.remove();
        fillPage();
    }, timeout);
}

$(window).on("load", fillPage);
$(window).resize(fillPage);
