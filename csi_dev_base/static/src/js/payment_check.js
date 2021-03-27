odoo.define('csi_dev_base.payment_check', function (require) {
"use strict";

var core = require('web.core');
var Dialog = require('web.Dialog');
var publicWidget = require('web.public.widget');
var paymentform = require('payment.payment_form');
var rpc = require('web.rpc');

var _t = core._t;

$( document ).ready(function() {
    var o_portal_sidebar = $('#quote_content').find('.custom_pay_now')
    var o_sale_portal_paynow = $('#o_sale_portal_paynow')

    $(o_portal_sidebar).click(function(){
        var radio_button = $(".o_payment_acquirer_select input[name='pm_id']");
        var radios_filter = radio_button.filter(":checked");
        var default_checked = radios_filter.attr('data-provider');
        if(default_checked == 'transfer'){
            $('.form_wire_trasfer').show()
            $('#payment_error').hide()
        }else{
            $('.form_wire_trasfer').hide()
        }
    })
    $(o_sale_portal_paynow).click(function(){
        var radio_button = $(".o_payment_acquirer_select input[name='pm_id']");
        var radios_filter = radio_button.filter(":checked");
        var default_checked = radios_filter.attr('data-provider');
        if(default_checked == 'transfer'){
            $('.form_wire_trasfer').show()
            $('#payment_error').hide()
        }else{
            $('.form_wire_trasfer').hide()
        }
    })
    $('.o_payment_acquirer_select').click(function(){
        var select_div = $(this).find('input')
        var input_att_data = select_div.attr('data-provider')
        if(input_att_data ==  'transfer'){
            $('.form_wire_trasfer').show()
            $('#payment_error').hide()

        }else{
            $('.form_wire_trasfer').hide()
            // $('.validation').hide()
        }
    });  
    // $(radio_button).on('change', function(){
    //     var input_value = $(this).attr('data-provider')
    //     if(input_value == 'transfer'){
    //         $('.form_wire_trasfer').show()
    //     }else{
    //         $('.form_wire_trasfer').hide()
    //         $('.validation').hide()
    //     }
    // });
});

paymentform.include({
    payEvent: function (ev) {
        ev.preventDefault();
        var self = this;
        if (ev.type === 'submit') {
            var button = $(ev.target).find('*[type="submit"]')[0]
        } else {
            var button = ev.target;
        }
        var checked_radio = this.$('input[type="radio"]:checked');
        if (checked_radio.length === 1) {
            checked_radio = checked_radio[0];
            var acquirer_id = this.getAcquirerIdFromRadio(checked_radio);
            var acquirer_form = false;
            if (this.isNewPaymentRadio(checked_radio)) {
                acquirer_form = this.$('#o_payment_add_token_acq_' + acquirer_id);
            } else {
                acquirer_form = this.$('#o_payment_form_acq_' + acquirer_id);
            }
            if (this.isNewPaymentRadio(checked_radio)) {
                
            }else if (this.isFormPaymentRadio(checked_radio)) {
            	var cust_bank_name = $("[name='cust_bank_name']").val()
                var cust_acc_number = $("[name='cust_acc_number']").val()
                var cust_rout_number = $("[name='cust_rout_number']").val()
                var cust_acc_holder = $("[name='cust_acc_holder']").val()
                var radios = $(".o_payment_acquirer_select input[name='pm_id']");
                var radios_filter = radios.filter(":checked");
                var wire_trasfer = radios_filter.attr('data-provider');
                if(wire_trasfer == 'transfer'){
                    if(cust_bank_name.toString() && cust_acc_number.toString() && cust_rout_number.toString()  && cust_acc_holder.toString()){
                        var split_transaction = self.$el[0].action.split('/transaction')
                        var split_order = split_transaction[0].split('my/orders/')[1]
                        var os_id = split_order
                        $('.validation').hide()
//                        this.disableButton(button);
                        var $tx_url = this.$el.find('input[name="prepare_tx_url"]');
                        // if there's a prepare tx url set
                        if ($tx_url.length === 1) {
                            // if the user wants to save his credit card info
                            var form_save_token = acquirer_form.find('input[name="o_payment_form_save_token"]').prop('checked');
                            // then we call the route to prepare the transaction
                            var res = rpc.query({
                                model: 'sale.order',
                                method: 'get_sale_order',
                                args: [os_id,cust_bank_name,cust_acc_number,cust_rout_number,cust_acc_holder]
                            }).then(function (data) {
                                console.log(data);
                            });
                        }
                    }else{
                        var input_1 = $(".o_payment_acquirer_select input[type=radio]");
                        var i
                        for (i = 0; i < input_1.length; i++) {
                            if($(input_1[i]).attr("data-provider") == 'transfer'){
                                var input_wire_trasfer = input_1[i]
                                $(input_wire_trasfer).parent().addClass('wire_trasfer_label')
                                // if($('.validation').length == 0){
                                    self.displayError(
                                        // _t('Server Error'),
                                        _t("Fill up all below ACH mandatory data fields!.")
                                    );
                                    // $('.wire_trasfer_label').after('<div class="validation" style="color:red;text-align: center;font-size:18px">Fill up all below ACH mandatory data fields! </div>')
                                // }
                                // else{
                                //     $('.validation').replaceWith('<div style=" color:red;text-align: center;font-size:18px" class="validation">Fill up all below ACH mandatory data fields! </div>')
                                // }
                            }
                        }
                        return;
                    }
                }
            }else{
            	
            }
        }
        this._super.apply(this, arguments);
    },
})



})