Beacon Health
=============

__Version:__ 1.1.3

Beacon Wellbeing connects you with qualified experts who can help.

## Flow Documentation

To know about questionnaire flow history and current working flow go through the doc:
[questionnaire flow](docs/api/questionnaire_flow.md)

To know about message attachments flow go through the doc:
[message attachment flow](docs/api/message_attachments_flow.md)

To know about various services that run on the server and how to restart them or inspect logs: [services info](docs/backend/services_info.md)

## Getting up and running

Minimum requirements: **pip, python3, redis & [postgres][install-postgres]**, setup is tested on Mac OSX only.

```
brew install postgres python3
```

[install-postgres]: http://www.gotealeaf.com/blog/how-to-install-postgresql-on-a-mac

In your terminal, type or copy-paste the following:

    git clone git@github.com:Fueled/beacon-backend.git
    cd beacon-backend
    make install

Go grab a cup of coffee, we bake your hot development machine.

Useful commands:

- `make serve` - start [django server](http://localhost:8000/)
- `make deploy_docs` - deploy docs to server
- `make test` - run the test locally with ipdb
- `python manage.py load_initial_templates` - load initial questions and templates in database
- `python manage.py load_initial_homepage_categories` - load initial homepage nav categories and subcategories in database
- `python manage.py cognito_services_tests` - Run unit tests for cognito integration, run this on server after deployment

Checkout `Makefile` for all the options available and what/how they do it.


## Deployment

The deployment are managed via Github Actions and are deployment to different enviornment based
on the git branch. Mapping for the branches to envrionments are as follows:

| Branch  | ENV     | Url                                           |
| ------- | ------- | --------------------------------------------- |
| master  | dev     | https://backend.beacon-dev.fueled.engineering |
| qa      | qa      | https://backend.beacon-qa.fueled.engineering  |
| staging | staging | https://stgapp.mybeaconwellbeing.com          |
| prod    | prod    | https://app.mybeaconwellbeing.com             |

Check out detailed server setup instruction [here](docs/backend/server_config.md).


## Contributing

Golden Rule:

> Anything in **master** is always **deployable**.

Avoid working on `master` branch, create a new branch with meaningful name, send pull request asap. Be vocal!

Refer to [CONTRIBUTING.md][contributing]

[contributing]: http://github.com/Fueled/beacon-backend/tree/master/CONTRIBUTING.md
# Beacon
