from .entities import Ad
from .baseclient import BaseClient

class AdsClient(BaseClient):
    """Sklik API ads namespace client."""

    def list_ads(self, campaigns=None, groups=None, include_deleted=False):
        filter = {
            'includeDeleted': bool(include_deleted),
        }
        display = {}
        if campaigns and groups:
            raise Exception('Cannot filter both by campaigns and groups')
        elif campaigns:
            filter['campaignIds'] = list(campaigns)
            display['showCampaignId'] = True
        elif groups:
            filter['groupIds'] = list(groups)
        result = self._marshalled_call('ads.list', filter, display)
        return Ad.marshall_list(result['ads'])

    def create_ads(self, ads):
        result = self._marshalled_call('ads.create', list(ads))
        return result["adIds"]

    def get_ads(self, adIds):
        result = self._marshalled_call('ads.get', list(adIds))
        return Ad.marshall_list(result["ads"])

    def check_ads(self, ads):
        result = self._marshalled_call('ads.check', list(ads))
        return True

    def update_ads(self, ads):
        result = self._marshalled_call('ads.update', list(ads))
        return result.get('newAdIds', [])

    def remove_ads(self, adIds):
        self._marshalled_call('ads.remove', list(adIds))
        return True

    def restore_ads(self, adIds):
        self._marshalled_call('ads.restore', list(adIds))
        return True
