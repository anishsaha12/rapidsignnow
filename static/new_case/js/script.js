/*global $, swal */

$('.btn-info').click(function () {
    'use strict';
    swal({
        title: 'Created',
        text: 'The case has been created',
        type: 'success',
        timer: 2000,
        showConfirmButton: false
    });
         
    setTimeout(function () {
        location.assign('/broker/all-cases/');
    }, 2000);
});