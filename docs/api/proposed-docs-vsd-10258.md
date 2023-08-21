# Proposed API Docs - VSD-10258 SCC to BWB

## Create user

```
POST /api/users/sync (authorization required)
```

__Authorization__

- The API uses JSON Web Tokens (JWT) for authorization
- HS-256 will be used to generate JWT
- Secret key will be generated and shared by Fueled
- Payload will be:

```json
{"APP_NAME": "BeaconWellBeing", "exp": "1635494633"}
```

- Please generate a new token after every hour.

- The key generated should be provided in the `Authorization` HTTP header prefixed with `Token`.

__Parameters__

| Name                     | Required | Description                                                                                                                                 |
| ------------------------ | -------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| memberId                 | Yes      | Connects member id of the user in secure care connects system.                                                                              |
| email                    | Yes      | Email of the user.                                                                                                                          |
| firstName                | Yes      | First name of the user                                                                                                                      |
| lastName                 | Yes      | Last name of the user                                                                                                                       |
| dateOfBirth              | Yes      | Birth date of the user. Format should be (CYYMMDD, e.i: 1211025 === Oct 25th, 2021)                                                         |
| gender                   | Yes      | Gender of the user. Available options ('M', 'F', 'U')                                                                                       |
| addressLine1             | Yes      | Address line 1 of the user's mailing address                                                                                                |
| addressLine2             | No       | Address line 2 of the user's mailing address                                                                                                |
| city                     | Yes      | City of the user's mailing address                                                                                                          |
| stateCode                | Yes      | State of the user's mailing address. Available options specified below                                                                      |
| zipCode                  | Yes      | Zipcode of the user's mailing address                                                                                                       |
| phoneAreaCode            | Yes      | Part of Phone Number - area code                                                                                                            |
| phoneCentralOfficeCode   | Yes      | Part of Phone Number - central office code                                                                                                  |
| phoneExchange            | Yes      | Part of Phone Number - exchange                                                                                                             |
| parentCode               | Yes      | Parent code of the organization of the user                                                                                                 |
| groupNumber              | Yes      | Group number of the organization of the user                                                                                                |
| benefitPackage           | Yes      | Benefit package of the organization of the user                                                                                             |
| relationshipStatus       | No       | Relationship of the user to the primary account holder. Valid options are mentioned below                                                   |
| employmentStatus         | No       | Employment status of the user. Available options are given below                                                                            |
| jobTitle                 | No       | Job title of the user. Available options are given below                                                                                    |
| presentingProblemPrimary | Yes      | User's Chief Complaint for MDLive                                                                                                           |
| beaconWellBeingQus2      | No       | User's another Chief Complaint for MDLive                                                                                                   |
| beaconWellBeingQus3A     | No       | User's answer for - "Over the past 2 weeks, how often have you had little interest or pleasure in doing things?"                            |
| beaconWellBeingQus3B     | No       | User's answer for - "Over the past 2 weeks, how often have you felt down, depressed, or hopeless?"                                          |
| beaconWellBeingQus5A     | No       | User's answer for - "Over the past 2 weeks, how often have you felt nervous, anxious, or on edge?"                                          |
| beaconWellBeingQus5B     | No       | User's answer for - "Over the past 2 weeks, how often have you felt you have not been able to stop or control worrying?"                    |
| beaconWellBeingQus7A     | No       | User's answer for - "When you drink or use drugs, do you find that you have difficulty stopping or keeping the limit you set for yourself?" |
| beaconWellBeingQus7B     | No       | User's answer for - "In the past year, have you felt or someone else expressed you should cut down on your drinking or drug use?"           |
| beaconWellBeingQus8      | No       | User's answer for - "How would you say you're doing emotionally today?"                                                                     |
| beaconWellBeingQus9      | No       | User's answer for - "How would you describe your current physical health?"                                                                  |
| beaconWellBeingQus10     | No       | User's answer for - "I have people that support me in my life"                                                                              |
| beaconWellBeingQus11     | No       | User's answer for - "I feel comfortable with the way I am managing my finances"                                                             |
| beaconWellBeingQus12     | No       | User's answer for - "I have the tools to manage life challenges"                                                                            |
| outcomeQuestion1         | No       | User's answer for - "During the past 30 days, how many days did you miss from your job because of your behavioral health issues?"           |
| outcomeQuestion2         | No       | User's answer for - "During the past 30 days, how many days were you less productive at work than usual?"                                   |
| mdLiveUserID             | No       | MDLive user id of the user                                                                                                                  |

**STATE OPTIONS**

- AA
- AE
- AL
- AN
- AP
- BH
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
- GU
- HI
- ID
- IL
- IN
- KR
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
- VI
- WA
- WV
- WI
- WY
- XX
- YA
- ZZ

**EMPLOYMENT STATUS OPTIONS**

| Option | Description                      |
| ------ | -------------------------------- |
| FT     | Full Time                        |
| PT     | Part Time                        |
| TM     | Terminated                       |
| ML     | Medical Leave                    |
| RE     | Retired                          |
| DL     | Disciplinary Leave               |
| LO     | Laid Off                         |
| IL     | Disability/Worker’s Compensation |
| OT     | Other                            |

