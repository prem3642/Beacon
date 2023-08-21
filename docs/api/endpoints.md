For api overview and usages, check out [this page](overview.md).

# Authentication

For clients to authenticate, the token key should be included in the Authorization HTTP header. The key should be prefixed by the string literal “Token”, with whitespace separating the two strings. For example:

```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

Two different types of Auth available `User Auth`, `Answer Auth`.
Unauthenticated `User Auth` responses that are denied permission will result in an HTTP 401 Unauthorized response.
Unauthenticated `Answer Auth` responses that are denied permission will result in an HTTP 403 Unauthorized response.

An example request:

```
curl http://localhost:8000/api/example/ -H `Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

NOTE: All calls requires authorization unless specified.

## Login

```
POST /api/auth/login (No Authorization Required)
```

__Parameters__

| Name     | Description           |
| -------- | --------------------- |
| email    | email of the user.    |
| password | password of the user. |

__Request__
```json
{
    "email": "hello@example.com",
    "password": "VerySafePassword0909"
}
```

__Response__

Status: `200 OK`

```json
{
    "id": "99743597-371f-40fa-b7a7-2d254df4044c",
    "email": "test@example.com",
    "first_name": "User",
    "last_name": "01",
    "phone": "+18888888888",
    "address1": "123 Est Road",
    "address2": null,
    "city": "NYC",
    "zip": "11008",
    "gender": "M",
    "state": "NY",
    "employment_status": "Full Time",
    "relationship_status": "Single",
    "job_title": "Executive/Manager",
    "mdlive_id": 642188195,
    "is_verified": true,
    "agrees_to_beacon_privacy_notice": true,
    "agrees_to_mdlive_informed_consent": true,
    "agrees_to_mdlive_privacy_agreement": true,
    "mdlive_consent_user_initials": "MJ",
    "chief_complaint1": "Anxiety",
    "chief_complaint2": "Grief or Loss",
    "appointment_state": "AL",
    "md_live": {
        "jwt": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyaWQiOjY0MjE4ODE5NSwidXNlcm5hbWUiOiJNRExJVkUtNzQ2NzczODUtNGNkMS00NTMzLTlhZTMtNzQ0ZjBlZmNjNTkxIiwiYXBpX2NyZWRfaWQiOjUyMywiZXhwIjoxNTU3Nzg3ODA5fQ.gBNXLzX9K13OJk1_MUd1ipOq0JtM3MpEeZ7OoPZUGto",
        "user": {
            "id": 642188195,
            "type": "Patient",
            "time_to_live_minutes": 60
        }
    },
    "md_live_ou": "beaconeapwellness",
    "auth_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2F1dGhlbnRpY2F0aW9uX2lkIjoiOWRiN2I2YjMtNjM1Yi00YmRkLTg1NjAtZmFlOThjN2JjNTgzIn0.uvMttjFfTA8sJvuGd0TZcztthGR9icYsv9CGSQ9oOEA:1h8k46:VRRdYYtRQrjnKbOUsxsxecheV1A"
}
```

or

```json
{
    "errors": [
        {
            "message": {
                "num_of_failed_login_attempts": 5,
                "error": "Either email or password not valid!"
            }
        }
    ],
    "error_type": "ValidationError"
}
```

## Logout

```
POST /api/auth/logout (User Authorization Required)
```

__NOTE__: This api invalidate beacon and cognito tokens but MDLive token will still work till its expiry.

__Response__

Status: `200 OK`

```
{
  "message": "Successfully logged out"
}
```

## Register

```
POST /api/auth/register
```

__Parameters__

| Name                               | Description                                                                                                                                       |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| email                              | email of the user. Errors out if email already registered.                                                                                        |
| password                           | password of the user. Minimum 8 characters and one capital required.                                                                              |
| first_name                         | First name of the user                                                                                                                            |
| last_name                          | Last name of the user                                                                                                                             |
| gender                             | Gender of the user. Available options ('M', 'F')                                                                                                  |
| birthdate                          | Birth date of the user. Format should be (mm/dd/yyyy)                                                                                             |
| phone                              | Phone number of the user                                                                                                                          |
| address1                           | address1 of the user's mailing address                                                                                                            |
| address2                           | address2 of the user's mailing address                                                                                                            |
| city                               | city of the user's mailing address                                                                                                                |
| state                              | state of the user's mailing address. Available options specified below                                                                            |
| zip                                | zipcode of the user's mailing address                                                                                                             |
| relationship                       | Relationship of user to primary account holder. Specified as either 'Self', 'Spouse', 'Child', or 'Other Adult'                                   |
| employment_status                  | Employment status of the user. Available options are given below                                                                                  |
| relationship_status                | Relationship status of the user. Available options are given below                                                                                |
| job_title                          | Job title of the user. Available options are given below                                                                                          |
| answer                             | Answer object id to link all the responses with the user                                                                                          |
| agrees_to_beacon_privacy_notice    | User agreed to beacon privacy terms                                                                                                               |
| agrees_to_mdlive_privacy_agreement | User agreed to mdlive privacy terms                                                                                                               |
| agrees_to_mdlive_informed_consent  | User gave mdlive consent                                                                                                                          |
| mdlive_consent_user_initials       | User mdlive consent initials                                                                                                                      |
| organisation                       | Organisation object id to link organisation with the user for future use - (Optional, if not given then BE link it with the default organisation) |
| chief_complaint1                   | User's Chief Complaint for MDLive (optional)                                                                                                      |
| chief_complaint2                   | User's another Chief Complaint for MDLive (optional)                                                                                              |
| appointment_state                  | User's mdlive appointment state                                                                                                                   |
| timezone                           | User's timezone                                                                                                                                   |

**STATE OPTIONS**

- AL
- AK
- AZ
- AR
- CA
- CO
- CT
- DC
- DE
- FL
- GA
- HI
- ID
- IL
- IN
- IA
- KS
- KY
- LA
- ME
- MD
- MA
- MI
- MN
- MS
- MO
- MT
- NE
- NV
- NH
- NJ
- NM
- NY
- NC
- ND
- OH
- OK
- OR
- PA
- PR
- RI
- SC
- SD
- TN
- TX
- UT
- VT
- VA
- WA
- WV
- WI
- WY

**EMPLOYMENT STATUS OPTIONS**

- Full Time
- Part Time
- Terminated
- Medical Leave
- Retired
- Disciplinary Leave
- Laid Off
- Disability/Worker’s Compensation
- Dependent

**RELATIONSHIP STATUS OPTIONS**

- Never Married
- Married
- Divorced
- Cohabitating
- Separated
- Widowed
- Prefer not to say

**JOB TITLE OPTIONS**

- Executive/Manager
- Professional
- Technical
- Sales
- Office/Clerical
- Craft Worker
- Operative
- Laborer
- Service Worker
- Dependent

__Request__
```json
{
  "first_name": "beacon",
  "last_name": "health",
  "gender": "M",
  "birthdate": "07/10/1990",
  "phone": "+18888888888",
  "email": "mayank+13@fueled.com",
  "address1": "123 Est Road",
  "city": "Sunrise",
  "state": "FL",
  "zip": "33325",
  "relationship": "Self",
  "relationship_status": "Never Married",
  "employment_status": "Full Time",
  "job_title": "Technical",
  "password": "E12345678",
  "answer": "c7b41606-282a-4535-b85e-09948be2d475",
  "agrees_to_beacon_privacy_notice": true,
  "agrees_to_mdlive_informed_consent": true,
  "agrees_to_mdlive_privacy_agreement": true,
  "mdlive_consent_user_initials": "BH",
  "organisation": "c7b41606-282a-4535-b85e-09948be2d475",
  "appointment_state": "Puerto Rico",
  "timezone": "America/New_York"
}
```

__Response__
Status: `201 Created`

```json
{
    "id": "99743597-371f-40fa-b7a7-2d254df4044c",
    "email": "test@example.com",
    "first_name": "User",
    "last_name": "01",
    "phone": "+18888888888",
    "address1": "123 Est Road",
    "address2": null,
    "city": "NYC",
    "zip": "11008",
    "gender": "M",
    "state": "NY",
    "employment_status": "Full Time",
    "relationship_status": "Single",
    "job_title": "Executive/Manager",
    "mdlive_id": 642188195,
    "is_verified": true,
    "agrees_to_beacon_privacy_notice": true,
    "agrees_to_mdlive_informed_consent": true,
    "agrees_to_mdlive_privacy_agreement": true,
    "mdlive_consent_user_initials": "MJ",
    "chief_complaint1": "Anxiety",
    "chief_complaint2": "Grief or Loss",
    "appointment_state": "AL",
    "md_live": {
        "jwt": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyaWQiOjY0MjE4ODE5NSwidXNlcm5hbWUiOiJNRExJVkUtNzQ2NzczODUtNGNkMS00NTMzLTlhZTMtNzQ0ZjBlZmNjNTkxIiwiYXBpX2NyZWRfaWQiOjUyMywiZXhwIjoxNTU3Nzg3ODA5fQ.gBNXLzX9K13OJk1_MUd1ipOq0JtM3MpEeZ7OoPZUGto",
        "user": {
            "id": 642188195,
            "type": "Patient",
            "time_to_live_minutes": 60
        }
    },
    "md_live_ou": "beaconeapwellness",
    "auth_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2F1dGhlbnRpY2F0aW9uX2lkIjoiOWRiN2I2YjMtNjM1Yi00YmRkLTg1NjAtZmFlOThjN2JjNTgzIn0.uvMttjFfTA8sJvuGd0TZcztthGR9icYsv9CGSQ9oOEA:1h8k46:VRRdYYtRQrjnKbOUsxsxecheV1A",
    "timezone": "America/New_York"
}
```

## Resend Verification email

```
POST /api/auth/resend-verification-email
```

__Parameters__

| Name  | Description       |
| ----- | ----------------- |
| email | Email of the user |

__Request__
```json
{
    "email": "test@example.com"
}
```

__Response__

Status: `200 OK`

```
{
    "message": "Further instructions will be sent to the email if it exists"
}
```

## Confirm Sign Up

```
POST /api/auth/confirm-sign-up
```

__Parameters__

