from datetime import datetime

from sklikapi.cipisek.groups import GroupsClient
from sklikapi.cipisek.entities import Group, Campaign
from sklikapi.cipisek.campaigns import CampaignsClient
from sklikapi.cipisek.exceptions import InvalidDataError
from sklikapi.cipisek.marshalling import marshall_param

from . import unittest
from . import only_with_login, get_client

class GroupsTest(unittest.TestCase):

    group_name = 'test group' + str(datetime.now())
    campaign_name = 'test group campaign' + str(datetime.now())

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

    values = dict(
        name=group_name,
        cpc=10000,
        cpcContext=10000
    )

    def test_construct(self):
        self.assertEqual(Group(self.group), self.group)

    def test_marshall(self):
        self.assertEqual(marshall_param(self.group), self.values)
        self.assertEqual(marshall_param([self.group]), [self.values])
        self.assertEqual(Group.marshall_list([self.values]), [self.group])

    @only_with_login
    def test_check(self):
        camp_c = get_client(CampaignsClient)
        campaign = Campaign(self.campaign)
        campaign.name += 'check'
        campaign_id = camp_c.create_campaigns([campaign])[0]

        try:
            group = Group(
                campaignId=campaign_id,
                name=self.group_name,
                cpc=1,
            )

            c = get_client(GroupsClient)

            with self.assertRaisesRegexp(InvalidDataError, '406; group_cpc_is_too_low'):
                c.check_groups([group])

        finally:
            camp_c.remove_campaigns([campaign_id])

    @only_with_login
    def test_create_get_delete_restore_delete(self):
        c = get_client(GroupsClient)
        camp_c = get_client(CampaignsClient)

        # 0) prepare campaign and group
        campaign = Campaign(self.campaign)
        campaign.name += 'crud'
        campaign_id = camp_c.create_campaigns([campaign])[0]
        group = Group(self.group)
        group.campaignId = campaign_id

        # 1) create
        ids = c.create_groups([group])
        existing = len(c.list_groups(campaigns=[campaign_id]))
        self.assertEqual(1, existing)

        # 2) check equality
        from_api = c.get_groups(ids)[0]
        for key, val in self.group:
            self.assertEqual(val, getattr(from_api, key))

        # 3) delete
        c.remove_groups(ids)
        existing2 = len(c.list_groups(campaigns=[campaign_id]))
        self.assertEqual(0, existing2)

        # 4) restore
        c.restore_groups(ids)
        existing3 = len(c.list_groups(campaigns=[campaign_id]))
        self.assertEqual(1, existing3)

        # 5) update
        group = Group(self.group)
        group.cpc = 20000
        group.id = ids[0]
        c.update_groups([group])

        # # 6) check equality
        from_api = c.get_groups(ids)[0]
        for key, val in group:
            self.assertEqual(val, getattr(from_api, key))

        # 7) delete
        c.remove_groups(ids)
        camp_c.remove_campaigns([campaign_id])