**RELATIONSHIP STATUS OPTIONS**

| Option | Description       |
| ------ | ----------------- |
| 1      | Never Married     |
| M      | Married           |
| 5      | Separated         |
| D      | Divorced          |
| W      | Widowed           |
| 4      | Cohabitating      |
| N      | Data not provided |

**JOB TITLE OPTIONS**

| Option | Description       |
| ------ | ----------------- |
| EXEC   | Executive/Manager |
| PROF   | Professional      |
| TECH   | Technical         |
| SALE   | Sales             |
| OFFI   | Office/Clerical   |
| CRAF   | Craft Worker      |
| OPER   | Operative         |
| LABO   | Laborer           |
| SER    | Service Worker    |
| DATA   | Data Not Provided |

__Request__

```json
{
    "memberId": "2d254df4-1111-2222-3333-123456789123",
    "email": "mayank+13@fueled.com",
    "firstName": "beacon",
    "lastName": "health",
    "dateOfBirth": "1211025",
    "gender": "M",
    "addressLine1": "123 Est Road",
    "addressLine2": "777 Wst Lane",
    "city": "Sunrise",
    "stateCode": "FL",
    "zipCode": "33325",
    "phoneAreaCode": "912",
    "phoneCentralOfficeCode": "888",
    "phoneExchange": "8888",
    "parentCode": "ABC",
    "groupNumber": "123",
    "benefitPackage": "demo",
    "relationshipStatus": "1",
    "employmentStatus": "FT",
    "jobTitle": "TECH",
    "presentingProblemPrimary": "AX",
    "beaconWellBeingQus2": "ST",
    "beaconWellBeingQus3A": "1",
    "beaconWellBeingQus3B": "2",
    "beaconWellBeingQus5A": "3",
    "beaconWellBeingQus5B": "0",
    "beaconWellBeingQus7A": "N",
    "beaconWellBeingQus7B": "Y",
    "beaconWellBeingQus8": "3",
    "beaconWellBeingQus9": "0",
    "beaconWellBeingQus10": "1",
    "beaconWellBeingQus11": "2",
    "beaconWellBeingQus12": "3",
    "outcomeQuestion1": "4",
    "outcomeQuestion2": "1"
}
```

__NOTE__:
 - If the user is not found, then BWB registers a new user and returns the entire resource to SCC.
 - If a perfect match is found for the user using their connects user ID, then BWB will update their non-demographic and non-contact data and will return the updated resource to SCC.

__Response__

Status: `201 Created`

```json
{
    "id": "99743597-371f-40fa-b7a7-2d254df4044c",
    "mdLiveUserID": "642188195",
    "memberId": "2d254df4-1111-2222-3333-123456789123",
    "email": "mayank+13@fueled.com",
    "firstName": "beacon",
    "lastName": "health",
    "dateOfBirth": "1211025",
    "gender": "M",
    "addressLine1": "123 Est Road",
    "addressLine2": "777 Wst Lane",
    "city": "Sunrise",
    "stateCode": "FL",
    "zipCode": "33325",
    "phoneAreaCode": "912",
    "phoneCentralOfficeCode": "888",
    "phoneExchange": "8888",
    "parentCode": "ABC",
    "groupNumber": "123",
    "benefitPackage": "demo",
    "relationshipStatus": "1",
    "employmentStatus": "FT",
    "jobTitle": "TECH",
    "presentingProblemPrimary": "AX",
    "beaconWellBeingQus2": "ST",
    "beaconWellBeingQus3A": "1",
    "beaconWellBeingQus3B": "2",
    "beaconWellBeingQus5A": "3",
    "beaconWellBeingQus5B": "0",
    "beaconWellBeingQus7A": "N",
    "beaconWellBeingQus7B": "Y",
    "beaconWellBeingQus8": "3",
    "beaconWellBeingQus9": "0",
    "beaconWellBeingQus10": "1",
    "beaconWellBeingQus11": "2",
    "beaconWellBeingQus12": "3",
    "outcomeQuestion1": "4",
    "outcomeQuestion2": "1"
}
```

Or

__NOTE__:
 - If the user is found partly, then the mismatched data fields are returned to SCC as ValidationError.
 - The mismatch data returned to SCC includes connects member id, demographics, and contact data. It doesn't include non-demographic and non-contact data like user answers.
 - In this case, the API doesn't update/compare any non-demographic and non-contact data in this case.

__Response__

Status: `400 Bad Request`

