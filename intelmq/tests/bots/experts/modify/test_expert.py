# -*- coding: utf-8 -*-
"""
Testing modify expert bot.
"""

import json
import unittest

from pkg_resources import resource_filename

import intelmq.lib.test as test
from intelmq.lib.utils import load_configuration
from intelmq.bots.experts.modify.expert import ModifyExpertBot

EVENT_TEMPL = {"__type": "Event",
               "feed.name": "Spamhaus Cert",
               "feed.url": "https://portal.spamhaus.org/cert/api.php?cert="
                           "<CERTNAME>&key=<APIKEY>",
               "classification.taxonomy": "malicious code",
               "classification.type": "infected-system",
               "time.observation": "2015-01-01T00:00:00+00:00",
               }
INPUT = [{'feed.name': 'Abuse.ch',
          'feed.url': 'https://feodotracker.abuse.ch/blocklist/?download=domainblocklist'},
         {'malware.name': 'foobar', 'feed.name': 'Other Feed'},
         {'source.port': 80, 'malware.name': 'zeus'},
         {'malware.name': 'xcodeghost'},
         {'malware.name': 'securityscorecard-someexample-value'},
         {'malware.name': 'anyvalue'},
         {'source.tor_node': True},
         {'source.tor_node': False},
         {},
         {'feed.accuracy': 5.22},
         {'feed.accuracy': 100},
         ]
OUTPUT = [{'classification.identifier': 'feodo'},
          {'classification.identifier': 'foobar'},
          {'protocol.transport': 'tcp', 'protocol.application': 'http',
           'classification.identifier': 'zeus'},
          {'classification.identifier': 'xcodeghost'},
          {'classification.identifier': 'someexample-value'},
          {'classification.identifier': 'anyvalue'},
          {'event_description.text': 'This is a TOR node.'},
          {'event_description.text': 'This is not a TOR node.'},
          {'event_description.text': 'We don\'t know if this is a TOR node.'},
          {'event_description.text': 'Accuracy is 10% or lower.'},
          {'event_description.text': 'Accuracy is the highest.'},
          ]
for index in range(len(INPUT)):
    copy1 = EVENT_TEMPL.copy()
    copy2 = EVENT_TEMPL.copy()
    copy1.update(INPUT[index])
    copy2.update(INPUT[index])
    copy2.update(OUTPUT[index])
    INPUT[index] = copy1
    OUTPUT[index] = copy2


class TestModifyExpertBot(test.BotTestCase, unittest.TestCase):
    """
    A TestCase for ModifyExpertBot.
    """

    @classmethod
    def set_bot(cls):
        cls.bot_reference = ModifyExpertBot
        config_path = resource_filename('intelmq',
                                        'bots/experts/modify/examples/default.conf')
        cls.sysconfig = {'configuration_path': config_path
                         }

    def test_events(self):
        """ Test if correct Events have been produced. """
        self.input_message = INPUT[:6]
        self.run_bot(iterations=6)

        for position, event_out in enumerate(OUTPUT[:6]):
            self.assertMessageEqual(position, event_out)

    def test_timing(self):
        """
        Test Timing.
        Call with:
        python3 intelmq/tests/bots/experts/modify/test_expert.py -q TestModifyExpertBot.test_timing
        """
        parameters = {'configuration_path': '/opt/intelmq/var/lib/bots/modify/malware_names.conf'}
        count = 10000
        self.prepare_bot(parameters=parameters)
        self.input_queue = [json.dumps({"__type": "Event", "malware.name": "this does not match anything :)"}) for i in range(count)]
        raise self.run_bot(prepare=False, timeit_number=count)


    def test_conversion(self):
        """ Test if the conversion from old dict-based config to new list based is correct. """
        old_path = resource_filename('intelmq',
                                     'tests/bots/experts/modify/old_format.conf')
        old_config = load_configuration(old_path)
        new_path = resource_filename('intelmq',
                                     'tests/bots/experts/modify/new_format.conf')
        new_config = load_configuration(new_path)
        self.assertDictEqual(modify_expert_convert_config(old_config)[0],
                             new_config[0])

    def test_types(self):
        """
        boolean etc
        """
        config_path = resource_filename('intelmq',
                                        'tests/bots/experts/modify/types.conf')
        parameters = {'configuration_path': config_path}
        self.input_message = INPUT[6:]
        self.prepare_bot(parameters=parameters)
        self.run_bot(prepare=False, iterations=len(INPUT[6:]))
        for position, event_out in enumerate(OUTPUT[6:]):
            self.assertMessageEqual(position, event_out)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
