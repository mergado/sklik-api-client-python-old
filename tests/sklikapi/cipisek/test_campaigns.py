from datetime import datetime

from sklikapi.cipisek.entities import Campaign, Keyword
from sklikapi.cipisek.campaigns import CampaignsClient
from sklikapi.cipisek.exceptions import InvalidDataError
from sklikapi.cipisek.marshalling import marshall_param

from . import unittest
from . import only_with_login, get_client

class CampaignsTest(unittest.TestCase):

    keyword = Keyword(name='some kw', matchType='negativeBroad')

    campaign_name = 'test campaign' + str(datetime.now())

    campaign = Campaign(
        name=campaign_name,
        dayBudget=10000,
        context=False,
        fulltext=True,
        negativeKeywords=[keyword]
    )

    values = dict(
        name=campaign_name,
        dayBudget=10000,
        context=False,
        fulltext=True,
        negativeKeywords=[dict(name='some kw', matchType='negativeBroad')]
    )

    def _get_client(self):
        return get_client(CampaignsClient)

    def test_construct(self):
        self.assertEqual(Keyword(self.keyword), self.keyword)
        self.assertEqual(Campaign(self.campaign), self.campaign)

    def test_marshall(self):
        self.assertEqual(marshall_param(self.campaign), self.values)
        self.assertEqual(marshall_param([self.campaign]), [self.values])
        self.assertEqual(Campaign.marshall_list([self.values]), [self.campaign])

    @only_with_login
    def test_check(self):
        campaign = Campaign(
            name=self.campaign_name,
            dayBudget=1,
        )

        c = get_client(CampaignsClient)

        with self.assertRaisesRegexp(InvalidDataError, '406; campaign_dayBudget_is_too_low'):
            c.check_campaigns([campaign])

    @only_with_login
    def test_create_get_delete_restore_delete(self):
        c = get_client(CampaignsClient)

        # 1) create
        ids = c.create_campaigns([self.campaign])

        # 2) check equality
        from_api = c.get_campaigns(ids)[0]
        for key, val in self.campaign:
            self.assertEqual(val, getattr(from_api, key))

        # 3) list
        existing = len(c.list_campaigns())
        self.assertGreaterEqual(existing, 1)

        # 4) delete
        c.remove_campaigns(ids)
        existing2 = len(c.list_campaigns())
        self.assertEqual(1, existing - existing2)

        # 5) restore
        c.restore_campaigns(ids)
        existing3 = len(c.list_campaigns())
        self.assertEqual(existing, existing3)

        # 6) update
        campaign = Campaign(self.campaign)
        campaign.dayBudget = 20000
        campaign.id = ids[0]
        c.update_campaigns([campaign])

        # 7) check equality
        from_api = c.get_campaigns(ids)[0]
        for key, val in campaign:
            self.assertEqual(val, getattr(from_api, key))

        # 8) delete
        c.remove_campaigns(ids)
