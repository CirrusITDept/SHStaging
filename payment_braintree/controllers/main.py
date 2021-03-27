# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################
import logging
import pprint
from datetime import datetime
import werkzeug

from odoo.tools.translate import _
from odoo import http
from odoo.http import request
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)

Error1 = _("Braintree Errors 1: Braintree Payment Gateway Currently not Configure for this Currency pls Connect Your Shop Provider !!!")
Error2 = _("Braintree Errors 2: Authentication Error: API keys are incorrect.")
Error3 = _("Braintree Errors 3: Authorization Error: not authorized to perform the attempted action.")
Error4 = _("Braintree Errors 4: Issue occure while generating clinet token, pls contact your shop provider.")
Error5 = _("Braintree Errors 5: Default 'Merchant Account ID' not found.")
Error6 = _("Braintree Errors 6: Transaction not Found.")
Error7 = _("Braintree Errors 7: Error occured while payment processing or Some required data missing.")
Error8 = _("Braintree Errors 8: Validation error occured. Please contact your administrator.")
Error9 = _("Braintree Errors 9: Payment has been recevied on braintree end but some error occured during processing the order.")
Error10 = _("Braintree Errors 10: Unknow Error occured. Unable to validate the Braintree payment.")
SuccessMsg = _("Payment Successfully recieved and submitted for settlement.")


class BraintreeController(http.Controller):

    @http.route('/payment/braintree/get_authorization', type='json', auth='public', csrf=False)
    def get_authorization_token(self, acquirer_id, merchant_account_id):
        acquirer = request.env['payment.acquirer'].browse(int(acquirer_id))
        return acquirer.sudo()._get_authorization_token(merchant_account_id)

    @http.route('/payment/braintree/check_availability', type='json', website=True, auth='public', csrf=False)
    def check_braintree_availability(self, acquirer_id, **kwargs):
        acquirer = request.env['payment.acquirer'].browse(int(acquirer_id))
        order = request.website.sale_get_order()
        return acquirer._process_merchant_account_id(order.pricelist_id.currency_id)

    def get_transaction_vals(self, form_vals, order=None):
        transaction_vals_dict = {}
        nonce_from_the_client = form_vals.get('payment_method_nonce')
        merchant_account_id = form_vals.get('merchant_account_id')
        if nonce_from_the_client and merchant_account_id:
            customer_obj = order.partner_id
            partner_billing_obj = order.partner_invoice_id
            partner_shipping_obj = order.partner_shipping_id
            transaction_vals_dict = {
                    "amount":  form_vals.get('amount'),
                    "order_id":  order.name,
                    "payment_method_nonce": nonce_from_the_client,
                    "merchant_account_id": merchant_account_id,
                    "options": {
                        "submit_for_settlement": True
                    },
                    "customer": {
                        "first_name": customer_obj.name,
                        "company": customer_obj.street,
                        "email": customer_obj.email,
                        "phone": customer_obj.phone,
                    },
                    "billing": {
                        "first_name": partner_billing_obj.name,
                        "company": partner_billing_obj.street,
                        "street_address": partner_billing_obj.street2,
                        "locality": partner_billing_obj.city,
                        "region": partner_billing_obj.state_id.name,
                        "postal_code": partner_billing_obj.zip,
                        "country_name": partner_billing_obj.country_id.name,
                        "country_code_alpha2": partner_billing_obj.country_id.code
                    },
                    "shipping": {
                        "first_name": partner_shipping_obj.name,
                        "street_address": partner_shipping_obj.street,
                        "locality": partner_shipping_obj.city,
                        "region": partner_shipping_obj.state_id.name,
                        "postal_code": partner_shipping_obj.zip,
                        "country_name": partner_shipping_obj.country_id.name,
                        "country_code_alpha2": partner_shipping_obj.country_id.code
                    }
                }
        return transaction_vals_dict

    def braintree_do_payment(self, **post):
        values = {'status': False}
        order = request.website.sale_get_order()
        paymentTransaction = request.env['payment.transaction']
        transaction = paymentTransaction.sudo().search([('reference', '=', post.get('reference'))])
        if not transaction:
            values['message'] = Error6
            return values

        transactionValues = self.get_transaction_vals(post, order)
        _logger.info('Braintree Api call with values %s', pprint.pformat(transactionValues))  # debug
        try:
            response = transaction.acquirer_id._create_braintree_transaction(transactionValues)
            if response['status']:
                response = response['response']
                if response.is_success:
                    values.update({
                        'status': response.is_success,
                        'reference': post.get('reference'),
                        'currency': response.transaction.currency_iso_code,
                        'amount': response.transaction.amount,
                        'acquirer_reference': response.transaction.id,
                        'partner_reference': response.transaction.customer.get('email'),
                        'tx_msg': SuccessMsg
                    })
                    _logger.info('Braintree form_feedback with values %s', pprint.pformat(values))  # debug
                    paymentTransaction.sudo().form_feedback(values, 'braintree')
                else:
                    message = "Payment Failed: %s" % " ".join(error.message for error in response.errors.deep_errors)
                    transaction.sudo()._set_transaction_error(message)
                    values['message'] = message
            else:
                values['message'] = response['message']
        except Exception as e:
            _logger.error("Braintree exception: %r", e)  # debug

            if values['status']:
                transaction.sudo().write({
                    'brt_txnid': values['acquirer_reference'],
                    'acquirer_reference':values['acquirer_reference'],
                    'state': 'error',
                    'date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    'state_message': Error9,
                })
                values['message'] = Error9
            elif not values['status']:
                transaction.sudo()._set_transaction_error(Error1)
                values['message'] = e or Error1
            else:
                values['message'] = Error10
                values.update({ 'status': False, 'redirect_brt': True, 'message': Error10 })
        return values

    @http.route('/payment/braintree', type='http', auth="public", website=True)
    def braintree_payment(self, **post):
        """ Braintree Payment Controller """
        _logger.info('Beginning Braintree with post data %s', pprint.pformat(post))  # debug
        result = self.braintree_do_payment(**post)
        if not result['status']:
            return request.render("payment_braintree.barintree_error", {'error_message': result['message']})
        return werkzeug.utils.redirect('/payment/process')
