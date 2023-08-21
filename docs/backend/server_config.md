# Server Architecture and configurations

## Concepts

Our overall stack looks like this:

```

              EC2
             ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐      RDS
┌─────────┐     ┌───────┐   ┌────────┐   ┌──────────┐      ┌────────────┐
│ Browser │──┼─▶│ NGINX │──▶│  ASGI  │──▶│  DJANGO  │──┬──▶│ POSTGRESQL │
└─────────┘     └───────┘   └────────┘   └─────┬────┘  │   └────────────┘
             │      │                          ▼     │ │
                    │       ┌────────┐    ┌────────┐   │   ┌────────────┐
             │      └──────▶│  Docs  │    │ REDIS  │ │ └──▶│     S3     │
                            └────────┘    └────────┘       └────────────┘
             │                                 │     │
                                    ┌────────┐ │
             │                      │ CELERY │◀┘     │
                                    └────────┘
             └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘
```

A web server faces the outside world. It can serve files (HTML, images, CSS, etc) directly from the file system. However, it can’t talk directly to Django applications; it needs something that will run the application, feed it requests from web clients (such as browsers) and return responses.

ASGI (ASGI stands for Asynchronous Server Gateway interface) which runs through Gunicorn running the actual Django instance. ASGI is an interface and sit in between the web server (NGINX) and the Django application. It creates a Unix socket, and serves responses to the web server via the asgi protocol.

## Third Party Services

Following third-party services are required in order to setup/deploy this project successfully.

### Amazon S3

Amazon Simple Storage Service ([Amazon S3]) is used to store the uploaded media files and static content. It is a scalable and cost-efficient storage solution.

After [signing up][s3-signup] for Amazon S3, [setup][s3-iam-setup] an IAM user with access to a S3 bucket, you'll need `BUCKET_NAME`, and `AWS_ACCESS_ID` & `AWS_ACCESS_SECRET` of IAM user to setup the project.

[Amazon S3]: http://aws.amazon.com/s3/
[s3-signup]: http://docs.aws.amazon.com/AmazonS3/latest/gsg/SigningUpforS3.html
[s3-iam-setup]: https://rbgeek.wordpress.com/2014/07/18/amazon-iam-user-creation-for-single-s3-bucket-access/

Note:

- IAM user must have permission to list, update, create objects in S3.

## Deploying Project

The deployment are managed via travis, but for the first time you'll need to set the configuration values on each of the server. Read this only, if you need to deploy for the first time.

### Protecting staging site with Basic Authentication

The project include [django-auth-wall](https://github.com/theskumar/django-auth-wall) which can be used to protect the site with Basic authentication during development. To enable the protection, add the following two variables in system environment or in django settings.

```
AUTH_WALL_USERNAME=<your_basic_auth_username_here>
AUTH_WALL_PASSWORD=<your_basic_auth_password_here>
AUTH_WALL_REALM=<your_basic_auth_message(optional)>
```

### AWS/EC2

For deploying on aws you need to configure all the addons provided and use python-dotenv to store and read enironment variables.

Add the following to your `~/.ssh/config` file.

```
Host backend.beacon-dev.fueled.engineering
    User ubuntu
    ForwardAgent yes
    identityfile <PATH_OF_SERVER_PRIVATE_KEY_HERE>

Host backend.beacon-qa.fueled.engineering
    User ubuntu
    ForwardAgent yes
    identityfile <PATH_OF_SERVER_PRIVATE_KEY_HERE>

Host app.mybeaconwellbeing.com
    hostname 18.253.135.190
    user ubuntu
    identityfile <PATH_OF_SERVER_PRIVATE_KEY_HERE>

Host stgapp.mybeaconwellbeing.com
    hostname 18.253.34.29
    user ubuntu
    identityfile <PATH_OF_SERVER_PRIVATE_KEY_HERE>
```

Now you can run the ansible script to setup the machine.

    ENV=prod make configure

This will setup os dependencies, services like supervisor, nginx and fetch our code from Github. Our production environment requires
some environment variables in `.env`. So you can write a file `prod.env` locally and upload it to server with

    scp prod.env beacon.com:/home/ubuntu/beacon-backend/.env

Now that you have `.env` setup, you can deploy your code and start services:

    ENV=prod make deploy
