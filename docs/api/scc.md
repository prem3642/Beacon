# Service Care Connects System

## Authentication & Authorization

- The API uses JSON Web Tokens (JWT) for authorization
- HS-256 will be used to generate JWT
- Secret key is generated and shared by Fueled
- Payload will be:

```json
{"APP_NAME": "BeaconWellBeing", "exp": "1635494633"}
```

- Please generate a new token after every hour.

- The key generated should be provided in the `Authorization` HTTP header prefixed with `Token`.

## Sync user

__Parameters__

| Name                         | Allow Null | Allow Blank | Description                                                                                                                                 |
| ---------------------------- | ---------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| memberId                     | No         | No          | Connects member id of the user in secure care connects system.                                                                              |
| emailAddress                 | No         | No          | Email of the user.                                                                                                                          |
| firstName                    | No         | Yes         | First name of the user                                                                                                                      |
| lastName                     | No         | Yes         | Last name of the user                                                                                                                       |
| dateOfBirth                  | No         | No          | Birth date of the user. Format should be (CYYMMDD, e.i: 1211025 === Oct 25th, 2021)                                                         |
| gender                       | No         | No          | Gender of the user. Available options ('M', 'F', 'U')                                                                                       |
| addressLine1                 | No         | No          | Address line 1 of the user's mailing address                                                                                                |
| addressLine2                 | Yes        | Yes         | Address line 2 of the user's mailing address                                                                                                |
| addressCity                  | No         | No          | City of the user's mailing address                                                                                                          |
| addressStateCode             | No         | No          | State of the user's mailing address. Available options specified below                                                                      |
| addressZipCode               | No         | No          | Zipcode of the user's mailing address                                                                                                       |
| phoneNumberAreaCode          | No         | No          | Part of Phone Number - area code                                                                                                            |
| phoneNumberCentralOfficeCode | No         | No          | Part of Phone Number - central office code                                                                                                  |
| phoneNumberExchange          | No         | No          | Part of Phone Number - exchange                                                                                                             |
| parentCode                   | No         | No          | Parent code of the organization of the user                                                                                                 |
| groupNumber                  | No         | No          | Group number of the organization of the user                                                                                                |
| benefitPackage               | No         | No          | Benefit package of the organization of the user                                                                                             |
| relationshipStatus           | Yes        | No          | Relationship of the user to the primary account holder. Valid options are mentioned below                                                   |
| employmentStatus             | Yes        | No          | Employment status of the user. Available options are given below                                                                            |
| jobTitle                     | Yes        | No          | Job title of the user. Available options are given below                                                                                    |
| primaryPresentingProblem     | No         | No          | User's Chief Complaint for MDLive                                                                                                           |
| secondaryPresentingProblem   | Yes        | No          | User's another Chief Complaint for MDLive                                                                                                   |
| depressionScreenerQuestion3A | Yes        | No          | User's answer for - "Over the past 2 weeks, how often have you had little interest or pleasure in doing things?"                            |
| depressionScreenerQuestion3B | Yes        | No          | User's answer for - "Over the past 2 weeks, how often have you felt down, depressed, or hopeless?"                                          |
| anxietyScreenerQuestion5A    | Yes        | No          | User's answer for - "Over the past 2 weeks, how often have you felt nervous, anxious, or on edge?"                                          |
| anxietyScreenerQuestion5B    | Yes        | No          | User's answer for - "Over the past 2 weeks, how often have you felt you have not been able to stop or control worrying?"                    |
| substanceUseQuestion7A       | Yes        | No          | User's answer for - "When you drink or use drugs, do you find that you have difficulty stopping or keeping the limit you set for yourself?" |
| substanceUseQuestion7B       | Yes        | No          | User's answer for - "In the past year, have you felt or someone else expressed you should cut down on your drinking or drug use?"           |
| wellbeingDomainQuestion8     | Yes        | No          | User's answer for - "How would you say you're doing emotionally today?"                                                                     |
| wellbeingDomainQuestion9     | Yes        | No          | User's answer for - "How would you describe your current physical health?"                                                                  |
| wellbeingDomainQuestion10    | Yes        | No          | User's answer for - "I have people that support me in my life"                                                                              |
| wellbeingDomainQuestion11    | Yes        | No          | User's answer for - "I feel comfortable with the way I am managing my finances"                                                             |
| wellbeingDomainQuestion12    | Yes        | No          | User's answer for - "I have the tools to manage life challenges"                                                                            |
| outcomesESDQuestion1         | Yes        | No          | User's answer for - "During the past 30 days, how many days did you miss from your job because of your behavioral health issues?"           |
| outcomesESDQuestion2         | Yes        | No          | User's answer for - "During the past 30 days, how many days were you less productive at work than usual?"                                   |
| mdLiveMemberID               | Yes        | No          | MDLive user id of the user                                                                                                                  |

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
| DATA   | Data Not Provided                |

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

