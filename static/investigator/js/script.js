/*global $, swal */

$('.success.accept-case').on('click', function () {
    'use strict';
    var case_id = $(this).attr('data-case-id');
    
    swal({
        title: "Are you sure?",
        text: "If you agree, this case will be selected as your current working case.",
        type: "info",
        showCancelButton: true,
        confirmButtonColor: "#a9d86e",
        confirmButtonText: "Yes",
        cancelButtonColor: '#ff6e61',
        cancelButtonText: "No",
        closeOnConfirm: false
    }).then(function () {
        $.post('/investigator/accept-case/', {
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            case_id: case_id
        }, function () {
            swal({
                title: 'Case Accepted',
                text: 'The case has been accepted',
                type: 'success',
                timer: 2000,
                showConfirmButton: false
            });
            
            setTimeout(function () {
                location.reload();
            }, 2000);
        });
    });
});

$('.failure.decline-case').on('click', function () {
    'use strict';
    var case_id = $(this).attr('data-case-id');
    
    swal({
        title: "Are you sure?",
        text: "This case will be declined and removed from your list",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#ff6e61",
        confirmButtonText: "Yes",
        cancelButtonText: "No",
        closeOnConfirm: false
    }).then(function () {
        $.post('/investigator/decline-case/', {
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            case_id: case_id
        }, function () {
            swal({
                title: 'Case Declined',
                text: 'The case has been declined',
                type: 'success',
                timer: 2000,
                showConfirmButton: false
            });
            
            setTimeout(function () {
                location.reload();
            }, 2000);
        });
    });
});