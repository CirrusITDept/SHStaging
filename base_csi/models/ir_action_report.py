# -*- coding: utf-8 -*-
import os
import logging
import io
from PyPDF2 import PdfFileWriter, PdfFileReader
from odoo import models, tools, _, http
from odoo.tools import config
from odoo.sql_db import TestCursor
from collections import OrderedDict
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)


def merge_pdf(pdf_data):
    ''' Merge a collection of PDF documents in one
    :param list pdf_data: a list of PDF datastrings
    :return: a unique merged PDF datastring
    '''
    writer = PdfFileWriter()
    for document in pdf_data:
        reader = PdfFileReader(io.BytesIO(document.get('pdf_content')), strict=False)
        for page in range(0, reader.getNumPages()):
            pager = reader.getPage(page)
            if document.get('custom') == True:
                # Rotate And Display
                pager.rotateCounterClockwise(90)
                pager.scaleTo(width=float(612), height=float(792))
                # without Rotate then enable this
                # pager.scaleTo(width=float(792), height=float(612))
            writer.addPage(pager)
    _buffer = io.BytesIO()
    writer.write(_buffer)
    merged_pdf = _buffer.getvalue()
    _buffer.close()
    return merged_pdf


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def render_qweb_pdf(self, res_ids=None, data=None):
        if not data:
            data = {}
        data.setdefault('report_type', 'pdf')

        # In case of test environment without enough workers to perform calls to wkhtmltopdf,
        # fallback to render_html.
        if (tools.config['test_enable'] or tools.config['test_file']) and not self.env.context.get('force_report_rendering'):
            return self.render_qweb_html(res_ids, data=data)

        # As the assets are generated during the same transaction as the rendering of the
        # templates calling them, there is a scenario where the assets are unreachable: when
        # you make a request to read the assets while the transaction creating them is not done.
        # Indeed, when you make an asset request, the controller has to read the `ir.attachment`
        # table.
        # This scenario happens when you want to print a PDF report for the first time, as the
        # assets are not in cache and must be generated. To workaround this issue, we manually
        # commit the writes in the `ir.attachment` table. It is done thanks to a key in the context.
        context = dict(self.env.context)
        if not config['test_enable']:
            context['commit_assetsbundle'] = True

        # Disable the debug mode in the PDF rendering in order to not split the assets bundle
        # into separated files to load. This is done because of an issue in wkhtmltopdf
        # failing to load the CSS/Javascript resources in time.
        # Without this, the header/footer of the reports randomly disapear
        # because the resources files are not loaded in time.
        # https://github.com/wkhtmltopdf/wkhtmltopdf/issues/2083
        context['debug'] = False

        # The test cursor prevents the use of another environnment while the current
        # transaction is not finished, leading to a deadlock when the report requests
        # an asset bundle during the execution of test scenarios. In this case, return
        # the html version.
        if isinstance(self.env.cr, TestCursor):
            return self.with_context(context).render_qweb_html(res_ids, data=data)[0]

        save_in_attachment = OrderedDict()
        if res_ids:
            # Dispatch the records by ones having an attachment and ones requesting a call to
            # wkhtmltopdf.
            Model = self.env[self.model]
            record_ids = Model.browse(res_ids)
            wk_record_ids = Model
            if self.attachment:
                for record_id in record_ids:
                    attachment = self.retrieve_attachment(record_id)
                    if attachment:
                        save_in_attachment[record_id.id] = self._retrieve_stream_from_attachment(attachment)
                    if not self.attachment_use or not attachment:
                        wk_record_ids += record_id
            else:
                wk_record_ids = record_ids
            res_ids = wk_record_ids.ids

        # A call to wkhtmltopdf is mandatory in 2 cases:
        # - The report is not linked to a record.
        # - The report is not fully present in attachments.
        if save_in_attachment and not res_ids:
            _logger.info('The PDF report has been generated from attachments.')
            return self._post_pdf(save_in_attachment), 'pdf'

        if self.get_wkhtmltopdf_state() == 'install':
            # wkhtmltopdf is not installed
            # the call should be catched before (cf /report/check_wkhtmltopdf) but
            # if get_pdf is called manually (email template), the check could be
            # bypassed
            raise UserError(_("Unable to find Wkhtmltopdf on this system. The PDF can not be created."))

        html = self.with_context(context).render_qweb_html(res_ids, data=data)[0]

        # Ensure the current document is utf-8 encoded.
        html = html.decode('utf-8')

        bodies, html_ids, header, footer, specific_paperformat_args = self.with_context(context)._prepare_html(html)

        if self.attachment and set(res_ids) != set(html_ids):
            raise UserError(_("The report's template '%s' is wrong, please contact your administrator. \n\n"
                "Can not separate file to save as attachment because the report's template does not contains the attributes 'data-oe-model' and 'data-oe-id' on the div with 'article' classname.") %  self.name)

        pdf_content = self._run_wkhtmltopdf(
            bodies,
            header=header,
            footer=footer,
            landscape=context.get('landscape'),
            specific_paperformat_args=specific_paperformat_args,
            set_viewport_size=context.get('set_viewport_size'),
        )
        if res_ids:
            enable_so_technical_drawings = self.env['ir.config_parameter'].sudo().get_param('base_csi.enable_so_technical_drawings')
            _logger.info('The PDF report has been generated for model: %s, records %s.' % (self.model, str(res_ids)))
            rec_ids = res_ids if self.model == 'sale.order' and self.report_name == 'base_csi.csi_report_saleorder' and enable_so_technical_drawings else html_ids
            return self._post_pdf(save_in_attachment, pdf_content=pdf_content, res_ids=rec_ids), 'pdf'
        return pdf_content, 'pdf'

    def _post_pdf(self, save_in_attachment, pdf_content=None, res_ids=None):
        streams = []
        enable_so_technical_drawings = self.env['ir.config_parameter'].sudo().get_param('base_csi.enable_so_technical_drawings')
        result = super(IrActionsReport, self)._post_pdf(save_in_attachment, pdf_content=pdf_content, res_ids=res_ids)
        if self.model == 'sale.order' and self.report_name == 'base_csi.csi_report_saleorder' and enable_so_technical_drawings:
            streams.append({'pdf_content': result, 'custom': False})
            url = ''
            if res_ids:
                order_id = self.env['sale.order'].search([('id', 'in', res_ids)], limit=1)
                if order_id.height and order_id.width:
                    hw_string = str(order_id.height) + 'ft x ' + str(order_id.width) + 'ft'
                    pdfs_path = http.addons_manifest['base_csi']['addons_path'] + '/base_csi/static/pdfs/'
                    if os.path.isdir(pdfs_path):
                        for root, dirs, files in os.walk(pdfs_path):
                            for static_file in files:
                                if (static_file.find(hw_string) != -1):
                                    url = os.path.join(root, static_file)
            if url:
                with open(url, 'rb') as pdf_document:
                    pdf_contentmy = pdf_document.read()
                streams.append({'pdf_content': pdf_contentmy, 'custom': True})
                result = merge_pdf(streams)
        return result
