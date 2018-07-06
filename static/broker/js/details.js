/*global $, swal, Promise, case_id, additional_expenses:true, no_of_miles:true */
/*jslint es5:true */

$('#updateStatusBtn').click(function () {
    'use strict';

    $('#adult-signature-names').remove();
    $('#child-signature-names').remove();
    

    var selected_status = $('input[name=case-status-radio]:checked').val(), change_status_call;
    selected_status = selected_status.substring(0, 1).toLocaleUpperCase() + selected_status.substring(1);
    selected_status = selected_status.split('-').join(' ');

    change_status_call = function (extra_info) {
        $('#adult-signature-names').remove();
        $('#child-signature-names').remove();
        
        $.post('/broker/change-status/', {
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            case_id: case_id,
            new_status: selected_status,
            extra_info: extra_info
        }, function () {
            swal({
                title: 'Status changed',
                text: 'The status has been changed',
                type: 'success',
                timer: 2000,
                showConfirmButton: false
            });

            setTimeout(function () {
                location.reload();
            }, 2000);
        }).fail(function (error) {
            
            swal({
                title: 'Unable to change status',
                text: 'Unable to change status of the case as either an active Invoice already exists or the investigator has been marked as paid',
                type: 'error',
                showConfirmButton: true

            });
            console.log(JSON.stringify(error.responseText, null, 2));
        });
    };
    // For case details page 
    if (selected_status === 'Client cancelled') {
        debugger;
        function cancelledOptions() {
            $('input[type=radio][name=cancelled-by]').change(function () {
                debugger;
                if (this.value == 'Client cancelled') {
                    $('.client-cancelled-radios').show();
                }
                else if (this.value == 'Firm decision') {
                    $('.client-cancelled-radios').hide();
                }
            });
        }

        swal({
            title: 'Cancelled',
            confirmButtonText: 'Submit',
            showCancelButton: true,
            onOpen: cancelledOptions,
            html: '<div class="swal2-radios" style="display: block;">\
            <div class="cancelled">\
            <label>\
                <input type="radio" name="cancelled-by" value="Client cancelled" style="margin-top:2px">\
                <span style="margin-left: -10px;">Client Cancelled</span>\
                <input type="radio" name="cancelled-by" value="Firm decision" style="margin-top:2px">\
                <span style="margin-left: -10px;">Firm Decision</span></label>\
                </div>\
                \
                <div class="client-cancelled-radios" style="display:none;margin-top:60px">\
                <p>Why did the Client Cancel ?</p>\
                <label>\
                <input type="radio" name="cancel-reason-radio" value="Changed mind" style="margin-top:2px">\
                <span style="margin-left: -10px;">Changed mind</span>\
                <input type="radio" name="cancel-reason-radio" value="Found new firm" style="margin-top:2px">\
                <span style="margin-left: -10px;">Found new firm</span>\
            </label>\
            <label>\
            <input type="radio" name="cancel-reason-radio" value="Client did not responded" style="margin-top:2px">\
                <span style="margin-left: -10px;">Client did not responded</span>\
                <label>\
            </div>\
                \
            </div>\
            <input style="display: block;" class="swal2-input" id="client-cancelled-more-info" placeholder="More info (optional)" type="text">',

            preConfirm: function () {
                return new Promise(function (resolve, reject) {


                    debugger;
                    var cancelledBy = $('input[name="cancelled-by"]:checked');
                    var cancellationReason = $('input[name="cancel-reason-radio"]:checked');

                    if (cancelledBy.val() == 'Firm decision') {
                        resolve({
                            'Cancelled by': cancelledBy.val(),
                            'Cancellation reason': '',
                            'More Info': $('#client-cancelled-more-info').val()
                        });
                    }

                    else if (cancelledBy.size() > 0 && cancellationReason.size() > 0) {


                        resolve({
                            'Cancelled by': cancelledBy.val(),
                            'Cancellation reason': cancellationReason.val(),
                            'More Info': $('#client-cancelled-more-info').val()
                        });


                    } else {
                        reject('You need to select one of the options');
                    }
                });
            }
        }).then(function (cancel_data) {
            change_status_call(JSON.stringify(cancel_data));
        }, function () {

        });
    } else if (selected_status === 'Signature obtained') {
        function setTagsInput(modalEle) {


            $('#adult-signature-names').tagsInput({
                width: 'auto',
                defaultText: ''
            });
            $('#child-signature-names').tagsInput({
                width: 'auto',
                defaultText: ''
            });

        }
        swal({
            title: 'Please enter the information below',
            confirmButtonText: 'Submit',
            onOpen: setTagsInput,
            html: '<div style="" class="form-horizontal"><div class="form-group"> <label class="col-md-6 control-label" for="no-of-adult-signatures-obtained">No. of adult signatures obtained</label> <div class="col-md-4"> <div class="input-group"> <input id="no-of-adult-signatures-obtained" name="no-of-adult-signatures-obtained" class="form-control" placeholder="0" type="number" min=0 required=""> <span class="input-group-addon">/ ' + no_of_adult_signatures_required + '</span> </div></div></div><div class="form-group"> <label class="col-md-6 control-label" for="no-of-child-signatures-obtained">No of child signatures obtained</label> <div class="col-md-4"> <div class="input-group"> <input id="no-of-child-signatures-obtained" name="no-of-child-signatures-obtained" class="form-control" placeholder="0" type="number" value=0 min=0  required=""> <span class="input-group-addon">/ ' + no_of_child_signatures_required + '</span> </div></div></div><div class="form-group">\
            <label class="col-md-6 control-label" for="adult-clients">Adult Client names</label><div class="col-md-4" id="adults-client-container">\
            <input id="adult-signature-names" type="text" name="adult-clients" class="form-control input-md tags adult-signature-names"  data-role="tagsinput" required/>\
            </div></div>\
            <div class="form-group"><label class="col-md-6 control-label" for="child-clients">Child Client names</label><div class="col-md-4" id="adults-client-container">\
            <input id="child-signature-names" type="text" name="child-clients" class="form-control input-md tags child-signature-names"  data-role="tagsinput" required/>\
            </div></div><div class="form-group"> <label class="col-md-6 control-label" for="mileage-description">No. of miles travelled</label> <div class="col-md-4"> <input id="mileage-description" name="mileage-description" type="number"min=0 placeholder="0.0"  class="form-control input-md" required=""> </div></div><div class="form-group"> <label class="col-md-6 control-label" for="out-of-pocket-expenses">Additional Expenses (if any)</label> <div class="col-md-4"> <div class="input-group"> <span class="input-group-addon">$</span> <input id="out-of-pocket-expenses" name="out-of-pocket-expenses" class="form-control" placeholder="0.00" value=0 min=0  type="number"> </div></div></div><div class="form-group"> <label class="col-md-6 control-label" for="signature-obtained-more-info">More Info</label> <div class="col-md-4"> <input id="signature-obtained-more-info" name="signature-obtained-more-info" type="text" placeholder="Required if additional expenses have beem incurred" class="form-control input-md"> </div></div></div><h6 style="color:red">*Client Names Spelling are Critical</h6>',
            // html: '<input style="display: block;" class="swal2-input" id="mileage-description" placeholder="Mileage description" type="text">\
            //     <input style="display: block;" class="swal2-input" id="out-of-pocket-expenses" placeholder="Out of pocket expenses" type="text">\
            //     <input style="display: block;" class="swal2-input" id="signature-obtained-more-info" placeholder="More info (optional)" type="text">',
            preConfirm: function () {
                return new Promise(function (resolve, reject) {

                    var mileageDescription = $('#mileage-description').val();
                    var outOfPocketExpenses = $('#out-of-pocket-expenses').val();
                    var noOfAdultSignaturesObtained = $('#no-of-adult-signatures-obtained').val();
                    var noOfChildSignaturesObtained = $('#no-of-child-signatures-obtained').val();
                    var moreInfo = $("#signature-obtained-more-info").val();
                    var adultClients = $('.adult-signature-names').val();
                    var childClients = $('.child-signature-names').val();
                    var adultClientNames = adultClients ? adultClients.split(",") : [];
                    var childClientNames = childClients ? childClients.split(",") : [];
                    debugger;
                    if (noOfAdultSignaturesObtained && noOfChildSignaturesObtained && mileageDescription && outOfPocketExpenses) {

                        if (isNaN(noOfAdultSignaturesObtained)) {
                            reject("The number of Adult signatures obtained should be a number");
                        } else if (isNaN(noOfChildSignaturesObtained)) {
                            reject("The number of Child signatures obtained should be a number");
                        }
                        else if (isNaN(mileageDescription)) {
                            reject("The mileage description should be a number");
                        } else if (isNaN(outOfPocketExpenses)) {
                            reject("The Out of pocket expenses should be a number");
                        } else {

                            if (Number.parseFloat(outOfPocketExpenses) > 0.0 && (!moreInfo || moreInfo == '')) {
                                reject("More info is required if Out of pocket expenses were made");
                            }

                            var adult_signatures_obtained = parseInt(noOfAdultSignaturesObtained);
                            var child_signatures_obtained = parseInt(noOfChildSignaturesObtained);
                            if (adult_signatures_obtained != adultClientNames.length) {
                                reject("The Number of adult client names provided should be equal to no of adult signature obtained");
                            }

                            if (child_signatures_obtained != childClientNames.length) {
                                reject("The Number of child client names provided should be equal to no of adult signature obtained");
                            }

                            resolve({
                                'Mileage Description': $('#mileage-description').val(),
                                'Out of pocket expenses': $('#out-of-pocket-expenses').val(),
                                'More Info': $('#signature-obtained-more-info').val(),
                                'no_of_adult_signatures_obtained': noOfAdultSignaturesObtained,
                                'no_of_child_signatures_obtained': noOfChildSignaturesObtained,
                                'adult_client_names': adultClients,
                                'child_client_names': childClients
                            });
                        }
                    } else {
                        reject('Please fill in No. of adult & child signatures obtained, No. of Miles travelled & Additional expenses');
                    }

                });
            }
        }).then(function (signature_details) {
            change_status_call(JSON.stringify(signature_details));
        }, function () {
        });
    } else if (selected_status === 'Signature not obtained') {
        swal({
            title: 'Please enter the information below',
            confirmButtonText: 'Submit',
            html: '<div style="" class="form-horizontal"><div class="form-group"> <label class="col-md-6 control-label" for="mileage-description">No. of miles travelled</label> <div class="col-md-4"> <input id="mileage-description" name="mileage-description" type="number" placeholder="0.0" min=0 class="form-control input-md" required=""> </div></div><div class="form-group"> <label class="col-md-6 control-label" for="out-of-pocket-expenses">Additional Expenses (if any)</label> <div class="col-md-4"> <div class="input-group"> <span class="input-group-addon">$</span> <input id="out-of-pocket-expenses" name="out-of-pocket-expenses" class="form-control" placeholder="0.00" min=0 type="number"> </div></div></div><div class="form-group"> <label class="col-md-6 control-label" for="signature-obtained-more-info">More Info</label> <div class="col-md-4"> <input id="signature-obtained-more-info" name="signature-obtained-more-info" type="text" placeholder="Required if additional expenses have beem incurred" class="form-control input-md"> </div></div></div>',
            // html: '<input style="display: block;" class="swal2-input" id="mileage-description" placeholder="Mileage description" type="text">\
            //     <input style="display: block;" class="swal2-input" id="out-of-pocket-expenses" placeholder="Out of pocket expenses" type="text">\
            //     <input style="display: block;" class="swal2-input" id="signature-obtained-more-info" placeholder="More info (optional)" type="text">',
            preConfirm: function () {
                return new Promise(function (resolve, reject) {

                    var mileageDescription = $('#mileage-description').val();
                    var outOfPocketExpenses = $('#out-of-pocket-expenses').val();
                    var moreInfo = $("#signature-obtained-more-info").val();

                    if (mileageDescription && outOfPocketExpenses) {

                        if (isNaN(mileageDescription)) {
                            reject("The mileage description should be a number");
                        } else if (isNaN(outOfPocketExpenses)) {
                            reject("The Out of pocket expenses should be a number");
                        } else {

                            if (Number.parseFloat(outOfPocketExpenses) > 0.0 && (!moreInfo || moreInfo == '')) {
                                reject("More info is required if Out of pocket expenses were made");
                            }

                            resolve({
                                'Mileage Description': $('#mileage-description').val(),
                                'Out of pocket expenses': $('#out-of-pocket-expenses').val(),
                                'More Info': $('#signature-obtained-more-info').val()
                            });
                        }
                    } else {
                        reject('Please fill in No. of Miles travelled & Additional expenses');
                    }
                });
            }
        }).then(function (signature_details) {
            change_status_call(JSON.stringify(signature_details));
        }, function () {
        });
    } else if (selected_status === 'Closed') {

        var case_result = $('#extra-params').attr('data-case-result')
        if (case_result.toLowerCase() == 'client cancelled') {

            swal({
                title: 'What is the case rating?',
                confirmButtonText: 'Submit',
                html: '<div class="swal2-radio" style="display: block;">\
                  <input name="rating-stars" type="hidden" value="">\
                  <span class="rating">\
                      <span class="star"></span>\
                      <span class="star"></span>\
                      <span class="star filled"></span>\
                      <span class="star"></span>\
                      <span class="star"></span>\
                  </span>\
            </div>',
                preConfirm: function () {
                    return new Promise(function (resolve, reject) {

                        var additional_expenses = 0,
                            no_of_miles = 0,
                            rsn_extra_expenses = 0;
                        resolve({
                            'Rating': $('.star.filled ~ .star').size() + 1,
                            'Out of pocket expenses': Number.parseFloat(additional_expenses) > 0.0 ? additional_expenses : '0',
                            'Mileage Description': Number.parseFloat(no_of_miles) > 0.0 ? no_of_miles : '0',
                            'More Info': '',
                            'RSN Expenses':Number.parseFloat(rsn_extra_expenses) > 0.0 ? rsn_extra_expenses : '0',
                            'RSN extra expenses info': ''
                        });
                    });
                }
            }).then(function (close_data) {
                change_status_call(JSON.stringify(close_data));
            }, function () {

            });

        } else {


            swal({
                title: 'What is the case rating?',
                confirmButtonText: 'Submit',
                html: '<div class="swal2-radio" style="display: block;">\
                  <input name="rating-stars" type="hidden" value="">\
                  <span class="rating">\
                      <span class="star"></span>\
                      <span class="star"></span>\
                      <span class="star filled"></span>\
                      <span class="star"></span>\
                      <span class="star"></span>\
                  </span>\
            </div>\
            <div class="case-extras">\
                <h5>No. of miles travelled</h5>\
                <p>' + no_of_miles + '</p>\
                <h5>Additional expenses</h5>\
                <p>' + additional_expenses + '</p>\
            </div>\
            <input style="display: block;" class="form-control" id="closed-no-of-miles-travelled" placeholder="No. of miles travelled" min=0 type="number"><br>\
            <input style="display: block;" class="form-control" id="closed-additional-expenses" placeholder="Additional expenses (Investigator)" min=0 type="number"><br>\
            <input style="display: block;" class="form-control" id="closed-more-info" placeholder="More info about Additional expenses (optional)" min=0 type="text"><br>\
            <h5>RSN Addtional Expenses</h5>\
            <input style="display: block;" class="form-control" id="closed-rsn-extra-expenses" placeholder="RSN extra expenses" min=0 value=0 type="number"><br>\
            <input style="display: block;" class="form-control" id="closed-rsn-extra-expenses-info" placeholder="More info RSN expenses (optional)" min=0 type="text">',
                preConfirm: function () {
                    return new Promise(function (resolve, reject) {

                        var additional_expenses = $('#closed-additional-expenses').val(),
                            no_of_miles = $('#closed-no-of-miles-travelled').val(),
                            more_info = $("#closed-more-info").val(),
                            rsn_extra_expenses = $('#closed-rsn-extra-expenses').val(),
                            rsn_extra_expenses_info = $('#closed-rsn-extra-expenses-info').val();
                        if (additional_expenses === '' || isNaN(additional_expenses)) {
                            reject('Please fill in additional expenses');
                        } else if (rsn_extra_expenses === '' || isNaN(rsn_extra_expenses)) {
                            reject('Please fill in RSN extra expenses');
                        } else if (no_of_miles === '' || isNaN(no_of_miles)) {
                            reject('Please fill in no. of miles');
                        } else if (Number.parseFloat(additional_expenses) > 0.0 && more_info == "") {
                            reject('If additional expenses were incurred, please fill in more info as well');
                        } else if (Number.parseFloat(rsn_extra_expenses) > 0.0 && rsn_extra_expenses_info == "") {
                            reject('If RSN extra expenses were incurred, please fill in more info RSN expenses as well');
                        } else {
                            resolve({
                                'Rating': $('.star.filled ~ .star').size() + 1,
                                'Out of pocket expenses': additional_expenses,
                                'Mileage Description': no_of_miles,
                                'More Info': $('#closed-more-info').val(),
                                'RSN extra expenses': rsn_extra_expenses,
                                'RSN extra expenses info' : rsn_extra_expenses_info
                            });
                        }
                    });
                }
            }).then(function (close_data) {
                change_status_call(JSON.stringify(close_data));
            }, function () {

            });
        }

        $('.rating:not(.fixed) .star').click(function () {
            $('.rating .star').removeClass('filled');
            $(this).addClass('filled');
        });

    } else {
        swal({
            title: 'More info',
            text: 'If there is additional info, please write it down',
            input: 'text',
            confirmButtonText: 'Submit',

            inputValidator: function (value) {
                return new Promise(function (resolve, reject) {
                    if (value) {
                        resolve();
                    } else {
                        resolve();
                        // reject('You need to write something!');
                    }
                });
            }
        }).then(function (value) {
            if (!value || value == '') {
                value = 'No additional Info provided'
            }
            change_status_call(JSON.stringify({ 'More info': value }));
        }, function () {
        });
    }

});


