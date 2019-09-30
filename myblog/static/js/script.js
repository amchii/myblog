$(function () {
    function render_time() {
        return moment($(this).data('timestamp')).format('lll')
    }

    $('[data-toggle="tooltip"]').tooltip(
        {title: render_time}
    );

    var imgs = $("img");
    var viewWidth = $(".col-sm-8").width();

    function scale(img) {
        if (img.width > viewWidth) {
            img.width = viewWidth;
        }
    }

    $.map(imgs, scale);
});