```json
{
    "errors": [{
        "message": {
            "bwb_user_id": "99743597-371f-40fa-b7a7-2d254df4044c",
            "fields_differences": {
                "memberId": {
                    "bwb_value": "",
                    "scc_value": "2d254df4-1111-2222-3333-123456789123"
                },
                "email": {
                    "bwb_value": "shiva+01@fueled.com",
                    "scc_value": "mayank+13@fueled.com"
                },
                "phoneAreaCode": {
                    "bwb_value": "918",
                    "scc_value": "912"
                },
                "phoneCentralOfficeCode": {
                    "bwb_value": "777",
                    "scc_value": "888"
                },
                "phoneExchange": {
                    "bwb_value": "7777",
                    "scc_value": "8888"
                },
                "addressLine1": {
                    "bwb_value": "111/112",
                    "scc_value": "123 Est Road"
                },
                "addressLine2": {
                    "bwb_value": "Est Road",
                    "scc_value": "777 Wst Lane"
                },
                "city": {
                    "bwb_value": "NYC",
                    "scc_value": "Sunrise"
                },
                "statCode": {
                    "bwb_value": "KY",
                    "scc_value": "FL"
                },
                "zipCode": {
                    "bwb_value": "11111",
                    "scc_value": "33325"
                },
                "firstName": {
                    "bwb_value": "health",
                    "scc_value": "beacon"
                },
                "lastName": {
                    "bwb_value": "beacon",
                    "scc_value": "health"
                },
                "gender": {
                    "bwb_value": "U",
                    "scc_value": "M"
                },
                "dateOfBirth": {
                    "bwb_value": "1211026",
                    "scc_value": "1211025"
                }
            }
        }
    }],
    "error_type": "ValidationError"
}
```

## Update user

```
PATCH /api/users/:bwb_user_id/force-sync (authorization required)
```

__NOTE__:
- This API doesn't perform any validations on the data and force updates the resource with whatever is coming from SCC because it is the source of truth.
- `bwb_user_id` passed in the URL is BWB's user id, and not the Connects member id or MDLive user id.

__Request__
```json
{
    "memberId": "2d254df4-1111-2222-3333-123456789123",
    "email": "mayank+13@fueled.com",
    "addressLine1": "123 Est Road",
    "addressLine2": "777 Wst Lane",
    "city": "Sunrise",
    "stateCode": "FL",
    "zipCode": "33325",
    "phoneAreaCode": "912",
    "phoneCentralOfficeCode": "888",
    "phoneExchange": "8888",
    "parentCode": "ABC",
    "groupNumber": "123",
    "benefitPackage": "demo",
    "relationshipStatus": "1",
    "employmentStatus": "FT",
    "jobTitle": "TECH",
    "presentingProblemPrimary": "AX",
    "beaconWellBeingQus2": "ST",
    "beaconWellBeingQus3A": "1",
    "beaconWellBeingQus3B": "2",
    "beaconWellBeingQus5A": "3",
    "beaconWellBeingQus5B": "0",
    "beaconWellBeingQus7A": "N",
    "beaconWellBeingQus7B": "Y",
    "beaconWellBeingQus8": "3",
    "beaconWellBeingQus9": "0",
    "beaconWellBeingQus10": "1",
    "beaconWellBeingQus11": "2",
    "beaconWellBeingQus12": "3",
    "outcomeQuestion1": "4",
    "outcomeQuestion2": "1"
}
```

__NOTE__: In the response, the entire updated resource is returned.

__Response__

Status: `200 OK`
```json
{
    "id": "99743597-371f-40fa-b7a7-2d254df4044c",
    "mdLiveUserID": "642188195",
    "memberId": "2d254df4-1111-2222-3333-123456789123",
    "email": "mayank+13@fueled.com",
    "firstName": "beacon",
    "lastName": "health",
    "dateOfBirth": "1211025",
    "gender": "M",
    "addressLine1": "123 Est Road",
    "addressLine2": "777 Wst Lane",
    "city": "Sunrise",
    "stateCode": "FL",
    "zipCode": "33325",
    "phoneAreaCode": "912",
    "phoneCentralOfficeCode": "888",
    "phoneExchange": "8888",
    "parentCode": "ABC",
    "groupNumber": "123",
    "benefitPackage": "demo",
    "relationshipStatus": "1",
    "employmentStatus": "FT",
    "jobTitle": "TECH",
    "presentingProblemPrimary": "AX",
    "beaconWellBeingQus2": "ST",
    "beaconWellBeingQus3A": "1",
    "beaconWellBeingQus3B": "2",
    "beaconWellBeingQus5A": "3",
    "beaconWellBeingQus5B": "0",
    "beaconWellBeingQus7A": "N",
    "beaconWellBeingQus7B": "Y",
    "beaconWellBeingQus8": "3",
    "beaconWellBeingQus9": "0",
    "beaconWellBeingQus10": "1",
    "beaconWellBeingQus11": "2",
    "beaconWellBeingQus12": "3",
    "outcomeQuestion1": "4",
    "outcomeQuestion2": "1"
}
```

Or

__NOTE__: Fields `firstName`, `lastName`, `dateOfBirth`, and `gender` can't be updated on BWB using these APIs. The API will raise an error if these attributes are used for force updates.

__Response__

`Status: 403 Forbidden`

```json
{
    "errors": [{
        "message": "You don't have permission for this action."
    }],
    "error_type": "PermissionDenied"
}
```

Or

__NOTE__: If an invalid `bwb_user_id` is passed in the URL to update.

__Response__:

`Status: 404 Not Found`

```json
{
    "errors": [{
        "message": "User not found to update."
    }],
    "error_type": "NotFound"
}
```