| Name  | Description                   |
| ----- | ----------------------------- |
| email | Email of the user             |
| otp   | OTP received by user on email |

__Request__
```json
{
    "email": "test@example.com",
    "otp": "919667"
}
```

__Response__

Status: `200 OK`

```
{
  "message": "User is successfully verified"
}
```

## Extend Auth Token

```
POST /api/auth/extend-token  (requires authentication)
```

__Response__

Status: `200 OK`

```
{
    "auth_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2F1dGhlbnRpY2F0aW9uX2lkIjoiOTFmYjg5NGMtMmE2Ny00MGJiLTllNWYtMjZhZWYyMTIzNTQyIn0.vUx7XfDaEkS_5mFxJ53Wsn9wa2y8-ugGXrZxI8cYlpY:1hBx44:wskY4rCw9aEn8CFC1xWB90-Ayss"
}
```


## Change password

```
POST /api/auth/password-change (requires authentication)
```

__Parameters__

| Name             | Description                   |
| ---------------- | ----------------------------- |
| current_password | Current password of the user. |
| new_password     | New password of the user.     |

__Request__
```json
{
    "current_password": "NotSoSafePassword",
    "new_password": "VerySafePassword0909"
}
```

__Response__
Status: `200 OK`

```
{
  "message": "Password changed successfully!"
}
```


## Request password for reset

Send an email to user if the email exist.

```
POST /api/auth/password-reset
```

__Parameters__

| Name  | Description                                 |
| ----- | ------------------------------------------- |
| email | (required) valid email of an existing user. |

__Request__
```json
{
    "email": "hello@example.com"
}
```

__Response__
Status: `420`

```json
{
  "errors": [
    {
      "message": "User is not verified yet!"
    }
  ],
  "error_type": "NotVerified"
}
```

Status: `200 OK`

```json
{
    "message": "Further instructions will be sent to the email if it exists"
}
```

or

```json
{
  "errors": [
    {
      "message": "Failed attempt limit exceeded, please try again after sometime!"
    }
  ],
  "error_type": "ValidationError"
}
```

or

```json
{
  "errors": [
    {
      "message": "This account has been disabled. Please contact an administrator!"
    }
  ],
  "error_type": "ValidationError"
}
```

## Confirm password reset

Confirm password reset for the user using the token sent in email.

```
POST /api/auth/password-reset-confirm
```

__Parameters__

| Name         | Description                   |
| ------------ | ----------------------------- |
| email        | Email of the user             |
| otp          | OTP received by user on email |
| new_password | New password of the user      |


__Request__
```json
{
    "email": "test@example.com",
    "new_password": "new_pass",
    "otp" : "123456"
}
```

__Response__
Status: `200 OK`

```
{
  "message": "Password changed successfully!"
}
```

# Current User Actions

## Get profile of current logged-in user
```
GET /api/me (requires authentication)
```

__Response__

Status: `200 Ok`

```json
{
    "id": "99743597-371f-40fa-b7a7-2d254df4044c",
    "email": "test@example.com",
    "first_name": "User",
    "last_name": "01",
    "phone": "+18888888888",
    "address1": "123 Est Road",
    "address2": null,
    "city": "NYC",
    "zip": "11008",
    "gender": "M",
    "state": "NY",
    "employment_status": "Full Time",
    "relationship_status": "Single",
    "job_title": "Executive/Manager",
    "mdlive_id": 642188195,
    "is_verified": true,
    "agrees_to_beacon_privacy_notice": true,
    "agrees_to_mdlive_informed_consent": true,
    "agrees_to_mdlive_privacy_agreement": true,
    "mdlive_consent_user_initials": "MJ",
    "chief_complaint1": "Anxiety",
    "chief_complaint2": "Grief or Loss",
    "appointment_state": "AL",
    "md_live": {
        "jwt": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyaWQiOjY0MjE4ODE5NSwidXNlcm5hbWUiOiJNRExJVkUtNzQ2NzczODUtNGNkMS00NTMzLTlhZTMtNzQ0ZjBlZmNjNTkxIiwiYXBpX2NyZWRfaWQiOjUyMywiZXhwIjoxNTU3Nzg3ODA5fQ.gBNXLzX9K13OJk1_MUd1ipOq0JtM3MpEeZ7OoPZUGto",
        "user": {
            "id": 642188195,
            "type": "Patient",
            "time_to_live_minutes": 60
        }
    },
    "md_live_ou": "beaconeapwellness",
    "organisation": "03d2eec3-e638-46c1-99c4-c90335de37e8"
}
```

## Update profile of current logged-in user
```
PATCH /api/me (requires authentication)
```

__Parameters__

| Name                | Description                                                            |
| ------------------- | ---------------------------------------------------------------------- |
| first_name          | First name of the user                                                 |
| last_name           | Last name of the user                                                  |
| gender              | Gender of the user. Available options ('M', 'F')                       |
| phone               | Phone number of the user                                               |
| address1            | address1 of the user's mailing address                                 |
| address2            | address2 of the user's mailing address                                 |
| city                | city of the user's mailing address                                     |
| state               | state of the user's mailing address. Available options specified below |
| zip                 | zipcode of the user's mailing address                                  |
| employment_status   | Employment status of the user. Available options are given below       |
| relationship_status | Relationship status of the user. Available options are given below     |
| job_title           | Job title of the user. Available options are given below               |

**STATE OPTIONS**

- AL
- AK
- AZ
- AR
- CA
- CO
- CT
- DC
- DE
- FL
- GA
- HI
- ID
- IL
- IN
- IA
- KS
- KY
- LA
- ME
- MD
- MA
- MI
- MN
- MS
- MO
- MT
- NE
- NV
- NH
- NJ
- NM
- NY
- NC
- ND
- OH
- OK
- OR
- PA
- PR
- RI
- SC
- SD
- TN
- TX
- UT
- VT
- VA
- WA
- WV
- WI
- WY

**EMPLOYMENT STATUS OPTIONS**

- Full Time
- Part Time
- Terminated
- Medical Leave
- Retired
- Disciplinary Leave
- Laid Off
- Disability/Worker’s Compensation
- Dependent

**RELATIONSHIP STATUS OPTIONS**

- Never Married
- Married
- Divorced
- Cohabitating
- Separated
- Widowed
- Prefer not to say

**JOB TITLE OPTIONS**

- Executive/Manager
- Professional
- Technical
- Sales
- Office/Clerical
- Craft Worker
- Operative
- Laborer
- Service Worker
- Dependent

__Request__
```json
{
    "first_name": "User",
    "state": "PR",
    "phone": "8888888888"
}
```

__Response__

Status: `200 Ok`

```json
{
    "message": "User profile has been updated successfully!"
}
```

## Update intake question responses of current logged-in user
```
PATCH /api/me/update-responses (requires authentication)
```

__Parameters__

| Name     | Description                                                                 |
| -------- | --------------------------------------------------------------------------- |
| id       | Answer object id to link all the responses with the current user (optional) |
| response | array of question objects (optional)                                        |

__Question object Parameters__

| Name                        | Description                                                                 |
| --------------------------- | --------------------------------------------------------------------------- |
| question                    | uuid of the question                                                        |
| answer                      | user response value for the question                                        |
| nested_response             | question object - (optional, required for nested questions only)            |
| multiple_questions_response | array of question object - (optional, required for multiple questions only) |

NOTE: Validation on each question type is there and return validation error like:

__Request__
```json
{
    "id": "99743597-371f-40fa-b7a7-2d254df4044c"
}
```

__Response__

Status: `200 Ok`

```json
{
  "message": "User responses updated successfully!"
}
```

## Update appointment state of current logged-in user

```
POST /api/me/update-appointment-state (requires authentication)
```

__Request__:

```json
{
    "appointment_state": "Florida"
}
```

__Response__

Status: `200 Ok`

```json
{
  "message": "Appointment State updated successfully!"
}
```

# Questionnaire

## Get all questions
```
GET /api/questions (No Authorization Required)
```

__Response__

Status: `200 OK`

