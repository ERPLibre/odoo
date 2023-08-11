# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models, tools


class MailCCMixin(models.AbstractModel):
    _name = 'mail.thread.cc'
    _inherit = 'mail.thread'
    _description = 'Email CC management'

    email_to = fields.Char('Email to', help='List of to from incoming emails.')
    email_cc = fields.Char('Email cc', help='List of cc from incoming emails.')

    def _mail_cc_sanitized_raw_dict(self, cc_string):
        '''return a dict of sanitize_email:raw_email from a string of cc'''
        if not cc_string:
            return {}
        return {tools.email_normalize(email): tools.formataddr((name, tools.email_normalize(email)))
            for (name, email) in tools.email_split_tuples(cc_string)}

    def get_list_ignore_mail(self):
        IRCP = self.env['ir.config_parameter'].sudo()
        domain = IRCP.get_param("mail.catchall.domain")
        lst_alias = [IRCP.get_param("mail.catchall.alias")]
        lst_alias += [a.alias_name for a in self.env["mail.alias"].search([]) if a.alias_name]
        lst_alias = list(set(lst_alias))
        lst_email_ignore = [f'{alias}@{domain}' for alias in lst_alias]
        return lst_email_ignore

    def filter_email_by_remove_ignore_mail(self, emails):
        if not emails:
            return emails
        lst_email_ignore = self.env[
            "mail.thread.cc"
        ].get_list_ignore_mail()
        lst_emails = [
            tools.formataddr((a, b))
            for a, b in tools.email_split_tuples(emails)
            if b not in lst_email_ignore
        ]
        return ", ".join(lst_emails)

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        if custom_values is None:
            custom_values = {}

        # Remove catchall email from TO
        lst_email_ignore = self.get_list_ignore_mail()
        lst_to = [tools.formataddr((a, b)) for a, b in tools.email_split_tuples(msg_dict.get('to')) if
                  b not in lst_email_ignore]
        to = ", ".join(lst_to)
        lst_cc = [tools.formataddr((a, b)) for a, b in tools.email_split_tuples(msg_dict.get('cc')) if
                  b not in lst_email_ignore]
        cc = ", ".join(lst_cc)
        cc_values = {
            'email_cc': cc,
            'email_to': to,
        }
        cc_values.update(custom_values)
        return super(MailCCMixin, self).message_new(msg_dict, cc_values)

    def message_update(self, msg_dict, update_vals=None):
        '''Adds cc email to self.email_cc while trying to keep email as raw as possible but unique'''
        if update_vals is None:
            update_vals = {}
        cc_values = {}
        new_cc = self._mail_cc_sanitized_raw_dict(msg_dict.get('cc'))
        if new_cc:
            old_cc = self._mail_cc_sanitized_raw_dict(self.email_cc)
            new_cc.update(old_cc)
            cc_values['email_cc'] = ", ".join(new_cc.values())
        cc_values.update(update_vals)
        return super(MailCCMixin, self).message_update(msg_dict, cc_values)

    def _message_get_suggested_recipients(self):
        recipients = super(MailCCMixin, self)._message_get_suggested_recipients()
        lst_ignore_mail = self.get_list_ignore_mail()
        for record in self:
            if record.email_cc:
                for email in tools.email_split_and_format(record.email_cc):
                    if tools.email_normalize(email) not in lst_ignore_mail:
                        record._message_add_suggested_recipient(recipients, email=email, reason=_('CC Email'))
            if record.email_to:
                for email in tools.email_split_and_format(record.email_to):
                    if tools.email_normalize(email) not in lst_ignore_mail:
                        record._message_add_suggested_recipient(recipients, email=email, reason=_('TO Email'))
        return recipients
