# Release Notes


## Cycle 32 (Apr 28, 2022 - May 11, 2022)

- Degrade Django to `3.2.11` as an immediate fix to restrict ASGI threads opening up multiple database connections. Django 4.x will be upgraded once we have pgbouncer integrated for connection pooling.

## Cycle 31 (Apr 14, 2022 - Apr 27, 2022) [v2.0.0]

*21st Apr, 2022*:

- Upgrade server `Ubuntu 16.04.4 LTS Xenial` to `Ubuntu 20.04.3 LTS focal`.
- Upgrade Django from 3.x to 4.x.
- Upgrade all dependencies to latest version and avoid any CVEs.

## Cycle 30 (Mar 31, 2022 - Apr 13, 2022) [v1.1.7]

*8th Apr, 2022*:

- [BEA-246](https://linear.app/beacon-health/issue/BEA-246/fts-not-working-on-stgprod-only)
  - Fix FullTextSearch for AWS RDS on staging and prod.

*6th Apr, 2022*:

- [BEA-242](https://linear.app/beacon-health/issue/BEA-242/cognito-errors-with-some-users-registered-by-scc-invalid-user-and-user)
    - For all new registrations through any system / FE of BWB site, we'll normalize emails and then sync up with all other systems. Normalization means lower-casing the domain part of the email.

*5th Apr, 2022*:

- Change `User.timezone` choices in DB to allow only currently acceptable timezones.

*4th Apr, 2022*:

- [BEA-245](https://linear.app/beacon-health/issue/BEA-245/update-users-timezone-on-mdlive-at-registration)
  - Sync user's timezone with MDLive during user registration.

*31st Mar, 2022*:

- [BEA-244](https://linear.app/beacon-health/issue/BEA-242/cognito-errors-with-some-users-registered-by-scc-invalid-user-and-user)
  - Make `gender` not required on Change User Admin form because the field is nullable for users getting registered via SCC. Provide default value "U" for cognito data because the field is required on Cognito.

- Update documentation to replace UWSGI with ASGI implementation.
- Fix nginx conf to have diff upstream for diff vhost.

## Cycle 29 (Mar 16, 2022 - Mar 30, 2022)

*29th Mar, 2022*:

- [BEA-243](https://linear.app/beacon-health/issue/BEA-243/change-the-char-limit-of-various-fields-in-the-db)
  - Change character limits of some fields in model `User` and `Organisation` to match character limits of these fields in SCC system.

*28th Mar, 2022*:

- Fix timezone set-up for new users on Django.

- [BEA-228](https://linear.app/beacon-health/issue/BEA-228/make-homepage-navs-searchable-by-client)
    - Add organisation column to HomepageNavs listing page on Django Admin.

- [BEA-172](https://linear.app/beacon-health/issue/BEA-172/add-timezone-to-register-endpoint-model)
    - Sync timezone to MDLive on user-registration.

*24th Mar, 2022*:

- Remove Mozilla SOPS integration completely from the repo. The ADR has been marked deprecated and kept for historical purposes.

*23rd Mar, 2022*:
  - Remove recently added 11 states from User Model as they are found to be unsupported with MDLive.
  - Add missing syncing with MDLive and Cognito in API (`POST /api/users/sync`).
  - Do not raise error if fields `firstName`, `lastName`, `gender`, `dateOfBirth` are received in SCC APIs request body. Instead, simply ignore them at serialization layer and move ahead.

  - [BEA-228](https://linear.app/beacon-health/issue/BEA-228/make-homepage-navs-searchable-by-client)
    - Make HomepageNavs searchable by organisations title, domain, and username on Django admin.

  - [BEA-236](https://linear.app/beacon-health/issue/BEA-236/show-additional-columns-on-django-scc-api-logs-results-page-add-filter)
    - Add more fields in SCC API Log list view on Django Admin. These fields are `connects_member_id`, `mdlive_id`, `parent_code`, `group_number`, and `benefit_package`.
    - Add filter by `status` in SCC API log.

  - [BEA-211](https://linear.app/beacon-health/issue/BEA-211/when-existing-user-is-changed-via-scc-update-show-changed-fields-in)
    - Enhance SCC API logs to store if the request is outgoing or incoming to BWB system, and also compute and store the changes done in BWB by incoming SCC requests.

*21st Mar, 2022*:

- [BEA-237](https://linear.app/beacon-health/issue/BEA-237/django-scc-api-log-request-and-response-text-not-readable-if-using)
  - Change color style of JSON rendering on Django Admin from `colorful` to `igor`, because `colorful` values were becoming invisible in dark modes.

- [BEA-240](https://linear.app/beacon-health/issue/BEA-240/add-location-to-response)
  - In API (`/api/organisations?search_term=`) also return `location` of the organisation.

- [BEA-232](https://linear.app/beacon-health/issue/BEA-232/filter-out-orgs-with-children)
  - In API (`/api/organisations?search_term=`), do not return parent organisations if they have child organisation.

## Cycle 28 (Mar 2, 2022 - Mar 16, 2022)

*10th Mar, 2022*:
  - Change cognito authentication failed error message to return "integer" for "num_of_failed_login_attempts".

*8th Mar, 2022*:

- [BEA-225](https://linear.app/beacon-health/issue/BEA-225/while-a-users-bw-account-is-deactivated-do-not-push-updates-to-mdlive)
  - Updates made to in-active users via Django Admin are not synced with MDLive (only synced with Cognito).

*7th Mar, 2022*:

- [BEA-223](https://linear.app/beacon-health/issue/BEA-223/[10258]-comparison-of-demographiccontact-fields-is-still-treated-as)
  - Add temp fix: return values in uppercase in the discrepancy error message, until SCC fixes value comparison on their side.

*4th Mar, 2022*:

- [BEA-212](https://linear.app/beacon-health/issue/BEA-212/mdlive-id-is-being-overwritten-with-null-value-by-scc-updates)
  - Add temp fix: ignore MDLive ID update in API (`/api/users/:id/force-sync`) if SCC sends `null` for field `mdLiveMemberID`, until SCC fixes their request body of force-sync API to include only those fields which are required to update.

*3rd Mar, 2022*:

- [BEA-212](https://linear.app/beacon-health/issue/BEA-212/mdlive-id-is-being-overwritten-with-null-value-by-scc-updates)
  - Add logger in SCC APIs, to display request body received from Service Care Connects system.

## Cycle 27 (Feb 17, 2022 - Mar 2, 2022)

*28th Feb, 2022*:

- [BEA-17](https://linear.app/beacon-health/issue/BEA-17/warn-users-about-account-lockout-due-to-incorrect-password-attempts)
  - Change error message format for login to include `num_of_failed_login_attempts`.

*25th Feb, 2022*:

- [BEA-177](https://linear.app/beacon-health/issue/BEA-177/edit-a-users-answers-from-bw-admin)
  - Allow admin to edit `appointment_status`, `chief_complaint1`, and `chief_complaint2` via user response admin detail-view.

- [BEA-194](https://linear.app/beacon-health/issue/BEA-194/error-address-line-2-cannot-be-empty)
  - Allow null for user field `address2` in serializers.
  - Save null in `address2` if no data provided for it while registering a new user on Django Admin.

- [BEA-207](https://linear.app/beacon-health/issue/BEA-224/[10258]-bw-users-registered-by-scc-are-not-able-to-see-provider)
  - SCC registrations in BW apply the same state to both users_user.state and answer.appointment_state

*22nd Feb, 2022*:

- [BEA-206](https://linear.app/beacon-health/issue/BEA-206/separate-auth-from-provider-availability-calls)
  - Segregate fake-user-token from search-providers/providers-profile API to overload MDLive servers with duplicate request and cause them to throw `Duplicate request error` with `425` HTTP status code.
    - `GET /api/mdlive/providers-profile` call now requires fake-user-token to be provided in `mdlive_token` mandatory query_param.
    - `POST /api/mdlive/search-providers?patient_id=642173385` call now requires fake-user-token to be provided in `mdlive_token` mandatory query_param and expects a mandatory `patient_id` query param of the fake user.

- [BEA-213](https://linear.app/beacon-health/issue/BEA-213/update-only-employment-status-relationship-status-and-job-title-in)
  - In SCC Sync API, if user matches, update only 3 personal info user fields `relationship_status`, `employment_status`, and `job_title`.

*21st Feb, 2022*:

- [BEA-192](https://linear.app/beacon-health/issue/BEA-192/display-users-login-attempt-information-under-user-agents)
- [BEA-193](https://linear.app/beacon-health/issue/BEA-193/add-user-agent-link-to-the-change-user-page)
    - Modify `users.User` and `users.UserAgent` admin to display dates and link user agent from User detail view page.

## Cycle 26 (Feb 2, 2022 - Feb 17, 2022)

*17th Feb, 2022*:

- Make `timezone` field optional and default to `UTC` in `users.serializers.UpdateUserProfileSerializer` which also affects the registration API (`POST /api/auth/register`).

*18th Feb, 2022*:

- Add 11 new states in the state choices for user to sync with SCC.
- Use case-insensitive match in user-search logic for match through SCC system `sync` API for `address1`, `address2`, `city`, `first_name`, `last_name` fields.

*15th Feb, 2022*:

- [BEA-208](https://linear.app/beacon-health/issue/BEA-208/org-matching-logic)
  - Organisation search logic tries to identify a single organisation with `parent_code`, then fallback on combination of `parent_code` and `group_number` and then further fallback on a combination of `parent_code`, `group_number` & `benefit_package` for SCC sync API(s).

- [BEA-199](https://linear.app/beacon-health/issue/BEA-199/scc-employment-status-data-not-provided-should-be-translated-to-blank)
  - Allow `relationship_status`, `employment_status`, `job_title` to be `null` in force-sync API

*14th Feb, 2022*:

- [BEA-205](https://linear.app/beacon-health/issue/BEA-205/[10268]-change-organisation-to-american-english-organization)
  - Fix spelling for SCC error to use American-English.

- [BEA-199](https://linear.app/beacon-health/issue/BEA-199/scc-employment-status-data-not-provided-should-be-translated-to-blank)
  - Add new option "Data Not Provided" in SCC employment status mapping.

- [BEA-204](https://linear.app/beacon-health/issue/BEA-204/vsd-10258-issue-with-non-numeric-values-for-outcome-questions)
  - Change SCC mapping for outcome questions. Non-numeric SCC values as answers of these questions are now converted to `None` instead of 0 (zero).

*10th Feb, 2022*:

- [BEA-202](https://linear.app/beacon-health/issue/BEA-202/vsd-10258-dt-340-unhelpful-error-message)
  - Fix answer validation error formatting
  - Pass `None` to `chief_complaint2` answer, if no option is selected for it while registering a new user from admin panel.
  - Add data migration to replace all previously filled `chief_complaint2` blank values with `None`s.

- [BEA-203](https://linear.app/beacon-health/issue/BEA-203/vsd-10258-dt-350-two-issues)
  - Fix gender mapping, if BWB has `None` for gender then send "U" to MDLive or SCC.

*9th Feb, 2022*:

- [BEA-200](https://linear.app/beacon-health/issue/BEA-200/scc-employment-status-disabilityworkers-coompensation-should-be)
  - Fixed typo in employment status choice "Disability/Worker’s Compensation".

- [BEA-197](https://linear.app/beacon-health/issue/BEA-197/[10255]-also-send-appointment-slot-queries-to-scc)
  - Send user data to SCC when API `POST /api/appointment-slot-queries` is called. This is the case when the user choose to "submit an appointment request" to MDLive rather than scheduling the slot.

- Catch Cognito exception for invalid passwords while registering users or changing their password on Cognito.
- If `scc.tasks.send_user_data_to_scc_task` fails while sending user data to SCC, then raise exception to mark the task as failed.

*4th Feb, 2022*:

- [BEA-195](https://linear.app/beacon-health/issue/BEA-195/[10258]-change-error-message)
  - In discrepancy message to SCC, replace "None" (string of None) to `null`.

## Cycle 25 (Jan 19, 2022 - Feb 2, 2022)

*28th Jan, 2022*:

- [BEA-187](https://linear.app/beacon-health/issue/BEA-187/exclude-inactive-orgs-from-search-and-dropdowns)
  - Exclude Inactive Organisations from search API (`/api/organisations?search_term=fueled`) and dropdown in user admin forms.

*27th Jan, 2022*:

- Make `organisations.Organisation.alternate_names` as optional field.
- Fix proxy call to MDLive `/api/mdlive/providers-profile` API.

*25th Jan, 2022*

- [BEA-188](https://linear.app/beacon-health/issue/BEA-188/[10258]-return-values-even-for-those-that-match)
  - In 10258 flow, if user is found with discrepancy in BWB, then return all (not just mismatched) fields related to conflict resolution to SCC.

*21st Jan, 2022*:

- Update decision records for bulk organisation-user deactivation flow, scc sync, django admin read only user view, and automated/manual deployment through Github Actions.

- [BEA-174](https://linear.app/beacon-health/issue/BEA-174/ability-to-display-custom-program-name-and-phone-in-welcome-emails)
  - Change the welcome-email template for new users to display custom program name and phone number.

*20th Jan, 2022*:

- [BEA-178](https://linear.app/beacon-health/issue/BEA-178/[10255]-manually-send-a-user-registration-from-bw-admin-to-connectsapi)
  - Add `SEND TO CONNECTS` button at user-detail view of admin.

- [BEA-176](https://linear.app/beacon-health/issue/BEA-176/ability-to-change-a-users-organisation-from-bw-admin)
  - Allow changing of `organisation` of user from Django admin with a warning help-text.

- [BEA-144](https://linear.app/beacon-health/issue/BEA-144/ability-to-deactivate-all-users-under-specific-org-in-django)
  - Auto deactivate/activate users if their organisation is set to inactive/active respectively from organisation-detail view of admin.
  - Add `deactivation_reason` field in user model.
  - Add `deactivation_reason` field in organisation model.

- [BEA-175](https://linear.app/beacon-health/issue/BEA-175/option-to-resend-a-users-welcome-email-from-bw-admin)
  - Remove `SEND TO CAMPAIGN MONITOR` button from user-detail view of admin.
  - Add `RESEND WELCOME EMAIL & RESET DEFAULT PASSWORD` button in user-detail view of admin for resetting to default password and re-sending welcome email.

## Cycle 24 (Jan 5, 2022 - Jan 19, 2022)

*18th Jan, 2022*:

- Improve FTS in organisation API to pre-compute search vector and index it using GIN.
- [BEA-168](https://linear.app/beacon-health/issue/BEA-168/expand-org-search-capabilities-be-component)
  - Add search in admin through `title`, `username`, `parent_code`, `group_number` and `benefit_package`

*17th Jan, 2022*:

- [BEA-136](https://linear.app/beacon-health/issue/BEA-136/add-org-search-functionality)
  - Add API for searching organisations `GET /api/organisations`.

*14th Jan, 2022*:

- [BEA-123](https://linear.app/beacon-health/issue/BEA-123/update-to-user-search-columns-in-django)
  - Modify user admin list display, remove modified_at, add parent code, group number, benefit package, and date joined.

*13th Jan, 2022*:

- [BEA-143](https://linear.app/beacon-health/issue/BEA-143/when-deactivating-a-user-account-in-django-active-flag-does-not-update)
  - Ignore MDLive exception if only is_active status of a user is changed via Admin panel.

- [BEA-116](https://linear.app/beacon-health/issue/BEA-116/identifycapture-users-time-zone-based-on-their-zip-code)
    - Add `timezone` field in user model and user registration API (`/api/auth/register`).

*11th Jan, 2022*:

  - [BEA-164](https://linear.app/beacon-health/issue/BEA-164/option-for-homepage-nav-links-to-open-in-a-new-browser-tab)
    - Add new boolean field in homepage navs to designate if links should open in a new browser tab.

*7th Jan, 2022*:

- Add Mozilla SOPS for secrets management
- Add SOPS to decrypt secrets via Github Actions.

## Cycle 23 (Dec 15, 2021 - Jan 5, 2022)

*4th Jan, 2022*:

- [BEA-154](https://linear.app/beacon-health/issue/BEA-154/new-field-for-navigation-item-descriptions)
  - Add an optional description field in homepage navs.

- [BEA-157](https://linear.app/beacon-health/issue/BEA-157/new-field-for-homepage-nav-order)
  - On Django Admin, make inline homepage navs in an organisation drag-and-drop sortable. And provide that sort order to frontend.

*17th Dec, 2021*:

- [BEA-150](https://linear.app/beacon-health/issue/BEA-150/change-celery-flower-dashboard-usernamepassword-configurable)
  - Fetch celeryflower dashboard's auth parameters (username/password) from .env at target machine's project director.

- [BEA-158](https://linear.app/beacon-health/issue/BEA-158/scc-instructed-email-updates-failing-when-attempting-to-update-on)
  - Add missing data before sending SCC updates to mdlive and cognito to avoid failures.

## Cycle 22 (Dec 1, 2021 - Dec 15, 2021)

*10th Dec, 2021*:

- [BEA-147](https://linear.app/beacon-health/issue/BEA-147/backup-user-response-json)
  - Backup user response JSON if changed while updating it with values coming from SCC system.

*7th Dec, 2021*:

- [BEA-134](https://linear.app/beacon-health/issue/BEA-134/be-tweaks-for-connects-compatability)
  - Override existing user answers if "null" value arrive from SCC for those answers.

- Pin dependency for django-sites to 0.11 which supports Django 3.x.

*2nd Dec, 2021*:

- [BEA-134](https://linear.app/beacon-health/issue/BEA-134/be-tweaks-for-connects-compatability)
  - Change SCC date of birth conversion and validation of CYYMMDD format. For year use C=1 for 1900, and C=2 for 2000.
  - Accept optional keys in 10258 requests having "null" as values.

## Cycle 21 (Nov 17, 2021 - Dec 1, 2021)

*30th Nov, 2021*:

- [BEA-133](https://linear.app/beacon-health/issue/BEA-133/[regression]-unable-to-sync-a-user)
  - Fix user match logic for syncing from SCC to BWB.

*26th Nov, 2021*:

- [BEA-102](https://linear.app/beacon-health/issue/BEA-102/refactor-and-improve-test-coverage-of-the-adapter-layer)
  - Validate incoming SCC data, refactor and add test cases for data conversion.

- [BEA-110](https://linear.app/beacon-health/issue/BEA-110/[10255]-when-a-user-self-registers-trigger-the-api-call-to-send-to)
  - When a user completes self registration and schedule a non-F2F appointment, trigger the API call in background to send data to SCC.

- [BEA-109](https://linear.app/beacon-health/issue/BEA-109/[10255]-send-new-non-f2f-self-registrations-to-connects)
  - Services to send new non-F2F self registration user data to SCC system.

- [BEA-108](https://linear.app/beacon-health/issue/BEA-108/[10255]-implement-auth-for-10255-sending-them-new-non-f2f-self)
  - Add method to generate auth tokens for making API calls to SCC system.

*24th Nov, 2021*:

- Add Github Actions.
- Remove Travis CI.
- [BEA-111](https://linear.app/beacon-health/issue/BEA-111/[10255]-dashboard-to-see-which-users-have-been-sent-to-connects-etc)
  - Add celery flower.

## Cycle 20 (Nov 3, 2021 - Nov 17, 2021)

*15th Nov, 2021*:

- [BEA-125](https://linear.app/beacon-health/issue/BEA-125/trigger-new-user-process-for-scc-imports)
  - Add a new user source choice option "scc" for new user registrations coming from SCC system.

- [BEA-126](https://linear.app/beacon-health/issue/BEA-126/update-patch-calls-to-put-calls-for-connects-compatibility)
  - Change HTTP request method of users force sync endpoint from PATCH to PUT for SCC compatibility.

*10th Nov, 2021*:

- [BEA-99](https://linear.app/beacon-health/issue/BEA-99/[10258]-user-sync-and-validation-endpoint)
  - Add user sync endpoint for SCC system [docs](api/scc.md#sync-user)

*3rd Nov, 2021*:

- [BEA-100](https://linear.app/beacon-health/issue/BEA-100/force-user-sync-endpoint)
  - Add force user sync endpoint for SCC system [docs](api/scc.md#force-sync-user)

- [BEA-98](https://linear.app/beacon-health/issue/BEA-98/format-conversionadapter-layer)
  - Add mappings and methods to handle data conversion between SecureCareConnect (SCC) and BeaconWellBeing (BWB).

## Cycle 20 (Oct 13, 2021 - Nov 3, 2021)

*2nd Nov, 2021*:

- [BEA-96](https://linear.app/beacon-health/issue/BEA-96/need-validation-on-urls-for-external-links)
  - Add validation for homepage nav urls to start with `/`, `#`, `http`, `https` for absolute & relative urls.

- [BEA-103](https://linear.app/beacon-health/issue/BEA-103/endpoint-stubs-for-connects-devs)
  - Add stubs for SCC user sync and force user sync API along with SCCAuth.

*29th Oct, 2021*:

- [BEA-97](https://linear.app/beacon-health/issue/BEA-97/implement-connects-auth)
    - Add `SCCAccess` permission.

*26th Oct, 2021*:

- [BEA-94](https://linear.app/beacon-health/issue/BEA-94/add-benefit-package-group-no-to-organisation)
    - Add `benefit_package` and `group_number` field in the organisation model.

## [0.1.0-dev]

__Date:__ [Under Developement](https://github.com/Fueled/beacon-backend/issues/1)

__Features__

- ...
- initial setup of project.

__Fixes__

- ...

[0.1.0-dev]: https://github.com/Fueled/beacon-backend/compare/v0.0.0...master
