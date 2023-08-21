# Character Fields with null=True

The issue came under notice, when FE intended to send "" (blank) to BWB in [BEA-194](https://linear.app/beacon-health/issue/BEA-194/error-address-line-2-cannot-be-empty)
When explored about the feasibility for allowing blank to `address2`, following results were concluded.

## Issue Description

Historically `address2` is not required, and the field is having `blank=False`, but `null=True` constrain at Database.
Currently, SCC also sends `null` to BWB when they don't have any data for this `address2`, so FE can also send `null`
to be consistent with SCC client.

Since, `address2` is an optional character field, keeping it `blank=False` and `null=True` together are not ideal constrains at the first place.
But right now it is like this only. Considering that BWB sends "" (blank) to MDLive or Cognito if no data exists for `address2`
in BWB system, therefore, changing constrains on this field such that to make it `null=False` and `blank=True` can
be a feasible solution.

But once this is implemented, both Beacon FE and SCC will need to make changes on their end as required. After which,
a complete regression test should be done to make sure it doesn't break anything.

## Interaction of field `address2` for no-data conditions across platforms

* Receiving `null` from SCC
* Receiving `null` from FE
* Saving `null` for new user registration via Django Admin
* Saving `null` in database while saving no data through change user form on Django Admin
* Sending `null` to SCC
* Sending blank to MDLive
* Sending blank to Cognito
* Sending blank to BWB Server

## Zooming out

That said about `address2` field. We see that this is not the only field like this. There are various other character
fields with `null=True` for example, in `User` model `first_name`, `last_name`, `phone`, `address1`, `city`, `zip`, etc.

If we aim to make this change for `address2`, we might want to fix those other fields too, and similarly the
changes will be required on Beacon FE and SCC. This entire solution should be done step by step by fixing each set of
fields and not everything in one release.

## Exceptions

There are lots of character fields with `null=True`, `blank=True` where these constrains make sense. For example, fields
in Model `UserResponse` and `UserAppointment` where in order to distinguish weather the answer given was "" (blank) or
weather the user didn't give any answer for that question (`null`).

## Solution Possibility and Implication

1. Making `address2` and other fields as `null=False`, `blank=True`. This would be the ideal state for a character field but will have the following implications.
    * SCC will need changes to send "" instead of `null` if they don't have any data for these user fields. This
        will make 10258 APIs sort of inconsistent. Why? Because currently SCC sends `null` for all fields if they don't have data for those fields.
        But after this change, they will have to send "" (blank) for one set of fields (belongs to model `User`) and `null` for
        another set of fields (belongs to model `UserResponse` and `Organisation`) in case they don't have any data.
    * Prior `null` data for these fields will get override to "" (blank), and reverting that change wouldn't be possible.

## Concluded Decision

Currently, it is best decided to not change constrains at the Database level, instead FE will send `null` for `address2`
(as consistent with SCC) to BE, and no change will be needed on SCC's side. The decision has been taken because, first
the solution required changes on FE and SCC both, and Erin Holmes (Beacon's Product Manager) informed us that:

    > we do need to avoid solutions that require a change to SCC's code where at all possible.
    > Any SCC code change would be a new "project" on their (SCC's) end, and would likely take months to get approved/in place.

Second, because the solution will make SCC's users sync and force sync APIs inconsistent.

Therefore, we are keeping `null=True`, `blank=False` as it is for the time being.
