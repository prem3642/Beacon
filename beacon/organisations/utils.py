# -*- coding: utf-8 -*-

# Beacon stuff
from beacon.users.tasks import sync_users_active_status_with_organisation_task


def sync_child_org_active_status_with_parent_org(
    child_org,
    is_parent_org_active,
    deactivation_reason,
):
    """
    Method to sync child org's active status with the given parent org's active status. If this syncing changes active
    status of child org, then also trigger the celery task to sync active status of its users.

    :param child_org: Instance of organisation subjected to sync its active status
    :param is_parent_org_active: Designates the latest active status of the parent organisation
    :param deactivation_reason: Org's deactivation reason to consider for syncing
    """
    is_update_child_org = False
    new_deactivation_reason = None
    if not is_parent_org_active and child_org.is_active:
        is_update_child_org = True
        new_deactivation_reason = deactivation_reason
    elif (
        is_parent_org_active
        and not child_org.is_active
        and child_org.deactivation_reason == deactivation_reason
    ):
        is_update_child_org = True

    if is_update_child_org:
        child_org.is_active = is_parent_org_active
        child_org.deactivation_reason = new_deactivation_reason
        child_org.save()
        sync_users_active_status_with_organisation_task.delay(
            org_id=child_org.id,
            is_active=child_org.is_active,
        )
