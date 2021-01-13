// Function for resizing fill-page divs
const fillPageQuery = ".fill-page"
function fillPage() {
    const bottomFillOffset = 10 + $("footer").height();
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

// Function for rendering character limits below textareas
function addCharacterLimit(query, maxChars) {
    const textareaElem = $(query);
    const charRemainingString  = " characters remaining";

    // generate unique id
    var id = Math.floor(Math.random() * 10000000000);
    while ($(`#chars-remaining-${ id }`).length) {
        id = Math.floor(Math.random() * 10000000000);
    }

    textareaElem.after(`<p class='text-right muted' id='chars-remaining-${ id }'>` + (maxChars - textareaElem.val().length) + charRemainingString + "</p>");
    textareaElem.keyup((event) => {
        $(`#chars-remaining-${ id }`).text((maxChars - $(event.target).val().length) + charRemainingString);
        if ($(event.target).val().length > maxChars) {
            $(event.target).val($(event.target).val().substring(0, maxChars));
        }
    })
}

$(window).on("load", fillPage);
$(window).resize(fillPage);