```json
{
    "count": 6,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": "4b5527da-4622-499c-b35c-65c3c6378608",
            "kind": "multiple_questions",
            "text": "Enter your address",
            "placeholder": "",
            "is_required": true,
            "min_length": null,
            "max_length": null,
            "is_start": false,
            "yes_button_text": null,
            "no_button_text": null,
            "next_question": "55186c08-0278-43ac-8856-e23e37c57f73",
            "previous_question": "6224b4b4-3880-414b-9f9e-4641380f665d",
            "show_safety_screen": false,
            "choices": [],
            "nested_question": null,
            "multiple_questions": [
                {
                    "id": "c86abaf7-0ef2-4aa8-9fc0-18681881523c",
                    "kind": "dropdown",
                    "text": "State",
                    "placeholder": "State",
                    "is_required": true,
                    "min_length": null,
                    "max_length": 3,
                    "is_start": false,
                    "yes_button_text": null,
                    "show_safety_screen": false,
                    "no_button_text": null,
                    "next_question": null,
                    "previous_question": null,
                    "choices": [
                        {
                            "id": "1f031156-3e4a-42db-bc52-0aa8a6122ae1",
                            "text": "Alabama",
                            "next_question": null,
                            "previous_question": null
                        },
                        {
                            "id": "6cf50269-aca7-4757-8782-6f0bc72880d6",
                            "text": "Alaska",
                            "next_question": null,
                            "previous_question": null
                        }
                    ],
                    "nested_question": null,
                    "multiple_questions": null
                },
                {
                    "id": "1cbf8e25-f730-4aab-9fbf-3d90fe0dc8f2",
                    "kind": "text",
                    "text": "Zip",
                    "placeholder": "Zip",
                    "is_required": true,
                    "min_length": 5,
                    "max_length": 5,
                    "is_start": false,
                    "yes_button_text": null,
                    "no_button_text": null,
                    "next_question": null,
                    "previous_question": null,
                    "show_safety_screen": false,
                    "choices": [],
                    "nested_question": null,
                    "multiple_questions": null
                }
            ]
        },
        {
            "id": "dc50183e-3581-4587-817d-b3a4e6dd0a4e",
            "kind": "multiple_choice",
            "text": "for",
            "placeholder": "",
            "is_required": true,
            "min_length": null,
            "max_length": null,
            "is_start": false,
            "yes_button_text": null,
            "no_button_text": null,
            "next_question": null,
            "previous_question": null,
            "show_safety_screen": false,
            "choices": [
                {
                    "id": "85a510c5-2519-4c22-86cd-f3eb0fd08cdc",
                    "text": "Stress",
                    "next_question": null,
                    "previous_question": null
                },
                {
                    "id": "992684c2-62a4-4190-9530-da78a1fb3d2d",
                    "text": "Depression",
                    "next_question": null,
                    "previous_question": null
                },
                {
                    "id": "0c04d117-149e-4f45-8b92-63bb32923efd",
                    "text": "Anxiety",
                    "next_question": null,
                    "previous_question": null
                }
            ],
            "nested_question": null
        },
        {
            "id": "cd6808ac-ca73-446b-b6de-dc1bea32b962",
            "kind": "dropdown",
            "text": "in",
            "placeholder": "",
            "is_required": true,
            "min_length": null,
            "max_length": null,
            "is_start": false,
            "yes_button_text": null,
            "no_button_text": null,
            "next_question": null,
            "previous_question": null,
            "show_safety_screen": false,
            "choices": [
                {
                    "id": "b25bf47e-7b6d-48af-ac39-9db9f95b1994",
                    "text": "Colorado",
                    "next_question": null,
                    "previous_question": null
                },
                {
                    "id": "d9e6eca4-8856-4a99-97bf-c0d34723f2e7",
                    "text": "California",
                    "next_question": null,
                    "previous_question": null
                },
                {
                    "id": "841c4e06-67cd-4636-82dd-e01ce5005291",
                    "text": "Arizona",
                    "next_question": null,
                    "previous_question": null
                },
                {
                    "id": "b3e1b56d-221f-4ba7-a9bd-e832010f9beb",
                    "text": "Alaska",
                    "next_question": null,
                    "previous_question": null
                },
                {
                    "id": "93f378da-830a-4dd7-9e5f-c559696d79ce",
                    "text": "Alabama",
                    "next_question": null,
                    "previous_question": null
                }
            ],
            "nested_question": "dc50183e-3581-4587-817d-b3a4e6dd0a4e"
        },
        {
            "id": "35091aa7-aa66-43ba-ac20-3ba793a0447f",
            "kind": "dropdown",
            "text": "Get emotional support for",
            "placeholder": "",
            "is_required": true,
            "min_length": null,
            "max_length": null,
            "is_start": false,
            "yes_button_text": null,
            "no_button_text": null,
            "next_question": "819be2f3-dbb0-48ea-9646-20a6505edde2",
            "previous_question": "02684d54-6f28-4323-b6a2-b7ad4dda75e5",
            "show_safety_screen": false,
            "choices": [
                {
                    "id": "eb5d91e8-bad7-4dfe-b076-c9ec65ce4014",
                    "text": "Coworker",
                    "next_question": null,
                    "previous_question": null
                },
                {
                    "id": "fa3a8d15-af6b-414a-9e63-bb8df97f6b6f",
                    "text": "Spouse",
                    "next_question": null,
                    "previous_question": null
                },
                {
                    "id": "38830f7f-d3ed-4459-9e35-bd9f714a8f2f",
                    "text": "Myself",
                    "next_question": null,
                    "previous_question": null
                }
            ],
            "nested_question": "cd6808ac-ca73-446b-b6de-dc1bea32b962"
        },
        {
            "id": "819be2f3-dbb0-48ea-9646-20a6505edde2",
            "kind": "checkbox",
            "text": "Over the last 2 weeks, how often have you felt down, depressed, or hopeless?",
            "placeholder": "",
            "is_required": true,
            "min_length": null,
            "max_length": null,
            "is_start": true,
            "yes_button_text": null,
            "no_button_text": null,
            "next_question": "02684d54-6f28-4323-b6a2-b7ad4dda75e5",
            "show_safety_screen": false,
            "choices": [
                {
                    "id": "506f77c4-f6a9-4abf-8682-05745e1bfc74",
                    "text": "Not at all",
                    "next_question": null
                },
                {
                    "id": "19fa6801-fc64-43fb-a522-59947e7856fc",
                    "text": "More than half the days",
                    "next_question": null
                },
                {
                    "id": "88277cbe-b5ac-4649-b57b-67b5bf46dbff",
                    "text": "Several days",
                    "next_question": null
                },
                {
                    "id": "cc953340-d338-4cd7-aec1-4f489a225ff0",
                    "text": "Nearly every day",
                    "next_question": null
                }
            ]
        },
        {
            "id": "02684d54-6f28-4323-b6a2-b7ad4dda75e5",
            "kind": "checkbox",
            "text": "Over the last 2 weeks, how often have you felt nervous, anxious or on edge?",
            "placeholder": "",
            "is_required": true,
            "min_length": null,
            "max_length": null,
            "is_start": false,
            "yes_button_text": null,
            "no_button_text": null,
            "next_question": "971bff38-7e09-4d53-881a-79bbdc73bdf3",
            "show_safety_screen": false,
            "choices": [
                {
                    "id": "da4e032f-c05d-451f-8b7b-00b317951e8a",
                    "text": "Not at all",
                    "next_question": null
                },
                {
                    "id": "91e2d7b2-c007-42ed-94f6-84eed19002a4",
                    "text": "More than half the days",
                    "next_question": null
                },
                {
                    "id": "3ecadcde-af67-483f-8e03-47cdb6714208",
                    "text": "Several days",
                    "next_question": null
                },
                {
                    "id": "a195b0b0-f809-4ad7-9ff2-1c321f596835",
                    "text": "Nearly every day",
                    "next_question": null
                }
            ]
        }
    ]
}
```

## Retrieve a question
```
GET /api/questions/{id}  (No Authorization Required)
```

__Response__

Status: `200 OK`

```json
{
    "id": "819be2f3-dbb0-48ea-9646-20a6505edde2",
    "kind": "checkbox",
    "text": "Over the last 2 weeks, how often have you felt down, depressed, or hopeless?",
    "subheading": null,
    "placeholder": "",
    "is_required": true,
    "min_length": null,
    "max_length": null,
    "is_start": true,
    "yes_button_text": null,
    "no_button_text": null,
    "next_question": "02684d54-6f28-4323-b6a2-b7ad4dda75e5",
    "previous_question": "02684d54-6f28-4323-b6a2-b7ad4dda75e5",
    "show_safety_screen": false,
    "choices": [
        {
            "id": "506f77c4-f6a9-4abf-8682-05745e1bfc74",
            "text": "Not at all",
            "next_question": null
        },
        {
            "id": "19fa6801-fc64-43fb-a522-59947e7856fc",
            "text": "More than half the days",
            "next_question": null
        },
        {
            "id": "88277cbe-b5ac-4649-b57b-67b5bf46dbff",
            "text": "Several days",
            "next_question": null
        },
        {
            "id": "cc953340-d338-4cd7-aec1-4f489a225ff0",
            "text": "Nearly every day",
            "next_question": null
        }
    ]
}
```

## Retrieve starting question
```
GET /api/questions/starting-question  (No Authorization Required)
```

__Response__

If starting question does not exists:

Status: `204 No Content`

Otherwise:

Status: `200 OK`

```json
{
    "id": "819be2f3-dbb0-48ea-9646-20a6505edde2",
    "kind": "checkbox",
    "text": "Over the last 2 weeks, how often have you felt down, depressed, or hopeless?",
    "subheading": null,
    "placeholder": "",
    "is_required": true,
    "min_length": null,
    "max_length": null,
    "is_start": true,
    "yes_button_text": null,
    "no_button_text": null,
    "next_question": "02684d54-6f28-4323-b6a2-b7ad4dda75e5",
    "previous_question": "02684d54-6f28-4323-b6a2-b7ad4dda75e5",
    "show_safety_screen": false,
    "choices": [
        {
            "id": "506f77c4-f6a9-4abf-8682-05745e1bfc74",
            "text": "Not at all",
            "next_question": null
        },
        {
            "id": "19fa6801-fc64-43fb-a522-59947e7856fc",
            "text": "More than half the days",
            "next_question": null
        },
        {
            "id": "88277cbe-b5ac-4649-b57b-67b5bf46dbff",
            "text": "Several days",
            "next_question": null
        },
        {
            "id": "cc953340-d338-4cd7-aec1-4f489a225ff0",
            "text": "Nearly every day",
            "next_question": null
        }
    ]
}
```

## Retrieve appointment question
```
GET /api/questions/appointment-starting-question  (No Authorization Required)
```

__Response__

If appointment starting question does not exists:

Status: `204 No Content`

Otherwise:

Status: `200 OK`

```json
{
    "id": "f9932fa1-b0dc-4884-9378-839e8a6fc1c6",
    "kind": "dropdown",
    "text": "How would you like to talk to your counselor?",
    "subheading": null,
    "placeholder": "",
    "is_required": true,
    "min_length": null,
    "max_length": null,
    "is_start": false,
    "yes_button_text": null,
    "no_button_text": null,
    "next_question": null,
    "previous_question": "b0302b54-8a36-4576-b56f-c5cd22a8af66",
    "show_safety_screen": false,
    "choices": [
        {
            "id": "5f3bc3f4-3357-4a26-ba15-5b014d2cdb76",
            "text": "Video",
            "next_question": null,
            "previous_question": null
        },
        {
            "id": "be3be8c5-a217-446f-918b-7182d14f76c5",
            "text": "Phone",
            "next_question": null,
            "previous_question": null
        },
        {
            "id": "43d43d5b-a65a-467b-9f7c-3b3a94d409e7",
            "text": "Face To Face",
            "next_question": "013eb3ee-57fa-4bd5-b8f6-e11e4c797f3a",
            "previous_question": null
        }
    ],
    "nested_question": null,
    "multiple_questions": null
}
```

## Retrieve nested questions
```
GET /api/questions/nested-questions  (No Authorization Required)
```

__Response__

Status: `200 OK`

