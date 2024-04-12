$(document).ready(function() {
    $(".scrolling-text a").each(function(index) {
        $(this).html($(this).find(".card-title").html());
    });
});