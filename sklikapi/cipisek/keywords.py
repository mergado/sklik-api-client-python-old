from .entities import Keyword
from .baseclient import BaseClient

class KeywordsClient(BaseClient):
    """Sklik API keywords namespace client."""

    def create_keywords(self, keywords):
        result = self._marshalled_call('keywords.create', list(keywords))
        return result["positiveKeywordIds"] + result["negativeKeywordIds"]

    def get_keywords(self, keywordIds):
        result = self._marshalled_call('keywords.get', list(keywordIds))
        return Keyword.marshall_list(result["keywords"])

    def check_keywords(self, keywords):
        result = self._marshalled_call('keywords.check', list(keywords))
        return True

    def update_keywords(self, keywords):
        def to_dict(kw):
            kw = dict(kw)
            del kw['name']
            del kw['matchType']
            return kw
        result = self._marshalled_call('keywords.update', map(to_dict, keywords))
        return True

    def remove_keywords(self, keywordIds):
        self._marshalled_call('keywords.remove', list(keywordIds))
        return True

    def restore_keywords(self, keywordIds):
        self._marshalled_call('keywords.restore', list(keywordIds))
        return True
