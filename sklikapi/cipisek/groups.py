from .entities import Group
from .baseclient import BaseClient


class GroupsClient(BaseClient):
    """Sklik API groups namespace client."""

    def list_groups(self, campaigns=None, include_deleted=False):
        filter = {
            'campaignIds': list(campaigns or []),
            'includeDeleted': bool(include_deleted),
        }
        result = self._call('groups.list', filter)
        return Group.marshall_list(result['groups'])

    def create_groups(self, groups):
        result = self._call('groups.create', list(groups))
        return result["groupIds"]

    def get_groups(self, group_ids):
        result = self._call('groups.get', list(group_ids))
        return Group.marshall_list(result["groups"])

    def check_groups(self, groups):
        self._call('groups.check', list(groups))
        return True

    def update_groups(self, groups):
        groups = [dict(g.iterate_updatable()) for g in groups]
        self._call('groups.update', groups)
        return True

    def remove_groups(self, group_ids):
        self._call('groups.remove', list(group_ids))
        return True

    def restore_groups(self, group_ids):
        self._call('groups.restore', list(group_ids))
        return True