```json
[
    {
        "id": "35091aa7-aa66-43ba-ac20-3ba793a0447f",
        "kind": "dropdown",
        "text": "Get emotional support for",
        "subheading": null,
        "placeholder": "",
        "is_required": true,
        "min_length": null,
        "max_length": null,
        "is_start": false,
        "yes_button_text": null,
        "no_button_text": null,
        "next_question": "819be2f3-dbb0-48ea-9646-20a6505edde2",
        "previous_question": "02684d54-6f28-4323-b6a2-b7ad4dda75e5",
        "show_safety_screen": false,
        "choices": [
            {
                "id": "024eefa5-2c60-4611-a403-9d095e3a6f49",
                "text": "MySelf",
                "next_question": null,
                "previous_question": null
            },
            {
                "id": "32f04b4f-c6d4-4c32-b55f-dc1c586a2c7d",
                "text": "A Dependent",
                "next_question": null,
                "previous_question": null
            },
            {
                "id": "390444a0-3450-4c26-8af0-7428e6f5895a",
                "text": "Spouse",
                "next_question": null,
                "previous_question": null
            },
            {
                "id": "38b2cb7c-4d38-49d7-a09c-b3246ec33fc9",
                "text": "CoWorker",
                "next_question": null,
                "previous_question": null
            }
        ],
        "nested_question": {
            "id": "cd6808ac-ca73-446b-b6de-dc1bea32b962",
            "kind": "dropdown",
            "text": "In",
            "subheading": null,
            "placeholder": "",
            "is_required": true,
            "min_length": null,
            "max_length": null,
            "is_start": false,
            "yes_button_text": null,
            "no_button_text": null,
            "next_question": null,
            "previous_question": null,
            "show_safety_screen": false,
            "choices": [
                {
                    "id": "93f378da-830a-4dd7-9e5f-c559696d79ce",
                    "text": "Alabama",
                    "next_question": null,
                    "previous_question": null
                },
                {
                    "id": "b3e1b56d-221f-4ba7-a9bd-e832010f9beb",
                    "text": "Alaska",
                    "next_question": null,
                    "previous_question": null
                },
                {
                    "id": "841c4e06-67cd-4636-82dd-e01ce5005291",
                    "text": "Arizona",
                    "next_question": null,
                    "previous_question": null
                },
                {
                    "id": "d9e6eca4-8856-4a99-97bf-c0d34723f2e7",
                    "text": "California",
                    "next_question": null,
                    "previous_question": null
                },
                {
                    "id": "b25bf47e-7b6d-48af-ac39-9db9f95b1994",
                    "text": "Colorado",
                    "next_question": null,
                    "previous_question": null
                }
            ],
            "nested_question": {
                "id": "dc50183e-3581-4587-817d-b3a4e6dd0a4e",
                "kind": "multiple_choice",
                "text": "for",
                "subheading": null,
                "placeholder": "",
                "is_required": true,
                "min_length": null,
                "max_length": null,
                "is_start": false,
                "yes_button_text": null,
                "no_button_text": null,
                "next_question": null,
                "previous_question": null,
                "show_safety_screen": false,
                "choices": [
                    {
                        "id": "0c04d117-149e-4f45-8b92-63bb32923efd",
                        "text": "Anxiety",
                        "next_question": null,
                        "previous_question": null
                    },
                    {
                        "id": "992684c2-62a4-4190-9530-da78a1fb3d2d",
                        "text": "Depression",
                        "next_question": null,
                        "previous_question": null
                    },
                    {
                        "id": "85a510c5-2519-4c22-86cd-f3eb0fd08cdc",
                        "text": "Stress",
                        "next_question": null,
                        "previous_question": null
                    }
                ],
                "nested_question": null
            }
        }
    }
]
```

## Get next question

```
GET /api/questions/{id}/next-question (Either answer auth or user auth required)
```

__Response__

Status: `200 Ok`

```json
{
    "id": "d337e86e-0ace-447c-9ce0-c51e2e79a7d2",
    "kind": "frontend",
    "text": "Help us understand a little more about what you’re going through",
    "subheading": null,
    "placeholder": "",
    "is_required": true,
    "min_length": null,
    "max_length": null,
    "is_start": false,
    "yes_button_text": null,
    "no_button_text": null,
    "next_question": null,
    "previous_question": null,
    "show_safety_screen": false,
    "frontend_url": null,
    "frontend_meta_data": null,
    "choices": [
        {
            "id": "19877400-4039-4f3b-b350-5d4a0fbe1233",
            "text": "Yes, I am",
            "next_question": null,
            "previous_question": null
        },
        {
            "id": "82512a7c-3860-4f6d-9d42-da42ce3828de",
            "text": "No, I am not",
            "next_question": null,
            "previous_question": null
        }
    ],
    "nested_question": null,
    "multiple_questions": null
}
```

## Get previous question

```
GET /api/questions/{id}/previous-question (Either answer auth or user auth required)
```

__Response__

Status: `200 Ok`

```json
{
    "id": "971d0aa3-8b00-4117-b40f-a610c7ea7206",
    "kind": "dropdown",
    "text": "Get emotional support for",
    "subheading": null,
    "placeholder": "",
    "is_required": true,
    "min_length": null,
    "max_length": null,
    "is_start": true,
    "yes_button_text": null,
    "no_button_text": null,
    "next_question": null,
    "previous_question": null,
    "show_safety_screen": false,
    "frontend_url": null,
    "frontend_meta_data": null,
    "choices": [
        {
            "id": "3812ae09-51ca-483f-84c1-7db04ff01a24",
            "text": "Myself",
            "next_question": null,
            "previous_question": null
        },
        {
            "id": "6a3ee8f8-32af-4ba4-8c0c-f9dfa4f02a54",
            "text": "My Partner",
            "next_question": null,
            "previous_question": null
        },
        {
            "id": "88674827-4208-426d-ad02-e286f0e5f0e0",
            "text": "A Co-Worker",
            "next_question": null,
            "previous_question": null
        },
        {
            "id": "283e4b9b-756d-47bc-b4ce-1b735a5c718f",
            "text": "A Dependent",
            "next_question": null,
            "previous_question": null
        }
    ],
    "nested_question": "9d32c55f-d871-455d-80b7-3a7cd2891e1a",
    "multiple_questions": null
}
```


# Answers

## Create a user response
```
POST /api/answers  (No authorization required)
```

__Parameters__

| Name                   | Description                                                                                                                             |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| response               | array of question objects                                                                                                               |
| mdlive_provider_id     | MDLive Provider Id selected by user for appointment - (optional)                                                                        |
| selected_timeslot      | MDLive Provider appointment timeslot selected by user - (optional)                                                                      |
| appointment_method     | MDLive appointment type selected by user (available options: `video`, `phone`) - (optional)                                             |
| last_answered_question | This field can be used by FE to store unique id of last answered question. It is a text field with limit of 50 characters. - (optional) |

__Question object Parameters__

| Name                        | Description                                                                 |
| --------------------------- | --------------------------------------------------------------------------- |
| question                    | uuid of the question                                                        |
| answer                      | user response value for the question                                        |
| nested_response             | question object - (optional, required for nested questions only)            |
| multiple_questions_response | array of question object - (optional, required for multiple questions only) |

NOTE: Validation on each question type is there and return validation error like:

```json
{
    "errors": [
        {
            "field": "response",
            "message": "Not at doesn't exists in valid choices of question id 02684d54-6f28-4323-b6a2-b7ad4dda75e5"
        }
    ],
    "error_type": "ValidationError"
}
```

Validations:
- `Multiple Checkbox/Multiple` Choice will take `array` as response
- `Checkbox/Dropdown/Yes_No/text` will take `string` as response
- `Number` will take `int` as response
- Nested questions validate answers nested with above validations


__Request__

```json
{
    "response": [
        {
            "question": "3a2390f1-c55a-4492-a36d-861d8a6a7bd9",
            "answer": null,
            "multiple_questions_response": [
                {
                    "question": "3b2390f1-c55a-4492-a36d-861d8a6a7bd9",
                    "answer": "lorem ipsum"
                },
                {
                    "question": "3a2390f1-c55a-4492-a36d-861d8a6a7bd9",
                    "answer": 10
                }
            ]
        },
        {
            "question": "3a2390f1-c55a-4492-a36d-861d8a6a7bd9",
            "answer": true
        },
        {
            "question": "0d055fa3-5b53-4456-a2a8-4282fd69296d",
            "answer": "Myself",
            "nested_response": {
                "question": "83a743bd-0953-45f9-893f-e29abde93991",
                "answer": "Nevada",
                "nested_response": {
                    "question": "83a743bd-0953-45f9-893f-e29abde93992",
                    "answer": "Anxiety",
                    "nested_response": {
                        "question": "83a743bd-0953-45f9-893f-e29abde93993",
                        "answer": "Depression"
                    }
                }
            }
        }
    ]
}
```

__Response__

Status: `201 Created`

```json
{
    "id": "ed80811f-2638-49f2-a87a-b5f89b706898",
    "response": [
        {
            "question": "lorem ipsum",
            "answer": null,
            "user_response_attribute": null,
            "user_appointment_attribute": "f2f_gender_preference",
            "multiple_questions_response": [
                {
                    "question": "lorem ipsum",
                    "answer": "option 1",
                    "user_response_attribute": null,
                    "user_appointment_attribute": "f2f_comfortable_language",
                    "text_mapped_value": "1"
                },
                {
                    "question": "lorem ipsum",
                    "answer": 8,
                    "user_response_attribute": null,
                    "user_appointment_attribute": "f2f_preferred_contact"
                }
            ]
        },
        {
            "question": "In the past year, have you used drugs or alcohol more than you meant to?",
            "answer": "Yes, I have",
            "user_response_attribute": "used_drugs",
            "user_appointment_attribute": null,
            "text_mapped_value": true
        },
        {
            "question": "Get emotional support for",
            "answer": "Myself",
            "user_response_attribute": "emotional_support_for",
            "user_appointment_attribute": null,
            "text_mapped_value": "Self",
            "nested_response": {
                "question": "in",
                "answer": "Nevada",
                "user_response_attribute": "appointment_state",
                "text_mapped_value": "CA",
                "nested_response": {
                    "question": "for",
                    "answer": "Anxiety",
                    "user_response_attribute": "chief_complaint1",
                    "text_mapped_value": "Anxiety",
                    "nested_response": {
                        "question": "and",
                        "answer": "Depression",
                        "user_response_attribute": "chief_complaint2",
                        "text_mapped_value": "Depression"
                    }
                }
            }
        }
    ],
    "mdlive_provider_id": null,
    "selected_timeslot": null,
    "appointment_method": null,
    "last_answered_question": null,
    "answer_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhbnN3ZXJfYXV0aGVudGljYXRpb25faWQiOiIxNmJiZDFjYS0wMjAwLTRjZWUtOTUyNS1iYjMxZTI2YTlmNDIifQ.b0USiy5PVm04h3sUVDmBuERVIJGiN2hfjzTsYYnnJ0Y:1gyy2j:FP7iSW99UPCRaUOX3ahoD6Azk2c"
}
```

