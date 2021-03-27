odoo.define('base_csi.PDFIframe', function (require) {
    'use strict';

    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var Widget = require('web.Widget');
    var PDFIframe = require('sign.PDFIframe');
    var _t = core._t;

    PDFIframe.include({
    	doPDFPostLoad: function() {
    		var self = this;
    		this._super();
    		var $cssLink2 = $("<link/>", {
                rel: "stylesheet", type: "text/css",
                href: "/base_csi/static/src/css/iframe.css"
            });
            this.$('head')[0].appendChild($cssLink2[0]);
            
    	}
    });

    return PDFIframe;
});