odoo.define('base_csi.ClientActionCsi', function(require) {
    var core = require('web.core');
    var BarcodeClientAction = require('stock_barcode.ClientAction');
    var _t = core._t;

    function isChildOf(locationParent, locationChild) {
        return _.str.startsWith(locationChild.parent_path, locationParent.parent_path);
    }
    BarcodeClientAction.include({
        _step_destination: function(barcode, linesActions) {
            var errorMessage;

            // Bypass the step if needed.
            if (this.mode === 'delivery' || this.actionParams.model === 'stock.inventory') {
                this._endBarcodeFlow();
                return this._step_source(barcode, linesActions);
            }

            var destinationLocation = this.locationsByBarcode[barcode];
            if (!this.scannedLines.length || this.mode === 'no_multi_locations') {
                if (this.groups.group_tracking_lot) {
                    errorMessage = _t("You are expected to scan one or more products or a package available at the picking's location");
                } else {
                    errorMessage = _t('You are expected to scan one or more products.');
                }
                return $.Deferred().reject(errorMessage);
            }
            var self = this;
            // FIXME: remove .uniq() once the code is adapted.
            _.each(_.uniq(this.scannedLines), function(idOrVirtualId) {
                var currentStateLine = _.find(self._getLines(self.currentState), function(line) {
                    return line.virtual_id &&
                        line.virtual_id.toString() === idOrVirtualId ||
                        line.id === idOrVirtualId;
                });
                if (currentStateLine.qty_done - currentStateLine.product_uom_qty >= 0) {
                    // Move the line.
                    currentStateLine.location_dest_id.id = destinationLocation.id;
                    currentStateLine.location_dest_id.display_name = destinationLocation.display_name;
                } else {
                    // Split the line.
                    var qty = currentStateLine.qty_done;
                    currentStateLine.qty_done -= qty;
                    var newLine = $.extend(true, {}, currentStateLine);
                    newLine.qty_done = qty;
                    newLine.location_dest_id.id = destinationLocation.id;
                    newLine.location_dest_id.display_name = destinationLocation.display_name;
                    newLine.product_uom_qty = 0;
                    var virtualId = self._getNewVirtualId();
                    newLine.virtual_id = virtualId;
                    delete newLine.id;
                    self._getLines(self.currentState).push(newLine);
                }
            });
            linesActions.push([this.linesWidget.clearLineHighlight, [undefined]]);
            linesActions.push([this.linesWidget.highlightLocation, [true]]);
            linesActions.push([this.linesWidget.highlightDestinationLocation, [true]]);
            this.scanned_location_dest = destinationLocation;
            return $.when({ linesActions: linesActions });
        },
        _onBarcodeScannedHandler: function(barcode) {
            var self = this;
            if (barcode == 'O-BTN.cancel') {
                return false;
            } else {
                this._super(barcode);
            }
        },
    });
});