## Add an answer

Append another answer in existing answer response

```
POST /api/answers/{id}/add_answer  (Answer Auth required)
```

__Parameters__

| Name                   | Description                                                                                                                             |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| response               | question object                                                                                                                         |
| last_answered_question | This field can be used by FE to store unique id of last answered question. It is a text field with limit of 50 characters. - (optional) |

__Question object Parameters__

| Name                        | Description                                                                 |
| --------------------------- | --------------------------------------------------------------------------- |
| question                    | uuid of the question                                                        |
| answer                      | user response value for the question                                        |
| nested_response             | question object - (optional, required for nested questions only)            |
| multiple_questions_response | array of question object - (optional, required for multiple questions only) |

NOTE: Validation on question type is there and return validation error like:

```json
{
    "errors": [
        {
            "field": "response",
            "message": "'Not at' doesn't exists in valid choices of question id 02684d54-6f28-4323-b6a2-b7ad4dda75e5"
        }
    ],
    "error_type": "ValidationError"
}
```

Validations:
- `Multiple Checkbox/Multiple` Choice will take `array` as response
- `Checkbox/Dropdown/Yes_No/text` will take `string` as response
- `Number` will take `int` as response
- Nested questions validate answers nested with above validations


__Request__

```json
{
    "response": {
        "question": "180a1061-c296-4fca-ad90-629e9ea21655",
        "answer": "Excellent"
    },
    "last_answered_question": "180a1061-c296-4fca-ad90-629e9ea21655"
}
```

__Response__

Status: `200 Ok`

```json
{
    "message": "Answer appended successfully!"
}
```

## Add or update an answer

Append another answer or update answer in existing user response

```
PATCH /api/answers/{id}/add-or-update-answer  (Answer Auth required)
```

__Parameters__

| Name                   | Description                                                                                                                             |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| response               | question object                                                                                                                         |
| last_answered_question | This field can be used by FE to store unique id of last answered question. It is a text field with limit of 50 characters. - (optional) |

__Question object Parameters__

| Name                        | Description                                                                 |
| --------------------------- | --------------------------------------------------------------------------- |
| question                    | uuid of the question                                                        |
| answer                      | user response value for the question                                        |
| nested_response             | question object - (optional, required for nested questions only)            |
| multiple_questions_response | array of question object - (optional, required for multiple questions only) |

NOTE: Validation on question type is there and return validation error like:

```json
{
    "errors": [
        {
            "field": "response",
            "message": "'Not at' doesn't exists in valid choices of question id 02684d54-6f28-4323-b6a2-b7ad4dda75e5"
        }
    ],
    "error_type": "ValidationError"
}
```

Validations:
- `Multiple Checkbox/Multiple` Choice will take `array` as response
- `Checkbox/Dropdown/Yes_No/text` will take `string` as response
- `Number` will take `int` as response
- Nested questions validate answers nested with above validations


__Request__

```json
{
    "response": {
        "question": "180a1061-c296-4fca-ad90-629e9ea21655",
        "answer": "Excellent"
    },
    "last_answered_question": "180a1061-c296-4fca-ad90-629e9ea21655"
}
```

__Response__

Status: `200 Ok`

```json
{
    "message": "Answer updated successfully!"
}
```

## Update user response
```
PATCH /api/answers/{id} (Answer Auth Required)
```

__Parameters__

| Name                   | Description                                                                                                                             |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| response               | array of question objects                                                                                                               |
| mdlive_provider_id     | MDLive Provider Id selected by user for appointment - (optional)                                                                        |
| selected_timeslot      | MDLive Provider appointment timeslot selected by user - (optional)                                                                      |
| appointment_method     | MDLive appointment type selected by user (available options: `video`, `phone`) - (optional)                                             |
| last_answered_question | This field can be used by FE to store unique id of last answered question. It is a text field with limit of 50 characters. - (optional) |

__Question object Parameters__

| Name                        | Description                                                                 |
| --------------------------- | --------------------------------------------------------------------------- |
| question                    | uuid of the question                                                        |
| answer                      | user response value for the question                                        |
| nested_response             | question object - (optional, required for nested questions only)            |
| multiple_questions_response | array of question object - (optional, required for multiple questions only) |

NOTE: Validation on each question type is there and return validation error like:

```json
{
    "errors": [
        {
            "field": "response",
            "message": "Not at doesn't exists in valid choices of question id 02684d54-6f28-4323-b6a2-b7ad4dda75e5"
        }
    ],
    "error_type": "ValidationError"
}
```

Validations:
- `Multiple Checkbox/Multiple` Choice will take `array` as response
- `Checkbox/Dropdown/Yes_No/text` will take `string` as response
- `Number` will take `int` as response
- Nested questions validate answers nested with above validations


__Request__

```json
{
    "response": [
        {
            "question": "819be2f3-dbb0-48ea-9646-20a6505edde2",
            "answer": "Not at all"
        },
        {
            "question": "02684d54-6f28-4323-b6a2-b7ad4dda75e5",
            "answer": "Nearly every day"
        }
    ]
}
```

__Response__

Status: `200 Ok`

```json
{
    "id": "ed80811f-2638-49f2-a87a-b5f89b706898",
    "response": [
        {
            "question": "Over the last 2 weeks, how often have you felt down, depressed, or hopeless?",
            "answer": "Not at all"
        },
        {
            "question": "Over the last 2 weeks, how often have you felt nervous, anxious or on edge?",
            "answer": "Nearly every day"
        }
    ],
    "mdlive_provider_id": null,
    "selected_timeslot": null,
    "appointment_method": null,
    "last_answered_question": null
}
```

## Extend Answer Token

Extend Answer JWT Token

```
POST /api/answers/extend-token  (Answer Auth Required)
```

__Response__

Status: `200 OK`

```json
{
    "answer_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyaWQiOjY0MjE3MzM4NSwidXNlcm5hbWUiOiJiZWFjb25oZWFsdGgxMjMiLCJhcGlfY3JlZF9pZCI6NTE3LCJleHAiOjE1NTExMDM1MDd9.v9t0023Z_pJAMFzRlUwVGy3ukEQkRaArh1R4MTyleLA"
}
```


# MDLive

## Fake User Token

Get fake user JWT token

```
GET /api/mdlive/fake-user-token  (Answer Auth Required)
```

__Response__

Status: `200 OK`

```json
{
    "jwt": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyaWQiOjY0MjE3MzM4NSwidXNlcm5hbWUiOiJiZWFjb25oZWFsdGgxMjMiLCJhcGlfY3JlZF9pZCI6NTE3LCJleHAiOjE1NTExODE1NzJ9.kcq1HV10RwZJD2NUCRRwb2gUU67WTmulIE_55vRyN5k",
    "user": {
        "id": 642173385,
        "type": "Patient",
        "time_to_live_minutes": 60
    }
}
```

## Search for providers

Search providers on MDLive

```
POST /api/mdlive/search-providers  (Answer Auth Required)
```

__NOTE__: Use the `/api/mdlive/fake-user-token` call given above to generate a token and pass the value of `jwt` key from that response to pass it in the `mdlive_token` query_param.

Use the `user.id` from the fake-user-token request to pass the query param `patient_id` which is mandatory for this request.

__Parameters__

| Name   | Description           |
| ------ | --------------------- |
| search | Search params objects |

__SearchObjectParameters__

