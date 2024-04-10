$(document).ready(function() {
    $(".scrolling-text a").each(function() {
        $(this).html($(this).find(".card-title").html());
    });
});