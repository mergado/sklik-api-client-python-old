from .ads import AdsClient
from .groups import GroupsClient
from .keywords import KeywordsClient
from .campaigns import CampaignsClient
from .baseclient import BaseClient

class Client(AdsClient, GroupsClient, KeywordsClient, CampaignsClient,
             BaseClient):
    """Sklik API client class."""
    pass
