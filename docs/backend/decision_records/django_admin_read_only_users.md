## Beacon | Django Admin read only view for users
###### Prepared for Internal
###### Prepared by Sanyam
###### Updated on 21 January 2022

### Problem

Beacon staff needs a way to see the information of users while at the same time prevent accidental modification of any information present on Django admin.

### Solution

Since there is no out-of-the-box solution present for this problem, we added a `Edit User` button on detail page of each user. The User view displayed on admin is actually for `beacon.users.models.ReadOnlyProxyUser` which provides a read-only view by default.

Once the `Edit User` button is clicked, the staff user will be redirected to the edit view for `beacon.users.models.User` to get a write-enabled detail view for the user.