| Name              | Description                                                                                                                                     |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| state_abbrev      | 2 Letter state abbreviated, from the states list                                                                                                |
| availability_type | Array, can be either ['phone'], ['video'], or ['phone', 'video']. Use to specify the preferred type of appointment for the patient - (Optional) |
| gender            | Preferred provider gender (Male or Female) - (optional)                                                                                         |
| provider_type_id  | Integer, Provider Type ID, from the provider types list (or the endpoint response) - (optional)                                                 |
| specific_date     | Date in YYYY-mm-dd format - (optional)                                                                                                          |
| language_id       | Integer, Language ID from the languages list (See [Languages](https://developers.mdlive.com/#languages)) - (optional)                           |

__URL Parameters__

| Name         | Description                                                                                   |
| ------------ | --------------------------------------------------------------------------------------------- |
| per_page     | # of providers per page - (Optional)                                                          |
| patient_id   | patient_id retrieved from the `user.id` of the `fake-user-token` request - (Required)         |
| mdlive_token | mdlive_token is the value  of `jwt` retrieved from the `fake-user-token` request - (Required) |
| page         | Page # - (Optional)                                                                           |

__Request__

```bash
curl -X POST {server_url}/api/mdlive/search-providers
  -H "Content-type: application/json"
  -H "Authorization: Token Answer-token"
  -H "Accept: application/json"
  -d '{ "search": {
           "state_abbrev": "FL",
           "language_id": 1
         }
      }'
```

__Response__

Status: `200 OK`

```json
{
    "providers": [
        {
            "id": 642180557,
            "fullname": "Dr. Nick Rivera",
            "gender": "Male",
            "photo_url": "/users/642180557/photo",
            "specialty": "General Practice",
            "group_name": null,
            "is_visit_now_available": false,
            "status": "Available",
            "next_appt_available_date": "2019-03-18T11:00:00-04:00",
            "availability_type": null,
            "photo_url_absolute": "https://stage-patient.mdlive.com/user/photo/642180557/medium_Screen_Shot_2019-02-06_at_12.51.41_PM.png"
        },
        {
            "id": 642176865,
            "fullname": "Dr. Diana Smith",
            "gender": "Female",
            "photo_url": "/users/642176865/photo",
            "specialty": "General Practice",
            "group_name": null,
            "is_visit_now_available": false,
            "status": null,
            "next_appt_available_date": null,
            "availability_type": null,
            "photo_url_absolute": "https://stage-patient.mdlive.com/user/photo/642176865/medium_Female-Doctor-Image.png"
        }
    ],
    "refine_search_options": {
        "default_provider_types": [
            {
                "id": 3,
                "name": "Family Physician",
                "had_consult_24_hr": false,
                "key": "general_health_adult"
            },
            {
                "id": 5,
                "name": "Therapist",
                "had_consult_24_hr": false,
                "key": "psychologist"
            },
            {
                "id": 6,
                "name": "Psychiatrist",
                "had_consult_24_hr": false,
                "key": "psychiatrist"
            },
            {
                "id": 12,
                "name": "Dermatologist",
                "had_consult_24_hr": false,
                "key": "dermatologist"
            }
        ],
        "availability_type": [
            "video",
            "phone"
        ]
    }
}
```

## Getting a Provider's Profile

After searching for available providers for a patient, the profile details for any provider selected by the patient are available.

```
GET /api/mdlive/providers-profile?provider_id=642180557  (Answer Auth Required)
```

__NOTE__: Use the `/api/mdlive/fake-user-token` call given above to generate a token and pass the value of `jwt` key from that response to pass it in the `mdlive_token` query_param.

__URL Parameters__

| Name              | Description                                                                                                                                                                        |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| provider_id       | MDLIVE ID for provider                                                                                                                                                             |
| availability_type | Can be either 'phone' or 'video', use to specify the preferred type of appointment for the patient - (Optional)                                                                    |
| provider_type     | Provider Type ID, from the [provider types list](https://developers.mdlive.com/#provider-types). Use to specify the preferred doctor type for an appointment - (Optional)          |
| specific_date     | Date in YYYY-mm-dd format, use to specify a preferred date for an appointment. Default is today. - (Optional)                                                                      |
| state_abbrev      | Abbreviation of U.S. [state](https://developers.mdlive.com/#states), use to specify the preferred state for the appointment. Default is the patient's MDLIVE address. - (Optional) |

__Request__

```bash
curl {server_url}/api/mdlive/providers-profile?provider_id=642180557
-H "Content-type: application/json"
-H "Authorization: Token Answer-token"
```

__Response__

Status: `200 OK`

```json
{
  "provider_details": {
    "id": 4,
    "fullname": "Travis Stork",
    "gender": "Male",
    "city": "MIAMI BEACH",
    "state_abbrev": "FL",
    "phone": "3057997818",
    "photo_url": "/users/4/photo",
    "photo_url_absolute": "https://patient.mdlive.com/assets/default-profile-picture.png",
    "years_in_practice": 15,
    "education": "Certified Nurse Educator",
    "about_me": "This is my profile description",
    "licenses": [
      {
        "state_id": 10,
        "state": "Florida"
      },
      {
        "state_id": 44,
        "state": "Texas"
      },
      {
        "state_id": 11,
        "state": "Georgia"
      }
    ],
    "languages": [
      {
        "id": 1,
        "name": "English",
        "alpha3_code": "eng"
      },
      {
        "id": 7,
        "name": "Polish",
        "alpha3_code": "pol"
      }
    ],
    "specialties": [
      {
        "id": 1,
        "name": "Abdominal Surgery",
        "code": "AS"
      },
      {
        "id": 51,
        "name": "General Practice",
        "code": "GP"
      }
    ],
    "publications": "Over 15 peer review publications in the field of emergency medicine and disaster medicine"
  },
  "availability_details": {
    "available_hours": [
      {
        "timeslot": "2018-01-10T15:00:00.000-05:00",
        "phys_availability_id": 6096481,
        "availability_type": [
          "video"
        ]
      },
      {
        "timeslot": "2018-01-10T15:30:00.000-05:00",
        "phys_availability_id": 6097008,
        "availability_type": [
          "phone"
        ]
      }
    ],
    "is_visit_now_available": false,
    "can_request_appointment": true,
    "appointment_date": "2018-01-15",
    "patient_appointment_types": [
      "video",
      "phone"
    ]
  }
}
```

## User Token

Get user JWT token

```
GET /api/mdlive/user-token  (User Auth Required)
```

__Response__

Status: `200 OK`

```json
{
    "jwt": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyaWQiOjY0MjE3MzM4NSwidXNlcm5hbWUiOiJiZWFjb25oZWFsdGgxMjMiLCJhcGlfY3JlZF9pZCI6NTE3LCJleHAiOjE1NTExODE1NzJ9.kcq1HV10RwZJD2NUCRRwb2gUU67WTmulIE_55vRyN5k",
    "user": {
        "id": 642173385,
        "type": "Patient",
        "time_to_live_minutes": 60
    }
}
```

## Extend Token

Extend user JWT token

```
POST /api/mdlive/extend-token  (User Auth Required)
```

__Parameters__

| Name      | Description            |
| --------- | ---------------------- |
| jwt_token | JWT token of the user. |

__Request__
```json
{
    "jwt_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyaWQiOjY0MjE3MzM4NSwidXNlcm5hbWUiOiJiZWFjb25oZWFsdGgxMjMiLCJhcGlfY3JlZF9pZCI6NTE3LCJleHAiOjE1NTExMDM1MDd9.v9t0023Z_pJAMFzRlUwVGy3ukEQkRaArh1R4MTyleLA"
}
```

__Response__

Status: `200 OK`

```json
{
    "jwt_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyaWQiOjY0MjE3MzM4NSwidXNlcm5hbWUiOiJiZWFjb25oZWFsdGgxMjMiLCJhcGlfY3JlZF9pZCI6NTE3LCJleHAiOjE1NTExMDM1MDd9.v9t0023Z_pJAMFzRlUwVGy3ukEQkRaArh1R4MTyleLA"
}
```

# Organisation

## Search Organisations

__NOTE__:

- This API will search the `title`, `location` & `alternate_names` of organisations and list all of them.
- `search_term` query parameter is required and should be at least 5 chars in length.
- Only active organisations will appear in search results.
- Parent organisations having child organisation will not be returned.

__Request__:

```
GET /api/organisations?search_term=fuele
```

__Response__:

```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "title": "Fueled",
            "domain": "fueled.com",
            "location": "London"
        }
    ]
}
```

## Get organisation configuration
```
GET /api/organisations/configuration (No Authorization Required)
```

__Response__

Status: `200 OK`

```json
{
  "id": "4b37f455-2a0f-4a12-80a7-2b6171850839",
  "domain": "test.example.com",
  "phone": "+18888888888",
  "username": "beaconapwellness",
  "program_name": "Beacon Wellbeing",
  "introduction": "Org specific carousel text",
  "logo": {
      "full_size": "http://localhost:8000/media/organisations/organisation/rF-BdIeCS_CvypP84yT4cw.png"
  },
  "glyph": {
      "full_size": "http://localhost:8000/media/organisations/organisation/rF-BdIeCS_CvypP84yT4cw.png"
  },
  "glyph_width": 3,
  "glyph_height": 3,
  "number_of_sessions": 5,
  "session_frequency": "per year",
  "is_no_of_sessions_hidden": true,
  "share_url": "https://client.mybeaconwellbeing.com",
  "company_code": "3344",
  "parent_code": "COT",
  "show_international_section": true,
  "mdlive_provider_type": 38,
  "show_safety_screen": false,
  "safety_screen_phone": null,
  "safety_screen_url": null,
  "show_disclaimer": false,
  "homepage_navs": [
        {
            "id": "68219e3a-4f52-44c6-ad70-6c5760046785",
            "label": "Get emotional support",
            "url": "/support",
            "is_emergency_nav": false,
            "sort_order": 1,
            "is_url_target_blank": false
        },
        {
            "id": "9f13ee3c-d905-4d11-bc40-9d14f55e476b",
            "label": "Find legal advice",
            "url": "/legal",
            "is_emergency_nav": false,
            "sort_order": 2,
            "is_url_target_blank": true
        },
        {
            "id": "f48d6f8e-5dde-4c4b-a6c4-080f5bcc33e5",
            "label": "Plan your finances",
            "url": "/financial",
            "is_emergency_nav": false,
            "sort_order": 3,
            "is_url_target_blank": true
        },
        {
            "id": "e63a89e8-55c2-49b1-b9ec-983024720a3c",
            "label": "Care for your family",
            "url": "/family",
            "is_emergency_nav": false,
            "sort_order": 4,
            "is_url_target_blank": false
        }
    ],
    "child_organisations": [
      {
        "id": "44aaecb7-53f5-4dbd-a00e-a774fc436c9f",
        "location": "Uchiyama America",
        "phone": "6173080722",
        "username": "BBF2",
        "program_name": "Beacon Wellbeing",
        "number_of_sessions": 5,
        "session_frequency": "per year",
        "is_no_of_sessions_hidden": false,
        "share_url": "https://client.mybeaconwellbeing.com",
        "company_code": "3344",
        "show_international_section": true,
        "parent_code": "COT"
      }
    ]
}
```

# Phrases

## Get homepage phrases

```
GET /api/phrases/home (requires authentication)
```

__Response__

Status: `200 Ok`

```json
[
    {
        "id": "f75980f3-b1bb-4a55-b9a5-a155e2c33ebc",
        "headline": "Look after your loved ones",
        "sub_headline": "with a private conversation with the right person. It only takes a few minutes to find an expert and schedule a time to talk."
    }
]
```

# Homepage Nav

## Get homepage navs
```
GET /api/homepage-navs (No Authorization Required)
```

Get the list of homepage navs available for the organisation

__Response__

Status: `200 OK`

```json
{
    "count": 4,
    "next": null,
    "previous": null,
    "results": [
         {
            "id": "68219e3a-4f52-44c6-ad70-6c5760046785",
            "label": "Get emotional support",
            "url": "/support",
            "is_emergency_nav": false,
            "sort_order": 1,
            "is_url_target_blank": false
        },
        {
            "id": "9f13ee3c-d905-4d11-bc40-9d14f55e476b",
            "label": "Find legal advice",
            "url": "/legal",
            "is_emergency_nav": false,
            "sort_order": 2,
            "is_url_target_blank": false
        },
        {
            "id": "f48d6f8e-5dde-4c4b-a6c4-080f5bcc33e5",
            "label": "Plan your finances",
            "url": "/financial",
            "is_emergency_nav": false,
            "sort_order": 3,
            "is_url_target_blank": true
        },
        {
            "id": "e63a89e8-55c2-49b1-b9ec-983024720a3c",
            "label": "Care for your family",
            "url": "/family",
            "is_emergency_nav": false,
            "sort_order": 4,
            "is_url_target_blank": true
        }
    ]
}
```

## Get homepage nav categories
```
GET /api/homepage-navs/{id}/categories (No Authorization Required)
```

Get the list of categories available for a homepage nav

__Response__

Status: `200 OK`

```json
[
    {
        "id": "676b6552-c781-45d1-a68b-5511e28556c8",
        "name": "Child Care Services",
        "subcategories": [
            {
                "id": "2dd32051-8ab7-4cda-9cc6-ef5acf7fa210",
                "name": "Adoption Assisted Search",
                "url": "http://www.powerflexweb.com/resultAdoptionAssistedSearchElement.php"
            },
            {
                "id": "cd9eafd3-276b-466d-9750-7f962a4fe80c",
                "name": "Adoption Provider Locator",
                "url": "http://www.powerflexweb.com/resultAdoptionLocatorElement.php"
            },
            {
                "id": "39aacfdf-9b52-4d91-a389-f08a5b41f635",
                "name": "Child Care Assisted Search",
                "url": "http://www.powerflexweb.com/resultChildCareAssistedSearchElement.php"
            },
            {
                "id": "de1dcf30-c928-49a9-a3d7-9ac67081d2a4",
                "name": "Child Care Provider Locator",
                "url": "http://www.powerflexweb.com/resultChildCareLocatorElement.php"
            }
        ]
    },
    {
        "id": "94d48e13-4284-414c-8346-ea3fbf21cf1f",
        "name": "Community Services",
        "subcategories": [
            {
                "id": "5d599761-a578-4308-aeba-0ac0c77c7c54",
                "name": "Volunteer Opportunities",
                "url": "http://www.powerflexweb.com/resultVolunteerOpportunitiesLocatorElement.php"
            }
        ]
    },
    {
        "id": "b3b26667-61db-43d3-8b9e-8fb34cfc2fca",
        "name": "Elder Care / Adult Care Services",
        "subcategories": [
            {
                "id": "340e9c63-f64a-4b6a-b210-ed053e610480",
                "name": "Adult Care Assisted Search",
                "url": "http://www.powerflexweb.com/resultElderCareLocatorElement.php"
            },
            {
                "id": "9308c679-96ef-429c-a391-6d58de618237",
                "name": "Adult Care Service Locator",
                "url": "http://www.powerflexweb.com/resultElderCareLocatorElement.php"
            }
        ]
    },
    {
        "id": "87f8ebf0-010b-45b4-b226-53089881cca6",
        "name": "Schools and Camps",
        "subcategories": [
            {
                "id": "284965d0-bf4b-4ab3-927c-7de75b7d3a69",
                "name": "Camp Locator",
                "url": "http://www.powerflexweb.com/resultCampLocatorElement.php"
            },
            {
                "id": "920170e4-0d96-4d05-8b84-57b4e27bb1e6",
                "name": "College Locator",
                "url": "http://www.powerflexweb.com/resultCollegeLocatorElement.php"
            },
            {
                "id": "91e144c3-b96c-431e-9ca1-9f2eacdd4a31",
                "name": "College Undergrad Locator",
                "url": "http://www.powerflexweb.com/resultCollegeUndergradLocatorElement.php"
            },
            {
                "id": "39c05611-aa49-4f01-afa1-d8791b48c661",
                "name": "Education Assisted Search",
                "url": "http://www.powerflexweb.com/resultEducationAssistedSearchElement.php"
            },
            {
                "id": "039ed59e-e085-4177-8bca-14943ab54e48",
                "name": "Scholarship Locator",
                "url": "http://www.powerflexweb.com/resultScholarshipLocatorElement.php"
            }
        ]
    },
    {
        "id": "4de2ca63-f426-4572-9ce1-f9ad24027351",
        "name": "Pet Care",
        "subcategories": [
            {
                "id": "a20ac797-921f-42ed-8a39-98b6f484300f",
                "name": "Pet Services Search",
                "url": "http://www.powerflexweb.com/resultPetLocatorElement.php"
            },
            {
                "id": "f07ba591-b155-45be-9952-73a806d8f9a2",
                "name": "Pet Services Locator",
                "url": "http://www.powerflexweb.com/resultPetLocatorElement.php"
            }
        ]
    }
]
```


# Appointments

## Create an appointment

```
POST /api/appointments  (User Auth required)
```

__Parameters__

| Name                   | Description                                                                                                                             |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| response               | question object                                                                                                                         |
| mdlive_provider_id     | MDLive Provider Id selected by user for appointment - (optional)                                                                        |
| selected_timeslot      | MDLive Provider appointment timeslot selected by user - (optional)                                                                      |
| last_answered_question | This field can be used by FE to store unique id of last answered question. It is a text field with limit of 50 characters. - (optional) |

__Question object Parameters__

| Name                        | Description                                                                 |
| --------------------------- | --------------------------------------------------------------------------- |
| question                    | uuid of the question                                                        |
| answer                      | user response value for the question                                        |
| nested_response             | question object - (optional, required for nested questions only)            |
| multiple_questions_response | array of question object - (optional, required for multiple questions only) |

NOTE: Validation on question type is there and return validation error like:

```json
{
    "errors": [
        {
            "field": "response",
            "message": "'Not at' doesn't exists in valid choices of question id 02684d54-6f28-4323-b6a2-b7ad4dda75e5"
        }
    ],
    "error_type": "ValidationError"
}
```

Validations:
- `Multiple Checkbox/Multiple` Choice will take `array` as response
- `Checkbox/Dropdown/Yes_No/text` will take `string` as response
- `Number` will take `int` as response
- Nested questions validate answers nested with above validations


__Request__

```json
{
    "response": {
        "question": "180a1061-c296-4fca-ad90-629e9ea21655",
        "answer": "Excellent"
    },
    "mdlive_provider_id": null,
    "selected_timeslot": null,
    "last_answered_question": null
}
```

__Response__

Status: `201 Created`

```json
{
    "id": "ed80811f-2638-49f2-a87a-b5f89b706898",
    "response": {
        "question": "lorem ipsum",
        "answer": null,
        "user_response_attribute": null,
        "user_appointment_attribute": "f2f_gender_preference",
        "multiple_questions_response": [
            {
                "question": "lorem ipsum",
                "answer": "option 1",
                "user_response_attribute": null,
                "user_appointment_attribute": "f2f_comfortable_language",
                "text_mapped_value": "1"
            }
        ]
    },
    "mdlive_provider_id": null,
    "selected_timeslot": null,
    "appointment_method": null,
    "last_answered_question": null
}
```

## Update an appointment

Append another answer to appointment response or update answer in existing appointment response

```
PATCH /api/appointments/{id}  (User Auth required)
```

__Parameters__

| Name                   | Description                                                                                                                             |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| response               | question object                                                                                                                         |
| mdlive_provider_id     | MDLive Provider Id selected by user for appointment - (optional)                                                                        |
| selected_timeslot      | MDLive Provider appointment timeslot selected by user - (optional)                                                                      |
| last_answered_question | This field can be used by FE to store unique id of last answered question. It is a text field with limit of 50 characters. - (optional) |

__Question object Parameters__

| Name                        | Description                                                                 |
| --------------------------- | --------------------------------------------------------------------------- |
| question                    | uuid of the question                                                        |
| answer                      | user response value for the question                                        |
| nested_response             | question object - (optional, required for nested questions only)            |
| multiple_questions_response | array of question object - (optional, required for multiple questions only) |

NOTE: Validation on question type is there and return validation error like:

```json
{
    "errors": [
        {
            "field": "response",
            "message": "'Not at' doesn't exists in valid choices of question id 02684d54-6f28-4323-b6a2-b7ad4dda75e5"
        }
    ],
    "error_type": "ValidationError"
}
```

Validations:
- `Multiple Checkbox/Multiple` Choice will take `array` as response
- `Checkbox/Dropdown/Yes_No/text` will take `string` as response
- `Number` will take `int` as response
- Nested questions validate answers nested with above validations


__Request__

```json
{
    "response": {
        "question": "180a1061-c296-4fca-ad90-629e9ea21655",
        "answer": "Excellent"
    },
    "last_answered_question": "180a1061-c296-4fca-ad90-629e9ea21655"
}
```

__Response__

Status: `200 Ok`

```json
{
    "id": "ed80811f-2638-49f2-a87a-b5f89b706898",
    "response": {
        "question": "180a1061-c296-4fca-ad90-629e9ea21655",
        "answer": "Excellent"
    },
    "last_answered_question": "180a1061-c296-4fca-ad90-629e9ea21655"
}
```

## Finalize an appointment

Finalize appointment to send data to BWB server and trigger email to user

```
POST /api/appointments/{id}/finalize  (User Auth required)
```

__Response__

Status: `200 Ok`

```json
{
  "message": "Appointment created successfully!"
}
```

## Get latest appointment

Get latest appointment for logged in user

```
GET /api/appointments/latest  (User Auth required)
```

__Response__

Status: `200 Ok`

```json
{
    "id": "21b530f5-2e81-4d92-931e-53cd189503a2",
    "appointment_method": "face_to_face",
    "mdlive_provider_id": null,
    "selected_time_slot": null,
    "show_homepage_message": true,
    "bwb_inquiry_id": "1111-1234",
    "created_at": "2019-09-23T09:21:52.923703Z",
    "modified_at": "2019-09-23T09:23:10.880884Z"
}
```


# Messages

## Create a message

```
POST /api/messages  (User Auth required)
```

__Parameters__

| Name                  | Description                                                            |
| --------------------- | ---------------------------------------------------------------------- |
| to_id                 | Provider id                                                            |
| subject               | Subject of the message                                                 |
| message               | Message body                                                           |
| replied_to_message_id | Message id if its a reply to a message (optional)                      |
| documents             | Array of uuids of documents to be attached with the message (optional) |


__Request__

```json
{
    "to_id": 642183606,
    "subject": "Testing",
    "message": "Testing message creation",
    "documents": ["87528443-476b-4aff-b5c5-535f26d86669", "a5c982e9-9d92-4f84-9458-a7a7d17adac3"]
}
```

__Response__

Status: `201 Created`

```json
{
    "id": 396488,
    "subject": "testing",
    "message": "testing message creation",
    "unread_status": true,
    "replied_to_message_id": null,
    "date_time": "2020-01-22T08:40:13.724375Z",
    "from": "User 01",
    "from_id": 642197373,
    "to": "Provider 01",
    "to_id": 642183606,
    "reply_allowed": false,
    "documents": [
        {
            "id": "87528443-476b-4aff-b5c5-535f26d86669",
            "mdlive_id": 1234,
            "document_name": "test.jpg",
            "mime_type": "image/jpg",
            "record_type": "Patient Record",
            "extension": "jpg"
        },
        {
            "id": "a5c982e9-9d92-4f84-9458-a7a7d17adac3",
            "mdlive_id": null,
            "document_name": "test.jpg",
            "mime_type": "image/jpg",
            "record_type": "Patient Record",
            "extension": null
        }
    ]
}
```

## Fetch list of messages

```
GET /api/messages  (User Auth required)
```

Filter messages list using `provider_id`, `unread_status`, `sent` and `received`

__Example__

```
/api/messages?unread_status=true&provider_id=642183606
/api/messages?sent=true
/api/messages?received=true
```

__Response__

Status: `200 Ok`

```json
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 393550,
            "subject": "Testing",
            "message": "Testing message creation",
            "unread_status": true,
            "replied_to_message_id": null,
            "date_time": "2019-12-06T15:18:39.470097Z",
            "from": "User 01",
            "from_id": 642197373,
            "to": "Provider 01",
            "to_id": 642183606,
            "reply_allowed": false,
            "documents": ["87528443-476b-4aff-b5c5-535f26d86669", "a5c982e9-9d92-4f84-9458-a7a7d17adac3"]
        },
        {
            "id": 393549,
            "subject": "Testing",
            "message": "Testing message creation",
            "unread_status": true,
            "replied_to_message_id": null,
            "date_time": "2019-12-06T15:18:16.674335Z",
            "from": "User 01",
            "from_id": 642197373,
            "to": "Provider 01",
            "to_id": 642183606,
            "reply_allowed": false,
            "documents": []
        }
    ]
}
```

## Fetch message detail

```
GET /api/messages/{id}  (User Auth required)
```

__Example__

```
/api/messages/393550
```

__Response__

Status: `200 Ok`

```json
{
    "id": 393550,
    "subject": "Testing",
    "message": "Testing message creation",
    "unread_status": true,
    "replied_to_message_id": null,
    "date_time": "2019-12-06T15:18:39.470097Z",
    "from": "User 01",
    "from_id": 642197373,
    "to": "Provider 01",
    "to_id": 642183606,
    "reply_allowed": false,
    "documents": [
        {
            "id": "87528443-476b-4aff-b5c5-535f26d86669",
            "mdlive_id": 1234,
            "document_name": "test.jpg",
            "mime_type": "image/jpg",
            "record_type": "Patient Record",
            "extension": "jpg"
        },
        {
            "id": "a5c982e9-9d92-4f84-9458-a7a7d17adac3",
            "mdlive_id": null,
            "document_name": "test.jpg",
            "mime_type": "image/jpg",
            "record_type": "Patient Record",
            "extension": null
        }
    ]
}
```

## Get unread messages count

```
GET /api/messages/unread-messages-count  (User Auth required)
```

__Response__

Status: `200 Ok`

```json
{
    "count": 4
}
```

## Mark message as read

```
PUT /api/messages/{message_id}/mark-read  (User Auth required)
```

__Response__

Status: `204 No Content`

## Get all contacts of logged in user

```
GET /api/contacts  (User Auth required)
```

__Response__

Status: `200 Ok`

```json
[
    {
        "id": 642183606,
        "fullname": "Provider 01",
        "prefix": "LCSW",
        "gender": "Male",
        "speciality": "General Practice",
        "photo_url": "/users/642183606/photo",
        "photo_url_absolute": "https://stage-patient.mdlive.com/assets/default-profile-picture.png"
    }
]
```

## Get contact detail

```
GET /api/contacts/{id}  (User Auth required)
```

__Response__

Status: `200 Ok`

```json
{
    "id": 642183606,
    "fullname": "Provider 01",
    "prefix": "LCSW",
    "gender": "Male",
    "speciality": "General Practice",
    "photo_url": "/users/642183606/photo",
    "photo_url_absolute": "https://stage-patient.mdlive.com/assets/default-profile-picture.png"
}
```


# Appointment Slot Queries

## Create an appointment slot query

```
POST /api/appointment-slot-queries  (User Auth required)
```

__Parameters__

| Name                     | Description                                                                                    |
| ------------------------ | ---------------------------------------------------------------------------------------------- |
| provider_id              | Provider id                                                                                    |
| preferred_time           | Preferred time of appointment. Should be one of (first available, morning, afternoon, evening) |
| appointment_method       | Requested type of appointment for the patient, should be 'video' or 'phone'                    |
| appointment_date         | Requested date for appointment, should be of format yyyy-mm-dd                                 |
| chief_complaint_comments | Extra comments regarding chief complaints (optional)                                           |


__Request__

```json
{
   "provider_id": 642193543,
   "appointment_date": "2018-12-20",
   "appointment_method": "phone",
   "preferred_time": "first available"
}
```

__Response__

Status: `200 Ok`

```json
{
    "id": "6b2b4354-d76b-4c61-ba6a-6f4b82c8abc9",
    "mdlive_id": 1284,
    "provider_id": 642193543,
    "preferred_time": "first available",
    "appointment_method": "phone",
    "appointment_date": "2018-12-20",
    "chief_complaint": "Anxiety",
    "chief_complaint_comments": null,
    "contact_number": "+19858001112",
    "appointment_request_state": "AL"
}
```

## Get all appointment slot queries

Retrieve the list of patient's all appointment slot queries

```
GET /api/appointment-slot-queries  (User Auth required)
```

__Response__

Status: `200 Ok`

```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": "486e7250-ed0a-471f-b8b1-2f68364f9a6a",
            "mdlive_id": 1285,
            "provider_id": 642193543,
            "preferred_time": "first available",
            "appointment_method": "phone",
            "appointment_date": "2018-12-20",
            "chief_complaint": "Anxiety",
            "chief_complaint_comments": null,
            "contact_number": "+19858001112",
            "appointment_request_state": "AL"
        }
    ]
}
```

## Get a specific appointment slot query


```
GET /api/appointment-slot-queries/{id}  (User Auth required)
```

__Response__

Status: `200 Ok`

```json
{
    "id": "486e7250-ed0a-471f-b8b1-2f68364f9a6a",
    "mdlive_id": 1285,
    "provider_id": 642193543,
    "preferred_time": "first available",
    "appointment_method": "phone",
    "appointment_date": "2018-12-20",
    "chief_complaint": "Anxiety",
    "chief_complaint_comments": null,
    "contact_number": "+19858001112",
    "appointment_request_state": "AL"
}
```

## Appointment slot query - Cancel

```
POST /api/appointment-slot-queries/{id}/cancel  (User Auth required)
```

Cancel a pending appointment slot query with a Provider.

__Response__

Status: `200 Ok`

```json
{
  "message": "Your appointment slot query has been cancelled"
}
```

## Appointment slot query - Remind

```
POST /api/appointment-slot-queries/{id}/remind  (User Auth required)
```

Remind a Provider with regards to a pending appointment slot query.

__Response__

Status: `200 Ok`

```json
{
  "message": "The Provider has been reminded about your appointment slot query"
}
```


# Documents

## Create a user document

```
POST /api/documents  (User Auth required)
```

__Parameters__

| Name          | Type   | Description                                                                                                    |
| ------------- | ------ | -------------------------------------------------------------------------------------------------------------- |
| id            | int    | Mdlive id received after uploading the document                                                                |
| document_name | string | Desired filename                                                                                               |
| mime_type     | string | Mime type, e.g. image/png                                                                                      |
| record_type   | string | One of the following values: (Behavioral, Exam-Face2Face, Patient Record, Test Result, Wellness Panel Results) |
| extension     | string | extension of the file uploaded to MDLive                                                                       |

__Response__

Status: `201 Created`

```json
{
    "id": "486e7250-ed0a-471f-b8b1-2f68364f9a6a",
    "mdlive_id": 1234,
    "document_name": "test.jpg",
    "mime_type": "image/jpg",
    "record_type": "Patient Record",
    "extension": "jpg"
}
```

## Get all user documents

Retrieve the list of a patient's current list of documents

```
GET /api/documents  (User Auth required)
```

__Response__

Status: `200 Ok`

```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": "486e7250-ed0a-471f-b8b1-2f68364f9a6a",
            "mdlive_id": 1234,
            "document_name": "test.jpg",
            "mime_type": "image/jpg",
            "extension": "jpg",
            "record_type": "Patient Record"
        }
    ]
}
```

## Retrieve specific user document

```
GET /api/documents/{id}  (User Auth required)
```

__Response__

Status: `200 Ok`

```json
{
    "id": "486e7250-ed0a-471f-b8b1-2f68364f9a6a",
    "mdlive_id": 1234,
    "document_name": "test.jpg",
    "mime_type": "image/jpg",
    "extension": "jpg",
    "record_type": "Patient Record"
}
```

## Delete a user document

```
DELETE /api/documents/{id}  (User Auth required)
```

__Response__

Status: `204 NoContent`
