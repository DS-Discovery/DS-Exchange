// Function for resizing fill-page divs
const fillPageQuery = ".fill-page"
const bottomFillOffset = 10;
function fillPage() {
    if ($(fillPageQuery).length == 1) {
        var el = $(fillPageQuery);
        el.height($(document).height() - el.offset().top - bottomFillOffset);
    }
}

$(window).on("load", fillPage);
$(window).resize(fillPage);
