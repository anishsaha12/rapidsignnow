/*global $ */

$('input, textarea').attr('readonly', 'readonly');
$('select').attr('disabled', 'disabled');

$('.form-buttons').click(function () {

    if ($(this).hasClass('editing')) {
        $(this).toggleClass('editing');
        $('input, textarea').attr('readonly', 'readonly');
        $('select').attr('disabled', 'disabled');
    } else {
        $(this).toggleClass('editing');
        $('input, textarea').removeAttr('readonly');
        $('select').removeAttr('disabled');
    }
});