```
POST /api/users/sync (authorization required)
```

__NOTE__:

- All fields are required to be present in this API request body.
- The API first attempts to search for the user using connects member ID, mdlive ID, demographic data, and contact data.
- If the user is not found, BWB registers a new user.
- If the request data matches with one user exactly, then BWB updates the following fields:
    - relationshipStatus
    - employmentStatus
    - jobTitle
    - primaryPresentingProblem
    - secondaryPresentingProblem
    - depressionScreenerQuestion3A
    - depressionScreenerQuestion3B
    - anxietyScreenerQuestion5A
    - anxietyScreenerQuestion5B
    - substanceUseQuestion7A
    - substanceUseQuestion7B
    - wellbeingDomainQuestion8
    - wellbeingDomainQuestion9
    - wellbeingDomainQuestion10
    - wellbeingDomainQuestion11
    - wellbeingDomainQuestion12
    - outcomesESDQuestion1
    - outcomesESDQuestion2
- If the user is found but request data doesn't match, then error is returned with listed field differences.

__Request__
```json
{
    "memberId": "1234",
    "emailAddress": "shiva+05@fueled.com",
    "mdLiveMemberID": "444445",
    "firstName": "shiva2",
    "lastName": "health",
    "dateOfBirth": "0991203",
    "gender": "M",
    "addressLine1": "111 Est Road",
    "addressLine2": "222 Wst Lane",
    "addressCity": "Sunset",
    "addressStateCode": "FL",
    "addressZipCode": "11111",
    "phoneNumberAreaCode": "929",
    "phoneNumberCentralOfficeCode": "222",
    "phoneNumberExchange": "2222",
    "parentCode": "COT",
    "groupNumber": "123",
    "benefitPackage": "demo",
    "relationshipStatus": "1",
    "employmentStatus": "FT",
    "jobTitle": "TECH",
    "primaryPresentingProblem": "AX",
    "secondaryPresentingProblem": "ST",
    "depressionScreenerQuestion3A": "1",
    "depressionScreenerQuestion3B": "2",
    "anxietyScreenerQuestion5A": "3",
    "anxietyScreenerQuestion5B": "1",
    "substanceUseQuestion7A": "N",
    "substanceUseQuestion7B": "Y",
    "wellbeingDomainQuestion8": "3",
    "wellbeingDomainQuestion9": "1",
    "wellbeingDomainQuestion10": "1",
    "wellbeingDomainQuestion11": "2",
    "wellbeingDomainQuestion12": "3",
    "outcomesESDQuestion1": "10",
    "outcomesESDQuestion2": "0"
}
```

__Response__

Status: `200 OK`
```json
{"message": "User is synced successfully"}
```

__NOTE__:

