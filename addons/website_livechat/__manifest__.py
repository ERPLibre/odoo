# -*- coding: utf-8 -*-
{
    'name': 'Website Live Chat',
    'category': 'Technical Settings',
    'summary': 'Chat with your website visitors',
    'version': '1.0',
    'description': """
Allow website visitors to chat with the collaborators. This module also brings a feedback tool for the livechat and web pages to display your channel with its ratings on the website.
    """,
    'depends': ['website', 'im_livechat'],
    'installable': True,
    'application': True,
    'auto_install': True,
    'data': [
        'views/website_livechat.xml',
    ],
}
