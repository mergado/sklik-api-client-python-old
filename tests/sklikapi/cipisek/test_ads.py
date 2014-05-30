import unittest
from datetime import datetime

from sklikapi.cipisek.ads import AdsClient
from sklikapi.cipisek.groups import GroupsClient
from sklikapi.cipisek.entities import Ad, Group, Campaign
from sklikapi.cipisek.campaigns import CampaignsClient
from sklikapi.cipisek.exceptions import InvalidDataError
from sklikapi.cipisek.marshalling import marshall_param

from . import only_with_login, get_client

class AdsTest(unittest.TestCase):

    creative1 = 'test ad'
    creative2 = 'first line'
    creative3 = 'second line'
    url_display = 'http://example.com/'
    url_link = 'http://example.com/?utm_source=sklik'

    group_name = 'test ad group' + str(datetime.now())
    campaign_name = 'test ad campaign' + str(datetime.now())

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

    ad = Ad(
        creative1=creative1,
        creative2=creative2,
        creative3=creative3,
        clickthruText=url_display,
        clickthruUrl=url_link,
    )

    values = dict(
        creative1=creative1,
        creative2=creative2,
        creative3=creative3,
        clickthruText=url_display,
        clickthruUrl=url_link,
    )

    def _get_client(self):
        return get_client(AdsClient)

    def test_construct(self):
        self.assertEqual(Ad(self.ad), self.ad)

    def test_marshall(self):
        self.assertEqual(marshall_param(self.ad), self.values)
        self.assertEqual(marshall_param([self.ad]), [self.values])
        self.assertEqual(Ad.marshall_list([self.values]), [self.ad])

    @only_with_login
    def test_check(self):
        ad = Ad(
            creative1=self.creative1,
            creative2=self.creative2,
            creative3=self.creative3,
            clickthruText=self.url_display,
            clickthruUrl='bad url',
        )

        c = get_client(AdsClient)

        with self.assertRaisesRegexp(InvalidDataError, '406; bad_url'):
            c.check_ads([ad])

    @only_with_login
    def test_create_get_delete_restore_delete(self):
        c = get_client(AdsClient)
        camp_c = get_client(CampaignsClient)
        grp_c = get_client(GroupsClient)

        # 0) prepare campaign and group
        campaign = Campaign(self.campaign)
        campaign.name += 'crud'
        campaign_id = camp_c.create_campaigns([campaign])[0]
        group = Group(self.group)
        group.campaignId = campaign_id
        group_id = grp_c.create_groups([group])[0]

        ad = Ad(self.ad)
        ad.groupId = group_id

        # 1) create
        ids = c.create_ads([ad])

        # 2) check equality
        from_api = c.get_ads(ids)[0]
        for key, val in self.ad:
            self.assertEqual(val, getattr(from_api, key))

        # 3) delete
        c.remove_ads(ids)

        # 4) restore
        c.restore_ads(ids)

        # 5) update
        ad = Ad(self.ad)
        ad.clickthruUrl += '&utm_cosi=nic'
        ad.id = ids[0]
        new_ids = c.update_ads([ad])
        self.assertEqual([], new_ids)

        # 6) check equality
        from_api = c.get_ads(ids)[0]
        for key, val in ad:
            self.assertEqual(val, getattr(from_api, key))

        # 7) create new one via update
        ad = Ad(self.ad)
        ad.creative3 += 'cosi'
        ad.id = ids[0]
        new_ids = c.update_ads([ad])
        self.assertEqual(1, len(new_ids))

        # 8) check equality
        ad.id = new_ids[0]
        from_api = c.get_ads(new_ids)[0]
        for key, val in ad:
            self.assertEqual(val, getattr(from_api, key))

        # 9) delete
        c.remove_ads(ids)
        grp_c.remove_groups([group_id])
        camp_c.remove_campaigns([campaign_id])
