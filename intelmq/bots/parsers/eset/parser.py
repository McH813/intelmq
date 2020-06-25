import json
from intelmq.lib.utils import base64_encode, base64_decode

message_taxonomy_map = {
  'Host actively distributes high-severity threat in the form of executable code.': 'malware',
  'Host is known to be distributing low-risk and potentially unwanted content.': 'malware',
  'Host is known source of phishing or other fraudulent content.': 'phishing',
  'Host is known to be actively distributing adware or other medium-risk software.': 'other',
  'Host is known source of active fraudulent content.': 'other'
}

from intelmq.lib.bot import ParserBot

class ESETParserBot(ParserBot):
  def init(self):
    self.f_map = {
      'ei.urls (json)': self.urls_parse,
      'ei.domains v2 (json)': self.domains_parse
    }

  def parse(self, report): # yield single sections for parse_line to parse
    data = json.loads(base64_decode(report['raw']))
    for section in data:
      yield section

  def parse_line(self, line, report): # parse a section of the received report
    event = self.new_event(report)
    feed_name = line['_eset_feed']

    self.common_parse(event, line)
    self.f_map[feed_name](event, line)

    yield event


  @staticmethod
  def _get_taxonomy(reason):
    tax = message_taxonomy_map.get(reason, None)
    if tax: # was found in dictionary
      return tax
    elif reason.startswith('Host is used as command and control server'): # dynamic section after that
      return 'c2server'
    else:
      return 'other'

  @staticmethod
  def domains_parse(event, line):
    event.add('time.source', line['last_seen'])


  @staticmethod
  def urls_parse(event, line):
    event.add('time.source', line['domain_last_seen'])
    event.add('source.url', line['url'])


  @staticmethod
  def common_parse(event, line):
    type = self._get_taxonomy(line['reason'])
    feed_name = line['_eset_feed']

    event.add('raw', base64_encode(json.dumps(line)))
    event.add('event_description.text', line['reason'])
    event.add('classification.type', type)
    if not line['ip'] in [line['domain'], None]:
      event.add('source.fqdn', line['domain']) # IP addresses are not permitted in FQDN, only domain names

    event.add('source.ip', line['ip'])
    event.add('feed.name', f'ESET Threat Intelligence Service ({feed_name})')
    event.add('feed.provider', 'ESET')
    event.add('feed.url', 'https://eti.eset.com/taxiiservice/discovery')
    event.add('feed.documentation', 'https://www.eset.com/int/business/services/threat-intelligence/')


BOT = ESETParserBot
