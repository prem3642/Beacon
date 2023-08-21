<style>
    .container h1{font-size: 1.5em; }
    .container h2{font-size: 1.2em; }
    .container hr{margin-top: 5px; }
</style>

Changelog is deprecated. Please refer to [release notes](../release_notes.md).

## 8 Apr, 2021

- Fix registration flow through API, when `user_appointment` is not available.

## 7 Apr, 2021

- Add `Architecture Decision Records` document at `docs/backend/architecture_decision_records.md`.

## 1 Apr, 2021

- On account re-registration, if MDLive returns the same ID, we'll revert back the info of existing user from our DB.

## 30 Mar, 2021

- Update docs related to services on the server, inspection of logs, etc for Beacon Infra team.

## 26 Mar, 2021

- Make `address2` not required in user edit form on Django admin.

## 25 Mar, 2021

- Add update appointment state API for current user API (`POST /api/me/update-appointment-state`).
- Replace `is_sent_to_campaign_monitor` flag from user admin list view and add `connects_mbr_id`. Add search functionality for `connects_mbr_id`.
- Update site title on all admin/API pages.

## 23 Mar, 2021

- Handle errors from Cognito while resending verification and updating the user profile through admin.

## 22 Mar, 2021

- Remove unique constraint check from `parent_code` attribute in `organisation`.
- Sync data to Cognito and MDLive synchronously.

## 17 Mar, 2021

- Update admin update user profile service to verify user email on Cognito as well.
- Add email verification check on confirm sign up api call (will be removed later).

## 15 Mar, 2021

- `GET /api/me` endpoint returns the `organisation` id the user belongs to.
- Raise error on user registration through admin if MDLive returns an ID that already exists in the system.

## 12 Mar, 2021

- Add filter on user admin to filter user by organisation's parent_code.
- Add `glyph_weight`, `glyph_height` in organisation and expose in `GET /api/organisations/configuration` API.
- Add `domain` attribute in `GET /api/organisations/configuration` API.
- Raise error for attempt to send verification code for disabled account.
- Ensure initial revision of the user is created on user creation.
- Mark user as not verified in Django when email is changed.
- Revert zip validation in user registration to be of max 5 chars.

## 11 Mar, 2021

- Fix issue with syncing changes in `is_active` and `email` together to Cognito.

## 10 Mar, 2021

- Remove congito account if mdlive throws error during registration in API (`POST /api/auth/register`) and the admin registration flow (`users/register`).

## 9 Mar, 2021

- Update validation on `zip` field in `POST /api/auth/register` call to support 5-10 characters.

## 8 Mar, 2021

- Add `glyph` field in the organisation related APIs (`GET /api/organisations/configuration`).

## 5 Mar, 2021

- Enable and disable user on Cognito on updating user's `is_active` status from Django admin.
- Add `session_frequency` in organsation and expose in related APIs (`* /api/organisations`).
- Add `is_no_of_sessions_hidden` attribute in organisations related APIs (`* /api/organisations`).

## 4 Mar, 2021

- Make `Add New Staff User` link on admin visible to only superuser.
- Add `source_admin` field to track the email of the admin who added a particular user.

## 3 Mar, 2021

- Reset `num_of_failed_login_attempts` to 0 on successful password reset to allow immediate login with new password.
- Ensure that `email` and `is_active` are correctly updated on Cognito.

## 2 Mar, 2021

- Add button to admin for adding staff user in `Call Centre Staff` group.
- Add `min_length` and `max_length` validation in `text` type questions.
- Increase the length of `f2f_zip` to be of 10 chars.
- Rename `old_load_initial_questions_f2f` management command to `old_load_initial_questions_f2f` as `load_initial_tempates` would superseed it.
- Modify the management commands `old_load_initial_questions_f2f` and `load_initial_tempates` to have Regex based f2f_zip question along with max length of 10 chars.

## 1 Mar, 2021

- Fix issue in `PATCH /api/answers/:id/add-or-update-answer` API for handling zip from 5 to 10 chars.
- Handle `LimitExceededException` in `POST /api/auth/resend-verification-email` API.
- Fix issue with celery defaulting to amqp instead of redis.
- Fix copy for registration email.

