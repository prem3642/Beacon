{% extends "email/base_email.html" %}
{% load i18n %}
{% load resolve_frontend_url from urls_extra %}

{# ======== Subject of email #}
{% block subject %}[beacon] Error: error in sending appointment data{% endblock %}

{% block body %}
{# ======== plain text version of email body #}
{% blocktrans %}Error in sending F2F appointment data to BWB server{% endblocktrans %}

{% trans "Error details" %}:

{% trans "Error" %}: {{ exception }}
{% trans "Organisation Username" %}: {{ organisation_username }}
{% trans "Appointment ID" %}: {{ appointment_id }}

{% if appointment_id %}
{% trans "Error" %}: {{ exception }}
{% trans "Organisation Username" %}: {{ organisation_username }}
{% trans "Appointment ID" %}: {{ appointment_id }}
{% endif %}

{% if appointment_ids %}
{% trans "Failed Appointment IDs" %}:
{% for appointment_id in appointment_ids %}
  - {{ appointment_id }}
{% endfor %}
{% endif %}
{% endblock body %}


{% block content %}
{# ======== html version of email body #}
<p>{% blocktrans %}Error in sending F2F appointment data to BWB server{% endblocktrans %}</p>

<p>{% trans "Error details" %}:</p>

{% if appointment_id %}
<ul>
  <li>{% trans "Error" %}: {{ exception }}</li>
  <li>{% trans "Organisation Username" %}: {{ organisation_username }}</li>
  <li>{% trans "Appointment ID" %}: {{ appointment_id }}</li>
</ul>
{% endif %}

{% if appointment_ids %}
<p>{% trans "Failed Appointment IDs" %}:</p>
<ul>
{% for appointment_id in appointment_ids %}
  <li>{{ appointment_id }}</li>
{% endfor %}
</ul>
{% endif %}
{% endblock content %}