- If user is found with discrepancies, then the error is returned.
- The error message mentions the values for various fields in both SCC and BWB systems.
- SCC system can use this message to find out which fields are mismatched, as BWB system is supposed to return all these fields even if only one field is mismatched as per [BEA-188](https://linear.app/beacon-health/issue/BEA-188/[10258]-return-values-even-for-those-that-match).
- BWB will return discrepancy values for the following fields in all uppercase. This is a short-term fix until SCC doesn't handle comparing these discrepancy values on their side.
  - First name
  - Last name
  - Address1
  - Address2
  - City

Status: `409 Conflict`
```json
{
  "errors": [
    {
      "message": {
        "memberId": {
          "bwb_value": "4mark",
          "scc_value": "4mark"
        },
        "firstName": {
          "bwb_value": "SHIVA4MARK",
          "scc_value": "SHIVA4MARK"
        },
        "lastName": {
          "bwb_value": "SAXENA",
          "scc_value": "SAXENA"
        },
        "gender": {
          "bwb_value": "M",
          "scc_value": "M"
        },
        "emailAddress": {
          "bwb_value": "shiva+4mark@fueled.com",
          "scc_value": "shiva+4mark@fueled.com"
        },
        "addressLine1": {
          "bwb_value": "742 ROSELVELT",
          "scc_value": "742 ROSELVELT"
        },
        "addressLine2": {
          "bwb_value": "MIDWAY TOWN",
          "scc_value": null
        },
        "addressCity": {
          "bwb_value": "SUNSET",
          "scc_value": "SUNSET"
        },
        "addressStateCode": {
          "bwb_value": "DE",
          "scc_value": "DE"
        },
        "addressZipCode": {
          "bwb_value": "10001",
          "scc_value": "10001"
        },
        "dateOfBirth": {
          "bwb_value": "1990-07-10",
          "scc_value": "1990-07-10"
        },
        "phoneNumberAreaCode": {
          "bwb_value": "912",
          "scc_value": "912"
        },
        "phoneNumberCentralOfficeCode": {
          "bwb_value": "777",
          "scc_value": "777"
        },
        "phoneNumberExchange": {
          "bwb_value": "7777",
          "scc_value": "7777"
        },
        "bwb_user_id": "c3493287-bab4-4433-be6e-15f9bd1e03c6"
      }
    }
  ],
  "error_type": "IntegrityError"
}
```

__NOTE__:

- If any data field fails validation, then validation error is returned.

Status: `400 Bad Request`
```json
{
  "errors": [
    {
      "message": "Invalid phone number!"
    }
  ],
  "error_type": "ValidationError"
}
```

## Force sync user

```
PUT /api/users/:bwb_user_id/force-sync (authorization required)
```

__NOTE__:

- All fields are optional to be present in the API request body.
- This API does basic validations on the data before force updating the resource with whatever is coming from SCC because it is the source of truth.
- `bwb_user_id` passed in the URL is BWB's user id, and not the Connects member id or MDLive user id.
- This API doesn't perform any user search based on the data provided in the body. Instead, it simply updates the user whose `bwb_user_id` is passed in the URL.
- Fields `parentCode`, `groupNumber`, `benefitPackage`, can't be updated in this API. These fields will be ignored if send in the request body.
- Fields `firstName`, `lastName`, `addresLine2` are allowed _blank_ only for the purpose of searching the user in API [POST /api/users/sync](#sync-user). However, blanks are not allowed to save in the BWB system for these fields.
- Fields `firstName`, `lastName`, `dateOfBirth`, and `gender` can't be updated on BWB using these APIs. These fields will be ignored if sent to update.

__Request__
```json
{
    "memberId": "2d254df4-1111-2222-3333-123456789123",
    "mdLiveMemberID": "123455",
    "emailAddress": "mayank+13@fueled.com",
    "addressLine1": "123 Est Road",
    "addressLine2": "777 Wst Lane",
    "addressCity": "Sunrise",
    "addressStateCode": "FL",
    "addressZipCode": "33325",
    "phoneNumberAreaCode": "912",
    "phoneNumberCentralOfficeCode": "888",
    "phoneNumberExchange": "8888",
    "relationshipStatus": "1",
    "employmentStatus": "FT",
    "jobTitle": "TECH",
    "primaryPresentingProblem": "AX",
    "secondaryPresentingProblem": "ST",
    "depressionScreenerQuestion3A": "1",
    "depressionScreenerQuestion3B": "2",
    "anxietyScreenerQuestion5A": "3",
    "anxietyScreenerQuestion5B": "0",
    "substanceUseQuestion7A": "N",
    "substanceUseQuestion7B": "Y",
    "wellbeingDomainQuestion8": "3",
    "wellbeingDomainQuestion9": "0",
    "wellbeingDomainQuestion10": "1",
    "wellbeingDomainQuestion11": "2",
    "wellbeingDomainQuestion12": "3",
    "outcomesESDQuestion1": "4",
    "outcomesESDQuestion2": "1"
}
```

__Response__

Status: `200 OK`
```json
{"message": "User is updated successfully"}
```