var UpdateStatusAllCases = function () { $('.status-change a').click(function () {
    'use strict';

    debugger;

    var selected_status = $(this).attr('data-case-status'), change_status_call, case_id = $(this).parent().parent().attr('data-case-id');
    selected_status = selected_status.substring(0, 1).toLocaleUpperCase() + selected_status.substring(1);
    selected_status = selected_status.split('-').join(' ');

    change_status_call = function (extra_info) {
        if (!extra_info) {
            return;
        }

        $('#adult-signature-names').remove();
        $('#child-signature-names').remove();
        
        debugger;
        $.post('/broker/change-status/', {
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            case_id: case_id,
            new_status: selected_status,
            extra_info: extra_info
        }, function (data) {
            swal({
                title: 'Status changed',
                text: 'The status has been changed',
                type: 'success',
                timer: 2000,
                showConfirmButton: false
            });

            setTimeout(function () {
                location.reload();
            }, 2000);

        }).fail(function (error) {
            debugger;
            swal({
                title: 'Unable to change status',
                text: 'Unable to change status of the case as either an active Invoice already exists or the investigator has been marked as paid',
                // text: error.responseText,
                type: 'error',
                showConfirmButton: true

            });
            console.log(JSON.stringify(error.responseText, null, 2));
        });


    };
    //For all cases screen

    if (selected_status === 'Client cancelled') {

        function cancelledOptions() {
            $('input[type=radio][name=cancelled-by]').change(function () {
                // debugger;
                if (this.value == 'Client cancelled') {
                    $('.client-cancelled-radios').show();
                }
                else if (this.value == 'Firm decision') {
                    $('.client-cancelled-radios').hide();
                }
            });
        }

        swal({
            title: 'Cancelled',
            confirmButtonText: 'Submit',
            showCancelButton: true,
            onOpen: cancelledOptions,
            html: '<div class="swal2-radios" style="display: block;">\
            <div class="cancelled">\
            <label>\
                <input type="radio" name="cancelled-by" value="Client cancelled" style="margin-top:2px">\
                <span style="margin-left: -10px;">Client Cancelled</span>\
                <input type="radio" name="cancelled-by" value="Firm decision" style="margin-top:2px">\
                <span style="margin-left: -10px;">Firm Decision</span></label>\
                </div>\
                \
                <div class="client-cancelled-radios" style="display:none;margin-top:60px">\
                <p>Why did the Client cancel ?</p>\
                <label>\
                <input type="radio" name="cancel-reason-radio" value="Changed mind" style="margin-top:2px">\
                <span style="margin-left: -10px;">Changed mind</span>\
                <input type="radio" name="cancel-reason-radio" value="Found new firm" style="margin-top:2px">\
                <span style="margin-left: -10px;">Found new firm</span>\
            </label>\
            <label>\
            <input type="radio" name="cancel-reason-radio" value="Client did not responded" style="margin-top:2px">\
                <span style="margin-left: -10px;">Client did not responded</span>\
                <label>\
            </div>\
                \
            </div>\
            <input style="display: block;" class="swal2-input" id="client-cancelled-more-info" placeholder="More info (optional)" type="text">',
            preConfirm: function () {
                return new Promise(function (resolve, reject) {
                    var cancelledBy = $('input[name="cancelled-by"]:checked');
                    var cancellationReason = $('input[name="cancel-reason-radio"]:checked');
                    if (cancelledBy.val() == 'Firm decision') {
                        resolve({
                            'Cancelled by': cancelledBy.val(),
                            'Cancellation reason': '',
                            'More Info': $('#client-cancelled-more-info').val()
                        });
                    }

                    else if (cancelledBy.size() > 0 && cancellationReason.size() > 0) {


                        resolve({
                            'Cancelled by': cancelledBy.val(),
                            'Cancellation reason': cancellationReason.val(),
                            'More Info': $('#client-cancelled-more-info').val()
                        });


                    } else {
                        reject('You need to select one of the options');
                    }
                });
            }
        }).then(function (cancel_data) {
            change_status_call(JSON.stringify(cancel_data));
        }, function () { });
    } else if (selected_status === 'Signature obtained') {
        debugger;
        var no_of_adult_signatures_required = $(this).attr("data-no-of-adult-signatures-required");
        var no_of_child_signatures_required = $(this).attr("data-no-of-child-signatures-required")
        function setTagsInput(modalEle) {


            $('#adult-signature-names').tagsInput({
                width: 'auto',
                defaultText: ''
            });
            $('#child-signature-names').tagsInput({
                width: 'auto',
                defaultText: ''
            });


        }
        swal({
            title: 'Please enter the information below',
            confirmButtonText: 'Submit',
            onOpen: setTagsInput,
            html: '<div style="" class="form-horizontal"><div class="form-group"> <label class="col-md-6 control-label" for="no-of-adult-signatures-obtained">No. of adult signatures obtained</label> <div class="col-md-4"> <div class="input-group"> <input id="no-of-adult-signatures-obtained" name="no-of-adult-signatures-obtained" class="form-control" placeholder="0" type="number" min=0 required=""> <span class="input-group-addon">/ ' + no_of_adult_signatures_required + '</span> </div></div></div><div class="form-group"> <label class="col-md-6 control-label" for="no-of-child-signatures-obtained">No of child signatures obtained</label> <div class="col-md-4"> <div class="input-group"> <input id="no-of-child-signatures-obtained" name="no-of-child-signatures-obtained" class="form-control" placeholder="0" type="number" value=0 min=0  required=""> <span class="input-group-addon">/ ' + no_of_child_signatures_required + '</span> </div></div></div><div class="form-group">\
            <label class="col-md-6 control-label" for="adult-clients">Adult Client names</label><div class="col-md-4" id="adults-client-container">\
            <input id="adult-signature-names" type="text" name="adult-clients" class="form-control input-md tags adult-signature-names"  data-role="tagsinput" required/>\
            </div></div>\
            <div class="form-group"><label class="col-md-6 control-label" for="child-clients">Child Client names</label><div class="col-md-4" id="adults-client-container">\
            <input id="child-signature-names" type="text" name="child-clients" class="form-control input-md tags child-signature-names"  data-role="tagsinput" required/>\
            </div></div><div class="form-group"> <label class="col-md-6 control-label" for="mileage-description">No. of miles travelled</label> <div class="col-md-4"> <input id="mileage-description" name="mileage-description" type="number" min=0 placeholder="0.0"  class="form-control input-md" required=""> </div></div><div class="form-group"> <label class="col-md-6 control-label" for="out-of-pocket-expenses">Additional Expenses (if any)</label> <div class="col-md-4"> <div class="input-group"> <span class="input-group-addon">$</span> <input id="out-of-pocket-expenses" name="out-of-pocket-expenses" class="form-control" placeholder="0.00" value=0 min=0 type="number"> </div></div></div><div class="form-group"> <label class="col-md-6 control-label" for="signature-obtained-more-info">More Info</label> <div class="col-md-4"> <input id="signature-obtained-more-info" name="signature-obtained-more-info" type="text" placeholder="Required if additional expenses have beem incurred" class="form-control input-md"> </div></div></div><h6 style="color:red">*Client Names Spelling are Critical</h6>',
            // html: '<input style="display: block;" class="swal2-input" id="mileage-description" placeholder="Mileage description" type="text">\
            //     <input style="display: block;" class="swal2-input" id="out-of-pocket-expenses" placeholder="Out of pocket expenses" type="text">\
            //     <input style="display: block;" class="swal2-input" id="signature-obtained-more-info" placeholder="More info (optional)" type="text">',
            preConfirm: function () {
                return new Promise(function (resolve, reject) {

                    var mileageDescription = $('#mileage-description').val();
                    var outOfPocketExpenses = $('#out-of-pocket-expenses').val();
                    var noOfAdultSignaturesObtained = $('#no-of-adult-signatures-obtained').val();
                    var noOfChildSignaturesObtained = $('#no-of-child-signatures-obtained').val();
                    var moreInfo = $("#signature-obtained-more-info").val();
                    var adultClients = $('.adult-signature-names').val();
                    var childClients = $('.child-signature-names').val();
                    var adultClientNames = adultClients ? adultClients.split(",") : [];
                    var childClientNames = childClients ? childClients.split(",") : [];
                    debugger;
                    if (noOfAdultSignaturesObtained && noOfChildSignaturesObtained && mileageDescription && outOfPocketExpenses) {

                        if (isNaN(noOfAdultSignaturesObtained)) {
                            reject("The number of Adult signatures obtained should be a number");
                        } else if (isNaN(noOfChildSignaturesObtained)) {
                            reject("The number of Child signatures obtained should be a number");
                        } else if (isNaN(mileageDescription)) {
                            reject("The mileage description should be a number");
                        } else if (isNaN(outOfPocketExpenses)) {
                            reject("The Out of pocket expenses should be a number");
                        } else {

                            if (Number.parseFloat(outOfPocketExpenses) > 0.0 && (!moreInfo || moreInfo == '')) {
                                reject("More info is required if Out of pocket expenses were made");
                            }

                            var adult_signatures_obtained = parseInt(noOfAdultSignaturesObtained);
                            var child_signatures_obtained = parseInt(noOfChildSignaturesObtained);
                            // var additional_money = parseInt(outOfPocketExpenses);
                            // var extra_miles = parseInt(mileageDescription);
                            // if (adult_signatures_obtained < 0) {
                            //     reject("The Number of adult signature obtained cannot be negative value");
                            // }
                            // if (child_signatures_obtained < 0) {
                            //     reject("The Number of child signature obtained cannot be negative value");
                            // }
                            // if (additional_money < 0) {
                            //     reject("No of miles travelled cannot be negative value");
                            // }
                            // if (extra_miles < 0) {
                            //     reject("Additional expenses cannot be negative value");
                            // }
                            if (adult_signatures_obtained != adultClientNames.length) {
                                reject("The Number of adult client names provided should be equal to no of adult signature obtained");
                            }

                            if (child_signatures_obtained != childClientNames.length) {
                                reject("The Number of child client names provided should be equal to no of adult signature obtained");
                            }

                            resolve({
                                'Mileage Description': $('#mileage-description').val(),
                                'Out of pocket expenses': $('#out-of-pocket-expenses').val(),
                                'More Info': $('#signature-obtained-more-info').val(),
                                'no_of_adult_signatures_obtained': noOfAdultSignaturesObtained,
                                'no_of_child_signatures_obtained': noOfChildSignaturesObtained,
                                'adult_client_names': adultClients,
                                'child_client_names': childClients
                            });
                        }
                    } else {
                        reject('Please fill in No. of adult & child signatures obtained, No. of Miles travelled & Additional expenses');
                    }

                });
            }
        }).then(function (signature_details) {
            change_status_call(JSON.stringify(signature_details));
        }, function () {
        });
    } else if (selected_status === 'Signature not obtained') {
        swal({
            title: 'Please enter the information below',
            confirmButtonText: 'Submit',
            html: '<div style="" class="form-horizontal"><div class="form-group"> <label class="col-md-6 control-label" for="mileage-description">No. of miles travelled</label> <div class="col-md-4"> <input id="mileage-description" name="mileage-description" type="number" min=0 placeholder="0.0" class="form-control input-md" required=""> </div></div><div class="form-group"> <label class="col-md-6 control-label" for="out-of-pocket-expenses">Additional Expenses (if any)</label> <div class="col-md-4"> <div class="input-group"> <span class="input-group-addon">$</span> <input id="out-of-pocket-expenses" name="out-of-pocket-expenses" class="form-control" placeholder="0.00"  min=0 type="number"> </div></div></div><div class="form-group"> <label class="col-md-6 control-label" for="signature-obtained-more-info">More Info</label> <div class="col-md-4"> <input id="signature-obtained-more-info" name="signature-obtained-more-info" type="text" placeholder="Required if additional expenses have beem incurred" class="form-control input-md"> </div></div></div>',
            // html: '<input style="display: block;" class="swal2-input" id="mileage-description" placeholder="Mileage description" type="text">\
            //     <input style="display: block;" class="swal2-input" id="out-of-pocket-expenses" placeholder="Out of pocket expenses" type="text">\
            //     <input style="display: block;" class="swal2-input" id="signature-obtained-more-info" placeholder="More info (optional)" type="text">',
            preConfirm: function () {
                return new Promise(function (resolve, reject) {

                    var mileageDescription = $('#mileage-description').val();
                    var outOfPocketExpenses = $('#out-of-pocket-expenses').val();
                    var moreInfo = $("#signature-obtained-more-info").val();

                    if (mileageDescription && outOfPocketExpenses) {

                        if (isNaN(mileageDescription)) {
                            reject("The mileage description should be a number");
                        } else if (isNaN(outOfPocketExpenses)) {
                            reject("The Out of pocket expenses should be a number");
                        } else {

                            if (Number.parseFloat(outOfPocketExpenses) > 0.0 && (!moreInfo || moreInfo == '')) {
                                reject("More info is required if Out of pocket expenses were made");
                            }

                            resolve({
                                'Mileage Description': $('#mileage-description').val(),
                                'Out of pocket expenses': $('#out-of-pocket-expenses').val(),
                                'More Info': $('#signature-obtained-more-info').val()
                            });
                        }
                    } else {
                        reject('Please fill in No. of Miles travelled & Additional expenses');
                    }
                });
            }
        }).then(function (signature_details) {
            change_status_call(JSON.stringify(signature_details));
        }, function () {
        });
    } else if (selected_status === 'Closed') {

        var case_result = $(this).attr('data-case-final-status')
        if (case_result.toLowerCase() == 'client cancelled') {

            swal({
                title: 'What is the case rating?',
                confirmButtonText: 'Submit',
                html: '<div class="swal2-radio" style="display: block;">\
                  <input name="rating-stars" type="hidden" value="">\
                  <span class="rating">\
                      <span class="star"></span>\
                      <span class="star"></span>\
                      <span class="star filled"></span>\
                      <span class="star"></span>\
                      <span class="star"></span>\
                  </span>\
            </div>',
                preConfirm: function () {
                    return new Promise(function (resolve, reject) {

                        var additional_expenses = 0,
                            no_of_miles = 0,
                            rsn_extra_expenses = 0;
                        resolve({
                            'Rating': $('.star.filled ~ .star').size() + 1,
                            'Out of pocket expenses': additional_expenses,
                            'Mileage Description': no_of_miles,
                            'More Info': '',
                            'RSN Expenses':Number.parseFloat(rsn_extra_expenses) > 0.0 ? rsn_extra_expenses : '0',
                            'RSN extra expenses info': ''
                        });
                    });
                }
            }).then(function (close_data) {
                change_status_call(JSON.stringify(close_data));
            }, function () {

            });

        } else {

            var no_of_miles = $(this).attr("data-no-of-miles-travelled");
            var additional_expenses = $(this).attr("data-additional-expenses-text")


            swal({
                title: 'What is the case rating?',
                confirmButtonText: 'Submit',
                html: '<div class="swal2-radio" style="display: block;">\
                  <input name="rating-stars" type="hidden" value="">\
                  <span class="rating">\
                      <span class="star"></span>\
                      <span class="star"></span>\
                      <span class="star filled"></span>\
                      <span class="star"></span>\
                      <span class="star"></span>\
                  </span>\
            </div>\
            <div class="case-extras">\
                <h5>No. of miles travelled</h5>\
                <p>' + no_of_miles + '</p>\
                <h5>Additional expenses</h5>\
                <p>' + additional_expenses + '</p>\
            </div>\
            <input style="display: block;" class="form-control" id="closed-no-of-miles-travelled" placeholder="No. of miles travelled" min=0 type="number"><br>\
            <input style="display: block;" class="form-control" id="closed-additional-expenses" placeholder="Additional expenses (Investigator)" min=0 type="number"><br>\
            <input style="display: block;" class="form-control" id="closed-more-info" placeholder="More info for additonal expenses(optional)" min=0 type="text"><br>\
            <h5>RSN Addtional Expenses</h5>\
            <input style="display: block;" class="form-control" id="closed-rsn-extra-expenses" placeholder="RSN extra expenses" min=0 value=0 type="number"><br>\
            <input style="display: block;" class="form-control" id="closed-rsn-extra-expenses-info" placeholder="More info RSN expenses (optional)" min=0 type="text">',
                preConfirm: function () {
                    return new Promise(function (resolve, reject) {

                        var additional_expenses_closed = $('#closed-additional-expenses').val(),
                            no_of_miles_closed = $('#closed-no-of-miles-travelled').val(),
                            more_info = $('#closed-more-info').val(),
                            rsn_extra_expenses = $('#closed-rsn-extra-expenses').val(),
                            rsn_extra_expenses_info = $('#closed-rsn-extra-expenses-info').val();
                        if (additional_expenses_closed === '' || isNaN(additional_expenses_closed)) {
                            reject('Please fill in additional expenses');
                        } else if (rsn_extra_expenses === '' || isNaN(rsn_extra_expenses)) {
                            reject('Please fill in RSN extra expenses');
                        } else if (no_of_miles_closed === '' || isNaN(no_of_miles_closed)) {
                            reject('Please fill in no. of miles');
                        } else if (Number.parseFloat(additional_expenses_closed) > 0.0 && more_info == "") {
                            reject('If additional expenses were incurred, please fill in more info as well');
                        } else if (Number.parseFloat(rsn_extra_expenses) > 0.0 && rsn_extra_expenses_info == "") {
                            reject('If RSN extra expenses were incurred, please fill in more info RSN expenses as well');
                        }
                        else {
                            resolve({
                                'Rating': $('.star.filled ~ .star').size() + 1,
                                'Out of pocket expenses': additional_expenses_closed,
                                'Mileage Description': no_of_miles_closed,
                                'More Info': more_info,
                                'RSN extra expenses': rsn_extra_expenses,
                                'RSN extra expenses info' : rsn_extra_expenses_info
                            });
                        }
                    });
                }
            }).then(function (close_data) {
                change_status_call(JSON.stringify(close_data));
            }, function () {

            });
        }

        $('.rating:not(.fixed) .star').click(function () {
            $('.rating .star').removeClass('filled');
            $(this).addClass('filled');
        });

    } else {
        swal({
            title: 'More info',
            text: 'If there is additional info, please write it down',
            input: 'text',
            confirmButtonText: 'Submit',
            inputValidator: function (value) {
                return new Promise(function (resolve, reject) {
                    resolve();
                });
            }
        }).then(function (value) {
            if (!value || value == '') {
                value = "No additional information provided"
            }
            change_status_call(JSON.stringify({ 'More info': value }));
        }, function () { });
    }

});
};

$('.details-tab').click(function () {
    'use strict';
    $('.tab-target').removeClass('show');
    $('.tab-target[data-target-value="' + $(this).attr('data-target') + '"]').addClass('show');
});

var extraInfoHolder = function(){ $('.extra-info-holder').click(function () {
    'use strict';

    var info_object = JSON.parse($(this).attr('data-stringified-info')), html_string = '', key;
    var field
    for (key in info_object) {
        field = key.replace(/_/g, " ")
        field = field.charAt(0).toUpperCase() + field.slice(1);
        if (info_object.hasOwnProperty(key)) {
            html_string += '<h4>' + field + '</h4>';
            html_string += '<p>' + info_object[key] + '</p>';
        }
    }

    swal({
        title: 'Status Details',
        html: html_string,
        customClass: 'details-popup'
    });
});
};