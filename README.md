# Offsite-test

### Getting started
Requirements:
- Python 3.8
- Docker & docker-compose

Navigate to the project directory and install the required packages:

`pip install -r requirements.txt`

The answers for each question are put into separate folders for clarity.

See below sections to find the respective programs for each question.


### Q1 SQL
**Docker and docker-compose are required to run.**

Navigate to the directory:

`offsite-test\Q1`

Docker compose a postgres container by running:

`docker-compose up`

Then run sql.py to display the query and result:
```
SQL query:

        WITH USER_WHO_INSTALLED_APP_ON_DATE AS ( 
            SELECT DISTINCT
                piwik_track.uid
            FROM
                piwik_track
            WHERE
                DATE(piwik_track.time) = to_date('2017-04-01', 'YYYY-MM-DD') 
                AND piwik_track.event_name = 'FIRST_INSTALL'
        ), USER_WHO_USED_APP_AT_LEAST_ONCE_IN_TIME_RANGE AS (
            SELECT DISTINCT
                piwik_track.uid
            FROM
                piwik_track
            WHERE
                piwik_track.time BETWEEN to_date('2017-04-02', 'YYYY-MM-DD') 
                AND to_date('2017-04-08', 'YYYY-MM-DD')
        )
        SELECT
            COUNT(uid)
        FROM
            USER_WHO_INSTALLED_APP_ON_DATE
        INNER JOIN
            USER_WHO_USED_APP_AT_LEAST_ONCE_IN_TIME_RANGE
        USING 
            (uid)
    
Table name: piwik_track
Number of dummy records: 10000
Number of dummy users: 1000
333

Process finished with exit code 0

```