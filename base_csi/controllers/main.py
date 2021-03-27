import ast
import zipfile
try:
    from BytesIO import BytesIO
except ImportError:
    from io import BytesIO

from odoo import http, api, fields
from odoo import SUPERUSER_ID
from odoo.http import content_disposition
from odoo.http import request
from odoo.addons.sign.controllers.main import Sign
from datetime import datetime


class ShipstationPortal(http.Controller):
    def _default_request_uid(self):
        return request.session.uid and request.session.uid or SUPERUSER_ID

    @http.route(
        "/shipstation/shipped", type="json", auth="public", csrf=False, cors="*"
    )
    def ship(self, req):
        env = api.Environment(request.cr, SUPERUSER_ID, request.context)
        url = str(req.jsonrequest.get("resource_url"))
        new_post = env["shipstation.postback"].create({"name": url})
        string = str(new_post.id)
        return string


class SignGFP(Sign):

    def get_document_qweb_context(self, id, token):
        res = super(SignGFP, self).get_document_qweb_context(id, token)
        sign_request = http.request.env['sign.request'].sudo().browse(id).exists()
        if sign_request:
            sr_values = http.request.env['sign.request.item.value'].sudo().search([('sign_request_id', '=', sign_request.id)])
            vals = {}
            comp_vals = {}
            first_name = False
            last_name = False
            for value in sr_values:
                if value.sign_item_id.contact_info_type == 'cont_name':
                    first_name = value.value
                elif value.sign_item_id.contact_info_type == 'last_name':
                    last_name = value.value
                elif value.sign_item_id.contact_info_type == 'cont_email':
                    vals['email'] = value.value
                elif value.sign_item_id.contact_info_type == 'busi_name':
                    comp_vals['name'] = value.value
            
            if 'email' in vals:
                name = first_name + ' ' + last_name
                vals['name'] = name

            PartnerObj = http.request.env['res.partner'].sudo()
            parent_id = False
            child_id = False
            if comp_vals:
                comp_vals['company_type'] = 'company'
                domain = [('name', '=', comp_vals['name'])]
                parent_ids = PartnerObj.search(domain)
                if parent_ids:
                    filtered_parent_ids = parent_ids.filtered(lambda x: x.company_type == 'company')
                    if filtered_parent_ids:
                        parent_id = filtered_parent_ids[0]
                    else:
                        parent_id = PartnerObj.create(comp_vals)
                else:
                    parent_id = PartnerObj.create(comp_vals)

            if vals and parent_id:
                vals['type'] = 'contact'
                domain = ['|', ('name', '=', vals['name']), ('email', '=', vals['email'])]
                child_ids = PartnerObj.search(domain)
                if child_ids:
                    filtered_child_ids = child_ids.filtered(lambda x: x.company_type == 'person')
                    if filtered_child_ids:
                        child_id = filtered_child_ids[0]
                    else:
                        child_id = PartnerObj.create(vals)
                else:
                    child_id = PartnerObj.create(vals)

            if parent_id and child_id:
                parent_id.write({
                    'child_ids': [(4, child_id.id)]
                    })
            if sign_request and sign_request.sale_id and child_id:
                sign_request.sale_id.sudo().partner_end_id = child_id.id
                if sign_request.sale_id.sudo().opportunity_id:
                    sign_request.sale_id.sudo().opportunity_id.sudo().end_user = child_id.id
        return res

    def validate_install_date_format(self, date_text):
        try:
            return datetime.strptime(date_text, '%m/%d/%Y')
        except ValueError:
            return False


class Binary(http.Controller):
    @http.route('/web/binary/download_document', type='http', auth="public")
    def download_document(self, tab_id, **kw):
        new_tab = ast.literal_eval(tab_id)
        attachment_ids = request.env['ir.attachment'].search([('id', 'in', new_tab)])
        file_dict = {}
        for attachment_id in attachment_ids:
            file_store = attachment_id.store_fname
            if file_store:
                file_name = attachment_id.name
                file_path = attachment_id._full_path(file_store)
                file_dict["%s:%s" % (file_store, file_name)] = dict(path=file_path, name=file_name)
        zip_filename = datetime.now()
        zip_filename = "%s.zip" % zip_filename
        bitIO = BytesIO()
        zip_file = zipfile.ZipFile(bitIO, "w", zipfile.ZIP_DEFLATED)
        for file_info in file_dict.values():
            zip_file.write(file_info["path"], file_info["name"])
        zip_file.close()
        return request.make_response(bitIO.getvalue(),
                                     headers=[('Content-Type', 'application/x-zip-compressed'),
                                              ('Content-Disposition', content_disposition(zip_filename))])
