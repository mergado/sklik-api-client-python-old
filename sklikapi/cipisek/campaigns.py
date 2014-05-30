from .entities import Campaign
from .baseclient import BaseClient

class CampaignsClient(BaseClient):
    """Sklik API ads namespace client."""

    def list_campaigns(self, include_deleted=False):
        filter = {
            'includeDeleted': bool(include_deleted),
        }
        result = self._marshalled_call('campaigns.list', filter)
        return Campaign.marshall_list(result['campaigns'])

    def create_campaigns(self, campaigns):
        result = self._marshalled_call('campaigns.create', list(campaigns))
        return result["campaignIds"]

    def get_campaigns(self, campaignIds):
        result = self._marshalled_call('campaigns.get', list(campaignIds))
        return Campaign.marshall_list(result["campaigns"])

    def check_campaigns(self, campaigns):
        result = self._marshalled_call('campaigns.check', list(campaigns))
        return True

    def update_campaigns(self, campaigns):
        result = self._marshalled_call('campaigns.update', list(campaigns))
        return True

    def remove_campaigns(self, campaignIds):
        self._marshalled_call('campaigns.remove', list(campaignIds))
        return True

    def restore_campaigns(self, campaignIds):
        self._marshalled_call('campaigns.restore', list(campaignIds))
        return True
