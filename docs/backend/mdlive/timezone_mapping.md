# MDLive's Timezone mapping

MDLive API maps a few numeric IDs to timezone name. Their API states these numbers in the documentation but the description is not mentioned in the docs.

Fueled team reached out to Axel from MDLive and were provided the following mapping:

| time_zone_id | Time Zone Name | Time Zone Description        |
| ------------ | -------------- | ---------------------------- |
| 1            | EST            | Eastern Standard Time (EST)  |
| 2            | CST            | Central Standard Time (CST)  |
| 3            | MST            | Mountain Standard Time (MST) |
| 4            | PST            | Pacific Standard Time (PST)  |
| 5            | AKST           | Alaska Standard Time (AKST)  |
| 6            | HST            | Hawaii Standard Time (HST)   |
| 7            | AMS            | American Samoa Time (AST)    |
| 8            | MIT            | Marshall Islands Time        |
| 9            | GST            | Guam                         |
| 10           | PAT            | Palau                        |
| 11           | AST            | Atlantic Standard Time (AST) |
| 12           | AZT            | Arizona Time (AZT)           |


This mapping is being used to map timezone name to ID to sync the timezone with MDLive when the user is first registered. Refer for more details: https://linear.app/beacon-health/issue/BEA-172/add-timezone-to-register-endpoint-model
