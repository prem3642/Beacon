## Beacon | Organisation Deactivation Flow
###### Prepared for Internal
###### Prepared by Sanyam
###### Updated on 21 January 2022

### Bulk user deactivation through Organisation Deactivation

If organisation is deactivated, all the users within the organisation are deactivated except those which were already deactivated.

Along with this, these new deactivated users have `User.deactivation_reason` set-up to `CLIENT_TERMINATED`. Whenever an organisation is again re-activated, only the users within the organisation that are inactive and deactivation_reason as `CLIENT_TERMINATED` will be reactivated.

If a parent organisation is deactivated, then all it's child organisations are deactivated causing a chain-effect to deactivate all the users. All the child organisation have the `Organisation.deactivation_reason` set to `PARENT_ORG_DEACTIVATED`. If any child of the parent organisation was already deactivated, it is not affected by this change at all.

When the parent organisation gets reactivated, then only the child organisations that were disabled with `Organisation.deactivation_reason` as `PARENT_ORG_DEACTIVATED` are reactivated. This is done to prevent accidental activation of a child-organisation which was previous disabled due to another reason.

When these users within organisations are made inactive, the status of `is_active` is synced with AWS Cognito. It is not synced to MDLive, as at time of this documentation MDLive doesn't support `is_active` flag.
