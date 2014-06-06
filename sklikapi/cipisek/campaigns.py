from .entities import Campaign
from .baseclient import BaseClient

class CampaignsClient(BaseClient):
    """Sklik API ads namespace client."""

    def list_campaigns(self, include_deleted=False):
        filter = {
            'includeDeleted': bool(include_deleted),
        }
        result = self._call('campaigns.list', filter)
        return Campaign.marshall_list(result['campaigns'])

    def create_campaigns(self, campaigns):
        result = self._call('campaigns.create', list(campaigns))
        return result["campaignIds"]

    def get_campaigns(self, campaign_ids):
        result = self._call('campaigns.get', list(campaign_ids))
        return Campaign.marshall_list(result["campaigns"])

    def check_campaigns(self, campaigns):
        result = self._call('campaigns.check', list(campaigns))
        return True

    def update_campaigns(self, campaigns):
        campaigns = [dict(c.iterate_updatable()) for c in campaigns]
        result = self._call('campaigns.update', campaigns)
        return True

    def remove_campaigns(self, campaign_ids):
        self._call('campaigns.remove', list(campaign_ids))
        return True

    def restore_campaigns(self, campaign_ids):
        self._call('campaigns.restore', list(campaign_ids))
        return True
