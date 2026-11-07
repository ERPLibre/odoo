# Part of Odoo. See LICENSE file for full copyright and licensing details.

import lxml.html

from odoo.tests import HttpCase, tagged


@tagged('post_install', '-at_install')
class TestCookiesBarConsent(HttpCase):
    """ The consent cookie, as the website's JavaScript writes it, controls
    the third-party iframes the server renders. """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        website = cls.env['website'].browse(1)
        website.write({'cookies_bar': True, 'block_third_party_domains': True})
        cls.env['website.page'].create({
            'name': 'Cookies bar video',
            'type': 'qweb',
            'arch': '''<t t-call="website.layout">
                <div id="wrap"><iframe id="video"
                    src="https://www.youtube-nocookie.com/embed/test"/></div>
            </t>''',
            'key': 'test_website.cookies_bar_video',
            'url': '/cookies-bar-video',
            'website_id': website.id,
            'is_published': True,
        })

    def _iframe_src(self, consent):
        """ Source of the video iframe, for a visitor sending ``consent`` as
        the raw value of the consent cookie (None: no cookie). """
        headers = {'Cookie': f'website_cookies_bar={consent}'} if consent else {}
        response = self.url_open('/cookies-bar-video', headers=headers, allow_redirects=False)
        self.assertEqual(response.status_code, 200)
        [iframe] = lxml.html.fromstring(response.content).xpath('//iframe[@id="video"]')
        return iframe.get('src')

    def test_consent_as_written_by_the_website(self):
        # Bare JSON with spaces and double quotes, as cookie.set() writes it:
        # not a valid cookie token, which strict cookie parsers drop.
        accepted = self._iframe_src('{"required": true, "optional": true}')
        self.assertEqual(accepted, 'https://www.youtube-nocookie.com/embed/test')
        refused = self._iframe_src('{"required": true, "optional": false}')
        self.assertEqual(refused, 'about:blank')
        self.assertEqual(self._iframe_src(None), 'about:blank')

    def test_consent_not_json(self):
        self.assertEqual(self._iframe_src('not-json'), 'about:blank')
