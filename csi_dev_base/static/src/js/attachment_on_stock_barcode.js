odoo.define('csi_dev_base.attachment_on_stock_barcode', function (require) {
"use strict";
	var core = require('web.core');
	var Widget = require('web.Widget');
	var QWeb = core.qweb;
	var stock_barcode = require('stock_barcode.LinesWidget');
	var utils = require('web.utils');
	var qweb = core.qweb;
	var _t = core._t;
	var _lt = core._lt;
	var rpc = require('web.rpc');
	
	stock_barcode.include({
		events: _.extend({}, stock_barcode.prototype.events, {
			'click .o_add_attachment': '_onClickoAddAttachment',
			'change .o_input_file': '_on_file_change',
	    }),
	    
	    _on_file_change: function (e) {
	        var self = this;
	        this.max_upload_size = 25 * 1024 * 1024;
	        var file_node = e.target;
	        if (file_node.files.length || $(file_node).val() !== '') {
                _.each(file_node.files, function (file) {
	                utils.getDataURLFromFile(file).then(function (data) {
	                    data = data.split(',')[1];
	                    self.on_file_uploaded(file.size, file.name, file.type, data);
	                });
                });
	        }
	    },
	    
	    on_file_uploaded: function (size, name) {
	        if (size === false) {
	            this.do_warn(_t("File Upload"), _t("There was a problem while uploading your file"));
	            console.warn("Error while uploading file : ", name);
	        } else {
	            this.on_file_uploaded_and_valid.apply(this, arguments);
	        }
	    },
	    
	    on_file_uploaded_and_valid: function (size, name, content_type, file_base64) {
	    	var self = this;
	    	if(this.__parentedParent && this.__parentedParent.currentState && this.__parentedParent.currentState.id){
	    		rpc.query({
	                args: [,this.__parentedParent.currentState.id,name,file_base64,content_type],
	                model: 'ir.attachment',
	                method: 'create_stock_barcode_attachment',
	            }).then(function(data){
	            	var msg = _t("File(s) successfully uploaded on document : %s.");
	            	self.do_warn(_t("File upload"), _.str.sprintf(msg,self.__parentedParent.title));
	            });
	    	}
	    },
	    
	    _onClickoAddAttachment: function (ev) {
	    	ev.preventDefault();
	    	ev.stopPropagation();
	    	var input_vals = this.$('input.o_input_file').click();
	    },
	    
	});


	
});