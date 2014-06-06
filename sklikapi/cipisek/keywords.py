from .entities import Keyword
from .baseclient import BaseClient

class KeywordsClient(BaseClient):
    """Sklik API keywords namespace client."""

    def list_keywords(self, groups, limit=None, offset=None,
                      positive=True, negative=True, include_deleted=False):
        filter = {
            'groupIds': list(groups),
            'positiveKeywords': bool(positive),
            'negativeKeywords': bool(negative),
            'includeDeleted': bool(include_deleted),
        }
        if limit:
            filter['limit'] = int(limit)
        if offset:
            filter['offset'] = int(offset)
        result = self._call('keywords.list', filter)
        return Keyword.marshall_list(result['keywords'])

    def create_keywords(self, keywords):
        result = self._call('keywords.create', list(keywords))
        return result["positiveKeywordIds"] + result["negativeKeywordIds"]

    def get_keywords(self, keyword_ids):
        result = self._call('keywords.get', list(keyword_ids))
        return Keyword.marshall_list(result["keywords"])

    def check_keywords(self, keywords):
        self._call('keywords.check', list(keywords))
        return True

    def update_keywords(self, keywords):
        keywords = [dict(kw.iterate_updatable()) for kw in keywords]
        self._call('keywords.update', keywords)
        return True

    def remove_keywords(self, keyword_ids):
        self._call('keywords.remove', list(keyword_ids))
        return True

    def restore_keywords(self, keyword_ids):
        self._call('keywords.restore', list(keyword_ids))
        return True
