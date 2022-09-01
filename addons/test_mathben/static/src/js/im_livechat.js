odoo.define('im_livechat.im_livechat', function (require) {
"use strict";

require('bus.BusService');
var core = require('web.core');
var session = require('web.session');
var Widget = require('web.Widget');
var QWeb = core.qweb;

var LivechatButton = Widget.extend({
    init: function (parent, serverURL, options) {
        this._super(parent);
        console.debug("mom");
    },
    willStart: function () {
        return this._loadQWebTemplate();
    },
    start: function () {
        console.debug("start the chat");
        // this.$el.text(this.options.button_text);

        this.call('bus_service', 'addChannel', "accorderie.notification.favorite");
        this.call('bus_service', 'startPolling');
        this.call('bus_service', 'onNotification', this, this._onNotification);
        return this._super();
    },
    /**
     * @private
     */
    _loadQWebTemplate: function () {
        console.warn("Mathben add dynamic template")
        // var xml_files = ['/mail/static/src/xml/abstract_thread_window.xml',
        //                  '/mail/static/src/xml/thread.xml',
        //                  '/im_livechat/static/src/xml/im_livechat.xml'];
        var xml_files = [];
        var defs = _.map(xml_files, function (tmpl) {
            return session.rpc('/web/proxy/load', { path: tmpl }).then(function (xml) {
                QWeb.add_template(xml);
            });
        });
        return $.when.apply($, defs);
    },
    /**
     * @private
     * @param {Array[]} notifications
     */
    _onNotification: function (notifications) {
        console.debug("check livechat");
        console.debug(notifications);
    },
});

return {
    LivechatButton: LivechatButton,
};

});
