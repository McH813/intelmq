# -*- coding: utf-8 -*-
"""
Testing Mail URL collector
"""
import unittest.mock as mock
import unittest
import os

import intelmq.lib.test as test
from intelmq.bots.collectors.mail.collector_mail_url import MailURLCollectorBot
if os.getenv('INTELMQ_TEST_EXOTIC'):
    from .lib import MockedTxtImbox


REPORT_FOOBARTXT = {
                    '__type': 'Report',
                    'extra.email_from': 'wagner@cert.at',
                    'extra.email_message_id': '<07ce0153-060b-f48d-73d9-d92a20b3b3aa@cert.at>',
                    'extra.email_subject': 'foobar txt',
                    'feed.accuracy': 100.0,
                    'feed.name': 'IMAP Feed',
                    'extra.file_name': 'foobar.txt',
                    'feed.url': 'http://localhost/foobar.txt',
                    'raw': 'YmFyIHRleHQK',
                    }


@test.skip_exotic()
class TestMailURLCollectorBot(test.BotTestCase, unittest.TestCase):
    """
    Test MailURLCollectorBot
    """
    @classmethod
    def set_bot(cls):
        cls.bot_reference = MailURLCollectorBot
        cls.sysconfig = {'mail_host': None,
                         'mail_user': None,
                         'mail_password': None,
                         'mail_ssl': None,
                         'folder': None,
                         'subject_regex': None,
                         'url_regex': 'http://localhost/.*\.txt',
                         'name': 'IMAP Feed',
                         }

    def test_localhost(self):
        with mock.patch('imbox.Imbox', new=MockedTxtImbox):
            self.run_bot()
        self.assertMessageEqual(0, REPORT_FOOBARTXT)
