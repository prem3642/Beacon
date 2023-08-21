{% extends "email/base_email.html" %}
{% load i18n %}
{% load resolve_frontend_url from urls_extra %}

{# ======== Subject of email #}
{% block subject %}[beacon] Error: error in sending appointment email for user{% endblock %}

{% block body %}
{# ======== plain text version of email body #}
{% blocktrans %}Error in sending F2F appointment email to user{% endblocktrans %}

{% trans "Error details" %}:

{% trans "Error" %}: {{ exception }}
{% trans "User Id" %}: {{ user_id }}
{% trans "Inquiry ID" %}: {{ inquiry_id }}
{% trans "Appointment ID" %}: {{ appointment_id }}
{% endblock body %}


{% block content %}
{# ======== html version of email body #}
<p>{% blocktrans %}Error in sending F2F appointment data to BWB server{% endblocktrans %}</p>

<p>{% trans "Error details" %}:</p>

<ul>
  <li>{% trans "Error" %}: {{ exception }}</li>
  <li>{% trans "User Id" %}: {{ user_id }}</li>
  <li>{% trans "Inquiry ID" %}: {{ inquiry_id }}</li>
  <li>{% trans "Appointment ID" %}: {{ appointment_id }}</li>
</ul>
{% endblock content %}
