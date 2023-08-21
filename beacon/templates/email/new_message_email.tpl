{% extends "email/base_email_new.html" %}
{% load i18n %}
{% load resolve_frontend_url_for_organisation from urls_extra %}

{# ======== Subject of email #}
{% block subject_content %}{% blocktrans %}{{ program_name }}: You have received a message{% endblocktrans %}{% endblock subject_content %}

{% block body_content %}
{# ======== plain text version of email body #}

{% blocktrans %}Dear {{ first_name }},{% endblocktrans %}

{% blocktrans %}You have been sent an important message in your account. Please login{% endblocktrans %} {% resolve_frontend_url_for_organisation 'messages-inbox' organisation=organisation %} {% blocktrans %}to view your messages.{% endblocktrans %}

{% trans "Thanks," %}

{{ program_name }}
{% endblock body_content %}


{% block title %}
{{ program_name }}
{% endblock title %}

{% block content %}
{# ======== html version of email body #}

<p>{% blocktrans %}Dear {{ first_name }},{% endblocktrans %}</p>

<p>{% blocktrans %}You have been sent an important message in your account. Please login{% endblocktrans %} <a href="{% resolve_frontend_url_for_organisation 'messages-inbox' organisation=organisation %}">here</a> {% blocktrans %}to view your messages.{% endblocktrans %}</p>

<p>{% trans "Thanks," %}</p>

<p>{{ program_name }}</p>
{% endblock content %}
