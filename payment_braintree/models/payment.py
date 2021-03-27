# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################
import logging
from datetime import datetime

from ..models.braintree_connector import BraintreeConnector
from odoo import api, fields, models, tools, _
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.tools.float_utils import float_compare

_logger = logging.getLogger(__name__)


class BraintreeMerchantAccount(models.Model):
    _name = 'braintree.merchant.account'
    _description='Braintree Merchant Account'
    _rec_name='braintree_merchant_id'

    braintree_merchant_id = fields.Char(string="Merchant Account ID", required=True)
    braintree_merchant_currency = fields.Many2one('res.currency', string="Currency", required=True)
    braintree_merchant_validate = fields.Boolean(string="Is Valideted ?")
    currency_ref = fields.Many2one('payment.acquirer', string="ref key with table", invisible=True)

    _sql_constraints = [
        ('braintree_merchant_id_key', 'UNIQUE (braintree_merchant_id)',  'Merchant account id already present!')
    ]

    def merchant_id_validate(self):
        for rec in self:
            resp = rec.currency_ref._validate_merchant_account_id(
                currency=rec.braintree_merchant_currency,
                merchant_account_id=rec.braintree_merchant_id,
                debug=True
            )
            if not resp['status']:
                raise ValidationError(resp['message'])
            rec.braintree_merchant_validate = True

class AcquirerBraintree(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('braintree', 'Braintree')])
    brt_merchant_id = fields.Char('Merchant ID ', required_if_provider='braintree', groups='base.group_user')
    brt_public_key = fields.Char('Public Key', required_if_provider='braintree', groups='base.group_user')
    brt_private_key = fields.Char('Private Key', required_if_provider='braintree', groups='base.group_user')
    brt_merchant_account_id = fields.Char(string='Default Merchant Account ID', groups='base.group_user')
    enable_3d_secure = fields.Boolean(string="Enable 3D Secure", groups='base.group_user')
    brt_multicurrency = fields.Boolean(string="Multi-Currency Setup", groups='base.group_user')
    multicurrency_ids = fields.One2many('braintree.merchant.account', 'currency_ref', string="Merchant Account IDs")
    brt_tokenization_key = fields.Char(string='Tokenization Key ', groups='base.group_user')
    authorization_process = fields.Selection([('client_token', 'Client Token'),
                                              ('auth_token', 'Authorized token')
                                            ], string="Authorization Process", groups='base.group_user', default="client_token")
    brt_paypal_enabled = fields.Boolean(string="paypal Enabled", default=True)

    def braintree_form_generate_values(self, tx_values):
        self.ensure_one()
        tx_values['enable_3d_secure'] = self.enable_3d_secure if self.authorization_process=='client_token' else False
        tx_values['paypal_enabled'] = self.brt_paypal_enabled
        tx_values['amount'] = round(tx_values['amount'], 2)
        return tx_values

    def _get_authorization_token(self, merchant_account_id):
        self.ensure_one()
        if self.brt_tokenization_key and self.authorization_process == 'auth_token' and not self.enable_3d_secure:
            return {
                'status': True,
                'token': self.brt_tokenization_key
            }
        BraintreeConn = self._braintree_setup()
        return BraintreeConn._get_client_token(merchant_account_id)

    def _braintree_setup(self):
        self.ensure_one()
        BraintreeConn = BraintreeConnector(
            merchant_id=self.brt_merchant_id,
            public_key=self.brt_public_key,
            private_key=self.brt_private_key,
            environment='production' if self.state=='enabled' else 'sandbox'
        )
        return BraintreeConn

    def _get_merchant_account_id(self, currency):
        self.ensure_one()
        if not self.brt_multicurrency:
            return self.brt_merchant_account_id
        merchant_account = self.multicurrency_ids.filtered(lambda r: r.braintree_merchant_currency.name == currency and r.braintree_merchant_validate)
        if merchant_account:
            return merchant_account[0].braintree_merchant_id
        return False

    def _fetch_merchant_account_id(self, merchant_account_id):
        self.ensure_one()
        BraintreeConn = self.sudo()._braintree_setup()
        return BraintreeConn._fetch_merchant_account(merchant_account_id)

    def _validate_merchant_account_id(self, currency, merchant_account_id, debug=False):
        result = {
            'status': False,
            'message': _("Braintree payment gateway not configure for '%s (%s)'. Please connect your shop provider.") % (currency.name, currency.symbol)
        }
        self.ensure_one()
        if not merchant_account_id:
            return  result
        resp = self._fetch_merchant_account_id(merchant_account_id)
        if resp['status'] and resp['account_status'] == 'active' and resp['account_currency'] == currency.name:
            return {
                'status': True,
                'currency': currency.name,
                'merchant_account_id': merchant_account_id
            }
        if not resp['status']:
            return resp

        if debug:
            if resp['account_status'] != 'active':
                result['message'] = _('Merchant account id not in active state.')
            if resp['account_currency'] != currency.name:
                result['message'] = _('Currency not match with merchant account id.')
        return result

    def _process_merchant_account_id(self, currency):
        merchant_account_id = self.sudo()._get_merchant_account_id(currency.name)
        return self._validate_merchant_account_id(currency, merchant_account_id)

    def _create_braintree_transaction(self, values):
        BraintreeConn = self.sudo()._braintree_setup()
        return BraintreeConn._create_transaction(values)

    def braintree_get_form_action_url(self):
        self.ensure_one()
        return '/payment/braintree'


class TransactionBraintree(models.Model):
    _inherit = 'payment.transaction'

    brt_txnid = fields.Char('Transaction ID')
    brt_txcurrency = fields.Char('Transaction Currency')

    @api.model
    def _braintree_form_get_tx_from_data(self, data):
        reference, amount, currency, acquirer_reference = data.get('reference'), data.get('amount'), data.get('currency'), data.get('acquirer_reference')
        if not reference or not amount or not currency or not acquirer_reference:
            error_msg = 'Braintree: received data with missing reference (%s) or acquirer_reference (%s) or Amount (%s)' % (
                reference, acquirer_reference, amount)
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        tx = self.search([('reference', '=', reference)])
        if not tx or len(tx) > 1:
            error_msg = _('received data for reference %s') % (pprint.pformat(reference))
            if not tx:
                error_msg += _('; no order found')
            else:
                error_msg += _('; multiple order found')
            _logger.info(error_msg)
            raise ValidationError(error_msg)
        return tx

    def _braintree_form_get_invalid_parameters(self, data):
        invalid_parameters = []
        if float_compare(float(data.get('amount', '0.0')), self.amount, 2) != 0:
            invalid_parameters.append(('amount', data.get('amount'), '%.2f' % self.amount))
        if data.get('currency') != self.currency_id.name:
            invalid_parameters.append(('currency', data.get('currency'), self.currency_id.name))
        return invalid_parameters

    def _braintree_form_validate(self, data):
        status = data.get('status')
        res = {
            'brt_txnid': data.get('acquirer_reference'),
            'acquirer_reference': data.get('acquirer_reference'),
            'state_message': data.get('tx_msg'),
            'brt_txcurrency': data.get('currency'),
        }
        if status:
            _logger.info('Validated Braintree payment for tx %s: set as done' % (self.reference))
            self._set_transaction_done()
            return self.write(res)

