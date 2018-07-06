/*global $, swal */
/*jslint es5:true */

$('.success').on('click', function () {
    'use strict';
    
    swal('Case Accepted', 'The case has been accepted', 'success');
});

$('.failure').on('click', function () {
    'use strict';
    
    swal('Case Declined', 'The case has been declined', 'error');
});