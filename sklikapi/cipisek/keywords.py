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
        result = {}
        chunks = [keywords[x:x+100] for x in xrange(0, len(keywords), 100)]
        for chunk in chunks:
            result.update(self._call('keywords.create', chunk))
        return result["positiveKeywordIds"] + result["negativeKeywordIds"]

    def get_keywords(self, keyword_ids):
        result = self._call('keywords.get', list(keyword_ids))
        return Keyword.marshall_list(result["keywords"])

    def check_keywords(self, keywords):
        return self._call('keywords.check', list(keywords))

    def update_keywords(self, keywords):
        keywords = [dict(kw.iterate_updatable()) for kw in keywords]
        return self._call('keywords.update', keywords)

    def remove_keywords(self, keyword_ids):
        return self._call('keywords.remove', list(keyword_ids))

    def restore_keywords(self, keyword_ids):
        return self._call('keywords.restore', list(keyword_ids))