## 26 Feb, 2021

- Update copy for registration email.
- Label updates in User registration form and couple of other minor edits.

## 25 Feb, 2021

- Add `Call Center Staff` group with view only permission and permission to create new account via management command.
- Handle NotAuthorized error on password reset API (`POST /api/auth/password-reset`) when account is disabled on AWS Cognito.
- Hide the default edit view of user behind an edit view.
- Allow only superuser permission for editing a user using admin.
- Sync updates to mdlive and cognito on saving user.

## 24 Feb, 2021

- Add `introduction` carousel text for organisations.

## 20 Feb, 2021

- Add `connects_mbr_id` field to user model for Beacon's internal id.
- Disable TLS 1.0 and 1.1 support and use only TLS 1.2 in NGINX.
- Tweak "Register New User" form by removing default selection from field, make a few fields required, and change the order of the fields.

## 19 Mar, 2020

- Add filters to for `sent` and `received` messages

## 16 Mar, 2020

- Add `show_disclaimer` flag in organisation models and api

## 10 Mar, 2020

- Add dependent fields in sending f2f data to beacon server flow

## 09 Mar, 2020

- Send new message email when message received from webhook from MDLive ([BWB-968](https://fueled.atlassian.net/browse/BWB-968))

## 06 Mar, 2020

- Add organisation question type handling ([BWB-953](https://fueled.atlassian.net/browse/BWB-953))
- Use organisation answered in intake question if not specified in user registration ([BWB-953](https://fueled.atlassian.net/browse/BWB-953))

## 05 Mar, 2020

- Create templates for questions ([BWB-953](https://fueled.atlassian.net/browse/BWB-953))
- Add mapping for questions flow per template ([BWB-953](https://fueled.atlassian.net/browse/BWB-953))
- Add next/previous question api ([BWB-953](https://fueled.atlassian.net/browse/BWB-953))
- Fix bug in user login if registered with child organisation ([BWB-972](https://fueled.atlassian.net/browse/BWB-972))

## 03 Mar, 2020

- Update documents api to use `mdlive_id` as `id`

## 25 Feb, 2020

- Fix bug in messages datetime mismatch with MDLive ([BWB-949](https://fueled.atlassian.net/browse/BWB-949))
- Hide `safety screen url` from admin ([BWB-956](https://fueled.atlassian.net/browse/BWB-956))
- Update help text of organisation username to warn user to not change it
- Hide `parent` field in admin

## 19 Feb, 2020

- Fix `location` required for root organisation bug
- Add organisation `parent_code` and `location` in bwb data
- Fix child organisation with same parent code validation bug

## 17 Feb, 2020

- add `reply_allowed` flag in messaging apis

## 14 Feb, 2020

- Update django version to fix sql injection vulnerability
- Add `show_safety_screen` flag in organisation and questionnaire to show it for specific organisations
- Remove Amtrek policy question and per organisation question flow as it is de-prioritized

## 10 Feb, 2020

- Update homepage nav subcategories to use organisation `parent_code` as username in urls

## 07 Feb, 2020

- Create `OrganisationNextQuestion` for per organisation question flow mapping ([BWB-885](https://fueled.atlassian.net/browse/BWB-885))
- Add Amtrek policy question ([BWB-885](https://fueled.atlassian.net/browse/BWB-885))
- Add organisation username in all fake user requests instead of default one
- Update CSV import mapping ([BWB-897](https://fueled.atlassian.net/browse/BWB-897))

## 04 Feb, 2020

- Update copy of invalid password account lockout copy ([BWB-868](https://fueled.atlassian.net/browse/BWB-868))

## 31 Jan, 2020

- Add `categories`, `subcategories` apis & models for Homepage Nav ([BWB-869](https://fueled.atlassian.net/browse/BWB-869))
- Remove `allow_search` flag as we added categories, subcategories options

## 28 Jan, 2020

- Add `allow_search` flag in Organisation Homepage Nav ([BWB-869](https://fueled.atlassian.net/browse/BWB-869))
- Increase `max_length` to 30 in user-agent models

## 23 Jan, 2020

- Rename `appointment-request` to `appointment-slot-query` in api, models and serializers
- Add source field in user model to indicate from where it got registered
- Remove message, user message, provider message from admin view
- Add `mdlive_provider_type` in base configuration and return with organisation configuration api

## 22 Jan, 2020

- Update message api to include documents
- Update mdlive message service to include document details in message if they are attached
- Make `parent_code` required for root organisation
- Make location required for child organisations

## 21 Jan, 2020

- Update appointment request apis according to changed MDLive api response
- Update user documents apis to not store files

## 20 Jan, 2020

- Add mdlive appointment requests apis
- Add documents api
- Add admin view to retry

## 18 Jan, 2020

- Fix upload csv parent org data bug

## 13 Jan, 2020

- Update pwd validation error copy
- Move existing password validation to field validation
- Update base templates
- Update jwt token decode to remove deprecation warning

## 10 Jan, 2020

- Add password validations, account lockout after 4 failed attempts
- Raise invalid user error if email does not exists on login & password reset
- Update `user does not exists` error copy

## 07 Jan, 2020

- Use parent org parent_code in user csv export & add message link in UserMessage

## 06 Jan, 2020

- Filter out user sent messages from unread message count api
- Use parent-organisation's parent code in organisation model string method
- Revert Alcohol question redirect back to cut down drinking

## 03 Jan, 2020

- Add child organisation in api
- Allow null parent code for child organisations


## 19 Dec, 2019

- Update contacts api url
- Add messages and contacts detail api
- Increase max length for browser and os as it was conflicting on mobile
- Fix typo in user messages serializer

## 18 Dec, 2019

- Fix datetime parsing bug in user csv upload
- Integrate user agent for user to store last device used info
- Update pillow, versatileimagefield, django and request log id

## 17 Dec, 2019

- Add mdlive services tests
- Update Alcohol question redirect and change csv upload column name to Email
- Change csv upload `EMAIL1/EMAIL2` to `EMAIL`

## 13 Dec, 2019

- Add tests for messages apis
- Add lowercase char validation in password

## 12 Dec, 2019

- Fix bug with None address2 when we send it to MDLive
- Integrate webhook and parse its data on celery

## 09 Dec, 2019

- Mock celery sync user message task in all users tests
- Add emergency & global homepage nav configuration in model and api

## 06 Dec, 2019

- Integrate mdlive messaging apis

## 05 Dec, 2019

- Fix bug in error parsing of new mapped attribute in csv upload

## 26 Nov, 2019

- Add checkbox in csv upload to create users or send data campaign monitor
- Add `parent_code` in string method of organisation and update ordering

## 26 Nov, 2019

- Update csv upload attribute mapping to match beacon's care connect

## 25 Nov, 2019

- Resolve frontend url according to an organisation for welcome email
- Remove logo from welcome email template

## 22 Nov, 2019

- Add action in admin to send multiple appointments data to bwb server
- Add id in searching on django admin

## 21 Nov, 2019

- Refactor cognito services code
- Add cognito unit tests
- Fix organisation bug
- Update cognito test service to get user email, password as input
- Replace cognito get profile data call with user local data
- Update zip-code intake question to be `text` type instead of `regex`

## 19 Nov, 2019

- Add additional fields in export user csv function
- Add parent code in organisation configuration api

## 15 Nov, 2019

- Upgrade libraries and refactor code
- Handle not authorized error in cognito on password change

## 13 Nov, 2019

- Add regex question type to validate specific fields like zip-code
- Refactor upload users csv to just send data to campaign monitor
- Skip user creation locally and on cognito

## 08 Nov, 2019

- Add request type in user response & include it in import/export & Campaign Monitor
- Add `modified_at` in user and send organisation data to campaign monitor
- Add validation for character length in number field
- Make zip code number type in address question
- Add `request_type` in admin and make campaign monitor flag read only
- Update request type order in admin

## 07 Nov, 2019

- Update names of campaign monitor custom fields to match beacon internal names
- Update upload users csv to handle some edge cases
  - parse all null fields
  - if email is null raise error
  - if parent code is null create user and raise error as well
  - skip all users having same email and raise error
- Update csv upload service to skip user with parent code null
- Add row number in error message is email is null for a user in csv upload

## 06 Nov, 2019

- Add export user data as CSV functionality

## 05 Nov, 2019

- Remove `F` func in user csv upload as its increasing count by extra 1
- Add button in user detail page in admin to send data to campaign monitor
- Add action to send multiple users data to campaign monitor

## 01 Nov, 2019

- Copy update in "how often worry" question
- Send uploaded user csv data to campaign monitor

## 30 Oct, 2019

- Add parent code in org & update user csv upload for intake questions

## 25 Oct, 2019

- Add support to upload users csv

## 15 Oct, 2019

- Add api to update user responses for currently logged in user

## 14 Oct, 2019

- Make address2 in f2f questions as optional

## 11 Oct, 2019

- Reverse the order of address questions in F2F flow
- Support sub-organisation structure
- Fix getting list of server admins from environment variable

## 10 Oct, 2019

- Add retry logic for sending f2f data, email and resend button in admin

## 04 Oct, 2019

- Add api for fetching the latest appointment
- Add show message flag in latest appointment api

## 03 Oct, 2019

- Store all cognito data on locally and script for existing users
- Add delay of 1sec and exception handling for user not found in cognito data fetch management command
- Fix typo in cognito get admin data service

## 01 Oct, 2019

- Update f2f email subject copy

## 30 Sep, 2019

- Update f2f appointment email template copy
- Fix trans block typo in templates

## 27 Sep, 2019

- Copy change for voice-mail question
- Fix email template typo
- Add `TextBox` as new question type and set it up for counselor notes question

## 26 Sep, 2019

- Add `show_international_section` flag in organisation and fix decoding bug
- Remove logo from f2f email and update copy of subject and body

## 25 Sep, 2019

- Upgrade Ansible, Django and drf

## 24 Sep, 2019

- Add subheading in Question model
- Hide comfortable language question
- Rename preferred time agreement question to leave voice mail question
- Update service to send data to bwb server to send json type header
- Add api to finalize appointment for returning user
- Add inquiry id in f2f email and update appointment api fields

## 23 Sep, 2019

- Copy edits for questions
- Add dynamic homepage nav models and api

## 20 Sep, 2019

- Fix appointment api bug

## 19 Sep, 2019

- Send email about f2f appointment and update preferred time f2f question
- Add api to create new appointment
- Make f2f_counselor_notes question optional

## 18 Sep, 2019

- Send user data to bwb server on registration via f2f flow
- Update leaving a voice mail question to be yes-no radio button selection

## 13 Sep, 2019

- Fix template rendering for welcome email

## 10 Sep, 2019

- Update welcome email with forgot-password link
- Remove hard-coded cognito region with settings variable

## 06 Sep, 2019

- Remove confirm-f2f question
- Replace checkbox with radio type
- Remove f2f confirm question from models
- Make preferred time agreement question optional
- Fix typo in making preferred time question optional change

## 05 Sep, 2019

- Add appointment starting question
- Fix gender preference bug
- Include follower questions in queryset in multiple questions update

## 03 Sep, 2019

- Add multiple questions support, update services
- Add F2F questions

## 02 Sep, 2019

- Create separate table for appointment and add 1-1 key through user-response table

## 29 Aug, 2019

- Add default organisation setting to return default config on testing env
- Add CORS regex whitelisting

## 22 Aug, 2019

- Fix bug in password generation for user created from admin

## 21 Aug, 2019

- Pass all parameters to register api response

## 20 Aug, 2019

- Send email to user with password details on register from admin

## 16 Aug, 2019

- Add homepage phrases models and apis

## 02 Aug, 2019

- Update tests
- Update error message and add validation for not verified user on login

## 31 Jul, 2019

- Update cognito password reset service to handle user not found error
- Update password reset confirm api to handle case insensitive email
- Update confirm sign up api to use case insensitive email

## 18 Jul, 2019

- Add user not found exception in confirm sign up & resend verification
