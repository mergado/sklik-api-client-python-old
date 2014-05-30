from datetime import datetime

from sklikapi.cipisek.groups import GroupsClient
from sklikapi.cipisek.keywords import KeywordsClient
from sklikapi.cipisek.entities import Keyword, Group, Campaign
from sklikapi.cipisek.campaigns import CampaignsClient
from sklikapi.cipisek.exceptions import InvalidDataError
from sklikapi.cipisek.marshalling import marshall_param

from . import unittest
from . import only_with_login, get_client

class KeywordsTest(unittest.TestCase):

    keyword_name = 'test keyword'
    group_name = 'test keyword group' + str(datetime.now())
    campaign_name = 'test keyword campaign' + str(datetime.now())

    campaign = Campaign(
        name=campaign_name,
        dayBudget=10000,
        context=False,
        fulltext=True
    )

    group = Group(
        name=group_name,
        cpc=10000,
        cpcContext=10000
    )

    keyword = Keyword(
        name=keyword_name,
        matchType='phrase'
    )

    values = dict(
        name=keyword_name,
        matchType='phrase'
    )

    def test_construct(self):
        self.assertEqual(Keyword(self.keyword), self.keyword)

    def test_marshall(self):
        self.assertEqual(marshall_param(self.keyword), self.values)
        self.assertEqual(marshall_param([self.keyword]), [self.values])
        self.assertEqual(Keyword.marshall_list([self.values]), [self.keyword])

    @only_with_login
    def test_check(self):
        keyword = Keyword(
            name=self.keyword_name,
            cpc=1,
        )

        c = get_client(KeywordsClient)

        with self.assertRaisesRegexp(InvalidDataError, '406; ambiguous_check'):
            c.check_keywords([keyword])

    @only_with_login
    def test_create_get_delete_restore_delete(self):
        c = get_client(KeywordsClient)
        camp_c = get_client(CampaignsClient)
        grp_c = get_client(GroupsClient)

        # 0) prepare campaign and group
        campaign = Campaign(self.campaign)
        campaign.name += 'crud'
        campaign_id = camp_c.create_campaigns([campaign])[0]
        group = Group(self.group)
        group.campaignId = campaign_id
        group_id = grp_c.create_groups([group])[0]

        keyword = Keyword(self.keyword)
        keyword.groupId = group_id

        # 1) create
        ids = c.create_keywords([keyword])
        existing = len(c.list_keywords(groups=[group_id]))
        self.assertEqual(existing, 1)

        # 2) check equality
        from_api = c.get_keywords(ids)[0]
        for key, val in self.keyword:
            self.assertEqual(val, getattr(from_api, key))

        # 3) delete
        c.remove_keywords(ids)
        existing2 = len(c.list_keywords(groups=[group_id]))
        self.assertEqual(0, existing2)

        # 4) restore
        c.restore_keywords(ids)
        existing3 = len(c.list_keywords(groups=[group_id]))
        self.assertEqual(1, existing3)

        # 5) update
        keyword = Keyword(self.keyword)
        keyword.cpc = 10000
        keyword.id = ids[0]
        c.update_keywords([keyword])

        # 6) check equality
        from_api = c.get_keywords(ids)[0]
        for key, val in keyword:
            self.assertEqual(val, getattr(from_api, key))

        # 7) delete
        c.remove_keywords(ids)
        grp_c.remove_groups([group_id])
        camp_c.remove_campaigns([campaign_id])
