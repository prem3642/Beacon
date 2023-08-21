## Beacon | Services on the Server

###### Prepared for Internal
###### Prepared by Sanyam
###### Updated on March 24, 2022

Three main services run on the Beacon server for any env.

I've detailed the steps below for the staging server. For any other server, just replace the `staging` with `dev`, `qa`, or `prod` for Dev/QA/Prod server respectively.

The first service is the NGINX which acts as a reverse proxy and also the layer where SSL decryption happens. It also helps in serving static resources.

The second service is the ASGI (ASGI stands for Asynchronous Server Gateway interface) which runs through Gunicorn running the actual Django instance. ASGI is an interface and sit in between the web server (NGINX) and the Django application.

The third service celery is used as an async task queue for all the long-running tasks in the system. There is also a `celerybeat` service that acts as a clock to trigger tasks at a pre-scheduled time using celery.

All these services use `systemd` for running so you can check the status of each service by using the following commands:

```
sudo systemctl status nginx.service
sudo systemctl status asgi-beacon-staging.service
sudo systemctl status celery-beacon-staging.service
sudo systemctl status celerybeat-beacon-staging.service
```

You can restart these services by using the command:

```
sudo systemctl restart nginx.service
sudo systemctl restart asgi-beacon-staging.service
sudo systemctl restart celery-beacon-staging.service
sudo systemctl restart celerybeat-beacon-staging.service
```

Instead of `status` or `restart` command with `systemctl`, you can also use `start` if you decide to `stop` a service instead of just doing a `restart`.

In most cases, the commands above will suffice to restart everything. In case there are any other issues, it has to be inspected. You can inspect logs of these services using the following commands:

```
tail -f /var/log/django/staging/beacon/asgi.log
tail -f /var/log/nginx/access.log
tail -f /var/log/celery/beacon-staging/celery.log
tail -f /var/log/celery/beacon-staging/celerybeat.log
```

`f` option, here is for streaming the output as it is written to the log file.

Remember that the logs won't be accessible as default user ubuntu on any of the servers. So, before inspecting logs, you'll either have to use `sudo` before the commands to output the log, or can update your privileges using `sudo su` and then execute commands to see the logs.
