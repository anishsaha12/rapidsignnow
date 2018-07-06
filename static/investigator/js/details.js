/*global $, swal, Promise, case_id */
/*jslint es5:true */

$('#updateStatusBtn').click(function () {
    'use strict';
    
    var selected_status = $('input[name=case-status-radio]:checked').val(), change_status_call;
    selected_status = selected_status.substring(0, 1).toLocaleUpperCase() + selected_status.substring(1);
    selected_status = selected_status.split('-').join(' ');
    
    change_status_call = function (extra_info) {
        $.post('/investigator/change-status/', {
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

    if (selected_status === 'Client cancelled') {

        function cancelledOptions(){
            $('input[type=radio][name=cancelled-by]').change(function() {
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
                <input type="radio" name="cancelled-by" value="Client cancelled">\
                <span>Client Cancelled</span>\
                <input type="radio" name="cancelled-by" value="Firm decision">\
                <span>Firm Decision</span></label>\
                </div>\
                \
                <div class="client-cancelled-radios" style="display:none;margin-top:60px">\
                <p>Why Did Client Cancelled ?</p>\
                <label>\
                    <input type="radio" name="cancel-reason-radio" value="Changed mind">\
                    <span>Changed mind</span>\
                    <input type="radio" name="cancel-reason-radio" value="Found new firm">\
                    <span>Found new firm</span>\
                </label>\
                <label>\
                <input type="radio" name="cancel-reason-radio" value="Client did not responded">\
                    <span>Client did not responded</span>\
                    <label>\
                </div>\
                \
            </div>\
            <input style="display: block;" class="swal2-input" id="client-cancelled-more-info" placeholder="More info (optional)" type="text">',
            preConfirm: function () {
                return new Promise(function (resolve, reject) {
                    var cancelledBy = $('input[name="cancelled-by"]:checked');
                    var cancellationReason = $('input[name="cancel-reason-radio"]:checked');
                    
                    if(cancelledBy.val() =='Firm decision'){
                        resolve({
                            'Cancelled by':cancelledBy.val(),
                            'Cancellation reason': '',
                            'More Info': $('#client-cancelled-more-info').val()
                        });
                    }

                    else  if (cancelledBy.size() > 0 && cancellationReason.size() > 0) {           
                                                resolve({
                                                    'Cancelled by':cancelledBy.val(),
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
        }, function () {});
    } else if ( selected_status === 'Signature not obtained') {
        swal({
            title: 'Please enter the information below',
            confirmButtonText: 'Submit',
            html:'<div style="" class="form-horizontal"><div class="form-group"> <label class="col-md-6 control-label" for="mileage-description">No. of miles travelled</label> <div class="col-md-4"> <input id="mileage-description" name="mileage-description" type="number" min=0 placeholder="0.0" class="form-control input-md" required=""> </div></div><div class="form-group"> <label class="col-md-6 control-label" for="out-of-pocket-expenses">Additional Expenses (if any)</label> <div class="col-md-4"> <div class="input-group"> <span class="input-group-addon">$</span> <input id="out-of-pocket-expenses" name="out-of-pocket-expenses" class="form-control" placeholder="0.00" min=0 type="number"> </div></div></div><div class="form-group"> <label class="col-md-6 control-label" for="signature-obtained-more-info">More Info</label> <div class="col-md-4"> <input id="signature-obtained-more-info" name="signature-obtained-more-info" type="text" placeholder="Required if additional expenses have beem incurred" class="form-control input-md"> </div></div></div>',
            // html: '<input style="display: block;" class="swal2-input" id="mileage-description" placeholder="Mileage description" type="text">\
            //     <input style="display: block;" class="swal2-input" id="out-of-pocket-expenses" placeholder="Out of pocket expenses" type="text">\
            //     <input style="display: block;" class="swal2-input" id="signature-obtained-more-info" placeholder="More info (optional)" type="text">',
            preConfirm: function () {
                return new Promise(function (resolve, reject) {

                    var mileageDescription = $('#mileage-description').val();
                    var outOfPocketExpenses = $('#out-of-pocket-expenses').val();
                    var moreInfo = $("#signature-obtained-more-info").val();

                    if ( mileageDescription && outOfPocketExpenses) {

                        if (isNaN(mileageDescription)) {
                            reject("The mileage description should be a number");
                        } else if (isNaN(outOfPocketExpenses)) {
                            reject("The Out of pocket expenses should be a number");
                        }  else {

                            if( Number.parseFloat(outOfPocketExpenses) >  0.0  &&  (!moreInfo || moreInfo == '')){
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
        }, function () {});
    }  else if (selected_status === 'Signature obtained' ) {
        var adultId = 'adult-input-'+Math.floor(Math.random()*100).toString()
        var childId = 'child-input-'+Math.floor(Math.random()*100).toString()
        
        function setTagsInput(modalEle){
            
            
                $('#adult-signature-names').tagsInput({
                width:'auto',
                defaultText: ''
                    });
                    $('#child-signature-names').tagsInput({
                        width:'auto' ,
                        defaultText: ''
                            });
                          
        }
        swal({
            title: 'Please enter the information below',
            confirmButtonText: 'Submit',
            onOpen: setTagsInput,
            html:'<div style="" class="form-horizontal"><div class="form-group"> <label class="col-md-6 control-label" for="no-of-adult-signatures-obtained">No. of adult signatures obtained</label> <div class="col-md-4"> <div class="input-group"> <input id="no-of-adult-signatures-obtained" name="no-of-adult-signatures-obtained" class="form-control" placeholder="0" type="number" min=0 required=""> <span class="input-group-addon">/ '+ no_of_adult_signatures_required + '</span> </div></div></div><div class="form-group"> <label class="col-md-6 control-label" for="no-of-child-signatures-obtained">No of child signatures obtained</label> <div class="col-md-4"> <div class="input-group"> <input id="no-of-child-signatures-obtained" name="no-of-child-signatures-obtained" class="form-control" placeholder="0"value=0 type="number" min=0  required=""> <span class="input-group-addon">/ '+no_of_child_signatures_required+'</span> </div></div></div><div class="form-group">\
            <label class="col-md-6 control-label" for="adult-clients">Adult Client names</label><div class="col-md-4" id="adults-client-container">\
            <input id="adult-signature-names" type="text" name="adult-clients" class="form-control input-md tags adult-signature-names"  data-role="tagsinput" required/>\
            </div></div>\
            <div class="form-group"><label class="col-md-6 control-label" for="child-clients">Child Client names</label><div class="col-md-4" id="adults-client-container">\
            <input id="child-signature-names" type="text" name="child-clients" class="form-control input-md tags child-signature-names"  data-role="tagsinput" required/>\
            </div></div><div class="form-group"> <label class="col-md-6 control-label" for="mileage-description">No. of miles travelled</label> <div class="col-md-4"> <input id="mileage-description" name="mileage-description" type="number" placeholder="0.0" min=0 class="form-control input-md" required=""> </div></div><div class="form-group"> <label class="col-md-6 control-label" for="out-of-pocket-expenses">Additional Expenses (if any)</label> <div class="col-md-4"> <div class="input-group"> <span class="input-group-addon">$</span> <input id="out-of-pocket-expenses" name="out-of-pocket-expenses" class="form-control" placeholder="0.00" value=0 min=0 type="number"> </div></div></div><div class="form-group"> <label class="col-md-6 control-label" for="signature-obtained-more-info">More Info</label> <div class="col-md-4"> <input id="signature-obtained-more-info" name="signature-obtained-more-info" type="text" placeholder="Required if additional expenses have beem incurred" class="form-control input-md"> </div></div></div><h6 style="color:red">*Client Names Spelling are Critical</h6>',
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
                    var adultClientNames = adultClients ?  adultClients.split(",") : []; 
                    var childClientNames = childClients ?  childClients.split(",") : []; 
                               
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
                        }  else {

                            if( Number.parseFloat(outOfPocketExpenses) >  0.0  &&  (!moreInfo || moreInfo == '')){
                                reject("More info is required if Out of pocket expenses were made");
                            }
                            
                            var adult_signatures_obtained = parseInt(noOfAdultSignaturesObtained);
                            var child_signatures_obtained = parseInt(noOfChildSignaturesObtained);
                            if( adult_signatures_obtained != adultClientNames.length){
                                reject("The Number of adult client names provided should be equal to no of adult signature obtained");
                            }

                            if( child_signatures_obtained != childClientNames.length){
                                reject("The Number of child client names provided should be equal to no of adult signature obtained");
                            }
                            resolve({
                                'Mileage Description': $('#mileage-description').val(),
                                'Out of pocket expenses': $('#out-of-pocket-expenses').val(),
                                'More Info': $('#signature-obtained-more-info').val(),
                                'no_of_adult_signatures_obtained':noOfAdultSignaturesObtained,
                                'no_of_child_signatures_obtained':noOfChildSignaturesObtained,
                                'adult_client_names':adultClients,
                                'child_client_names':childClients
                            });
                        }
                    } else {
                        reject('Please fill in No. of adult & child signatures obtained, No. of Miles travelled & Additional expenses');
                    }

                });
            }
        }).then(function (signature_details) {
            change_status_call(JSON.stringify(signature_details));
        }, function () {});
    }else {
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
            if(!value || value == ''){
                value = 'No additional Info provided'
            }
            change_status_call(JSON.stringify({'More info': value}));
        }, function () {});
    }

});

$('.status-change a').click(function () {
    'use strict';
    
    var selected_status = $(this).attr('data-case-status'), change_status_call, case_id = $(this).parent().parent().attr('data-case-id');
    selected_status = selected_status.substring(0, 1).toLocaleUpperCase() + selected_status.substring(1);
    selected_status = selected_status.split('-').join(' ');
    
    change_status_call = function (extra_info) {
        $.post('/investigator/change-status/', {
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
                location.assign('/investigator/all-cases/');
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

    if (selected_status === 'Client cancelled') {

        function cancelledOptions(){
            $('input[type=radio][name=cancelled-by]').change(function() {
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
                <input type="radio" name="cancelled-by" value="Client cancelled">\
                <span>Client Cancelled</span>\
                <input type="radio" name="cancelled-by" value="Firm decision">\
                <span>Firm Decision</span></label>\
                </div>\
                \
                <div class="client-cancelled-radios" style="display:none;margin-top:60px">\
                <p>Why Did Client Cancelled ?</p>\
                <label>\
                    <input type="radio" name="cancel-reason-radio" value="Changed mind">\
                    <span>Changed mind</span>\
                    <input type="radio" name="cancel-reason-radio" value="Found new firm">\
                    <span>Found new firm</span>\
                </label>\
                <label>\
                <input type="radio" name="cancel-reason-radio" value="Client did not responded">\
                    <span>Client did not responded</span>\
                    <label>\
                </div>\
                \
            </div>\
            <input style="display: block;" class="swal2-input" id="client-cancelled-more-info" placeholder="More info (optional)" type="text">',
            preConfirm: function () {
                return new Promise(function (resolve, reject) {
                    var cancelledBy = $('input[name="cancelled-by"]:checked');
                    var cancellationReason = $('input[name="cancel-reason-radio"]:checked');
                    
                    if(cancelledBy.val() =='Firm decision'){
                        resolve({
                            'Cancelled by':cancelledBy.val(),
                            'Cancellation reason': '',
                            'More Info': $('#client-cancelled-more-info').val()
                        });
                    }

                    else  if (cancelledBy.size() > 0 && cancellationReason.size() > 0) {           
                                                resolve({
                                                    'Cancelled by':cancelledBy.val(),
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
        }, function () {});
    } else if ( selected_status === 'Signature not obtained') {
        swal({
            title: 'Please enter the information below',
            confirmButtonText: 'Submit',
            html:'<div style="" class="form-horizontal"><div class="form-group"> <label class="col-md-6 control-label" for="mileage-description">No. of miles travelled</label> <div class="col-md-4"> <input id="mileage-description" name="mileage-description" type="number" min=0 placeholder="0.0" class="form-control input-md" required=""> </div></div><div class="form-group"> <label class="col-md-6 control-label" for="out-of-pocket-expenses">Additional Expenses (if any)</label> <div class="col-md-4"> <div class="input-group"> <span class="input-group-addon">$</span> <input id="out-of-pocket-expenses" name="out-of-pocket-expenses" class="form-control" placeholder="0.00" min=0 type="number"> </div></div></div><div class="form-group"> <label class="col-md-6 control-label" for="signature-obtained-more-info">More Info</label> <div class="col-md-4"> <input id="signature-obtained-more-info" name="signature-obtained-more-info" type="text" placeholder="Required if additional expenses have beem incurred" class="form-control input-md"> </div></div></div>',
            // html: '<input style="display: block;" class="swal2-input" id="mileage-description" placeholder="Mileage description" type="text">\
            //     <input style="display: block;" class="swal2-input" id="out-of-pocket-expenses" placeholder="Out of pocket expenses" type="text">\
            //     <input style="display: block;" class="swal2-input" id="signature-obtained-more-info" placeholder="More info (optional)" type="text">',
            preConfirm: function () {
                return new Promise(function (resolve, reject) {

                    var mileageDescription = $('#mileage-description').val();
                    var outOfPocketExpenses = $('#out-of-pocket-expenses').val();
                    var moreInfo = $("#signature-obtained-more-info").val();

                    if ( mileageDescription && outOfPocketExpenses) {

                        if (isNaN(mileageDescription)) {
                            reject("The mileage description should be a number");
                        } else if (isNaN(outOfPocketExpenses)) {
                            reject("The Out of pocket expenses should be a number");
                        }  else {

                            if( Number.parseFloat(outOfPocketExpenses) >  0.0  &&  (!moreInfo || moreInfo == '')){
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
        }, function () {});
    }  else if (selected_status === 'Signature obtained' ) {
        var adultId = 'adult-input-'+Math.floor(Math.random()*100).toString()
        var childId = 'child-input-'+Math.floor(Math.random()*100).toString()
        var no_of_adult_signatures_required = $(this).attr("data-no-of-adult-signatures-required");
        var no_of_child_signatures_required = $(this).attr("data-no-of-child-signatures-required")
        function setTagsInput(modalEle){
            
            
                $('#adult-signature-names').tagsInput({
                width:'auto',
                defaultText: ''
                    });
                    $('#child-signature-names').tagsInput({
                        width:'auto' ,
                        defaultText: ''
                            });
                          
        }
        swal({
            title: 'Please enter the information below',
            confirmButtonText: 'Submit',
            onOpen: setTagsInput,
            html:'<div style="" class="form-horizontal"><div class="form-group"> <label class="col-md-6 control-label" for="no-of-adult-signatures-obtained">No. of adult signatures obtained</label> <div class="col-md-4"> <div class="input-group"> <input id="no-of-adult-signatures-obtained" name="no-of-adult-signatures-obtained" class="form-control" placeholder="0" type="number" min=0 required=""> <span class="input-group-addon">/ '+ no_of_adult_signatures_required + '</span> </div></div></div><div class="form-group"> <label class="col-md-6 control-label" for="no-of-child-signatures-obtained">No of child signatures obtained</label> <div class="col-md-4"> <div class="input-group"> <input id="no-of-child-signatures-obtained" name="no-of-child-signatures-obtained" class="form-control" placeholder="0"value=0 type="number" min=0  required=""> <span class="input-group-addon">/ '+no_of_child_signatures_required+'</span> </div></div></div><div class="form-group">\
            <label class="col-md-6 control-label" for="adult-clients">Adult Client names</label><div class="col-md-4" id="adults-client-container">\
            <input id="adult-signature-names" type="text" name="adult-clients" class="form-control input-md tags adult-signature-names"  data-role="tagsinput" required/>\
            </div></div>\
            <div class="form-group"><label class="col-md-6 control-label" for="child-clients">Child Client names</label><div class="col-md-4" id="adults-client-container">\
            <input id="child-signature-names" type="text" name="child-clients" class="form-control input-md tags child-signature-names"  data-role="tagsinput" required/>\
            </div></div><div class="form-group"> <label class="col-md-6 control-label" for="mileage-description">No. of miles travelled</label> <div class="col-md-4"> <input id="mileage-description" name="mileage-description" type="number" placeholder="0.0" min=0 class="form-control input-md" required=""> </div></div><div class="form-group"> <label class="col-md-6 control-label" for="out-of-pocket-expenses">Additional Expenses (if any)</label> <div class="col-md-4"> <div class="input-group"> <span class="input-group-addon">$</span> <input id="out-of-pocket-expenses" name="out-of-pocket-expenses" class="form-control" placeholder="0.00" value=0 min=0 type="number"> </div></div></div><div class="form-group"> <label class="col-md-6 control-label" for="signature-obtained-more-info">More Info</label> <div class="col-md-4"> <input id="signature-obtained-more-info" name="signature-obtained-more-info" type="text" placeholder="Required if additional expenses have beem incurred" class="form-control input-md"> </div></div></div><h6 style="color:red">*Client Names Spelling are Critical</h6>',
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
                    var adultClientNames = adultClients ?  adultClients.split(",") : []; 
                    var childClientNames = childClients ?  childClients.split(",") : []; 
                               
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
                        }  else {

                            if( Number.parseFloat(outOfPocketExpenses) >  0.0  &&  (!moreInfo || moreInfo == '')){
                                reject("More info is required if Out of pocket expenses were made");
                            }
                            
                            var adult_signatures_obtained = parseInt(noOfAdultSignaturesObtained);
                            var child_signatures_obtained = parseInt(noOfChildSignaturesObtained);
                            if( adult_signatures_obtained != adultClientNames.length){
                                reject("The Number of adult client names provided should be equal to no of adult signature obtained");
                            }

                            if( child_signatures_obtained != childClientNames.length){
                                reject("The Number of child client names provided should be equal to no of adult signature obtained");
                            }
                            resolve({
                                'Mileage Description': $('#mileage-description').val(),
                                'Out of pocket expenses': $('#out-of-pocket-expenses').val(),
                                'More Info': $('#signature-obtained-more-info').val(),
                                'no_of_adult_signatures_obtained':noOfAdultSignaturesObtained,
                                'no_of_child_signatures_obtained':noOfChildSignaturesObtained,
                                'adult_client_names':adultClients,
                                'child_client_names':childClients
                            });
                        }
                    } else {
                        reject('Please fill in No. of adult & child signatures obtained, No. of Miles travelled & Additional expenses');
                    }

                });
            }
        }).then(function (signature_details) {
            change_status_call(JSON.stringify(signature_details));
        }, function () {});
    }else {
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
            if(!value || value == ''){
                value = 'No additional Info provided'
            }
            change_status_call(JSON.stringify({'More info': value}));
        }, function () {});
    }


});

$('.details-tab').click(function () {
    'use strict';
    $('.tab-target').removeClass('show');
    $('.tab-target[data-target-value="' + $(this).attr('data-target') + '"]').addClass('show');
});

$('.extra-info-holder').click(function () {
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