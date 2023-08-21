## Beacon | BWB and SCC user data syncing
###### Prepared for Internal
###### Prepared by Sanyam
###### Updated on 21 January 2022

### VSD-10255 | BWB => SCC

The syncing in this flow is from BWB system to SCC system.

There are two kinds of syncing:

- Automated:
  - Whenever a new user is regsitered on BWB with non-F2F (non face-to-face) appointment.
- Manual:
  - The manual button on Users' detail page on Django admin enables manual syncing to SCC.

In both the cases, celery task queue handles the syncing which can be checked via flower dashboard hosted on `/flower/` URL.

Along with this, we also store the request body sent to SCC as well as the response retrieved from SCC to `beacon.scc.models.SccApiLog`

### VSD-10258 | SCC => BWB

The syncing in this flow is from SCC system to BWB system.

The logic for user matching on BWB side is mentioned in the [API documentation itself](../../api/scc.md). We are not replicating it here to follow DRY-approach.

One important caveat on BWB side is of backup response JSON field.

BWB now saves the older response JSON to `beacon.answers.models.UserResponse.response_backup` field. This field keeps track of all the older values of response JSON. Because SCC can update
the existing users answers to `null` using 10258 APIs, if this creates any unforeseeable issue in
future, we can use the responses backup to get the working data back.

This also helps in tracking the changes in user response.
