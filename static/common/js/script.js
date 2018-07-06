/*global $ */

$('.panel .panel-heading').click(function () {
    'use strict';
    
    var el = $(this).parents(".panel").children(".panel-body"), icon = $(this).find('.fa').first();
    if (icon.hasClass("fa-chevron-down")) {
        icon.removeClass("fa-chevron-down").addClass("fa-chevron-up");
        el.slideUp(200);
    } else {
        icon.removeClass("fa-chevron-up").addClass("fa-chevron-down");
        el.slideDown(200);
    }
});

function getParameterByName(name, url) {
    
    'use strict';
    if (!url) {
        url = window.location.href;
    }
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)", "i"),
        results = regex.exec(url);
    if (!results) {
        return null;
    }
    if (!results[2]) {
        return '';
    }
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}