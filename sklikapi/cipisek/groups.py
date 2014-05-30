from .entities import Group
from .baseclient import BaseClient

class GroupsClient(BaseClient):
    """Sklik API groups namespace client."""

    def create_groups(self, groups):
        result = self._marshalled_call('groups.create', list(groups))
        return result["groupIds"]

    def get_groups(self, groupIds):
        result = self._marshalled_call('groups.get', list(groupIds))
        return Group.marshall_list(result["groups"])

    def check_groups(self, groups):
        result = self._marshalled_call('groups.check', list(groups))
        return True

    def update_groups(self, groups):
        result = self._marshalled_call('groups.update', list(groups))
        return True

    def remove_groups(self, groupIds):
        self._marshalled_call('groups.remove', list(groupIds))
        return True

    def restore_groups(self, groupIds):
        self._marshalled_call('groups.restore', list(groupIds))
        return True
