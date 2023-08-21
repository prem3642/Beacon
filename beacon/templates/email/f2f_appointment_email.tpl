{% extends "email/base_email_new.html" %}
{% load i18n %}

{# ======== Subject of email #}
{% block subject_content %}{% blocktrans %}You’ve successfully submitted your request{% endblocktrans %}{% endblock subject_content %}

{% block body_content %}
{# ======== plain text version of email body #}

{% blocktrans %}Hello {{ first_name }},{% endblocktrans %}

{% blocktrans %}We'll start looking for counselors right away, and we will be in touch with you soon. If you still have not heard back after 48 hours, please give us a call at{% endblocktrans %} {{ organisation.phone }}{% if inquiry_id %},
 quoting your Inquiry ID, which is {{ inquiry_id }}{% endif %}.

{% trans "In good health," %}

{{ organisation.program_name }}
{% endblock body_content %}


{% block title %}
{{ organisation.program_name }}
{% endblock title %}

{% block content %}
{# ======== html version of email body #}

<p>{% blocktrans %}Hello {{ first_name }},{% endblocktrans %}</p>

<p>{% blocktrans %}We'll start looking for counselors right away, and we will be in touch with you soon. If you still have not heard back after 48 hours, please give us a call at{% endblocktrans %} {{ organisation.phone }}{% if inquiry_id %},
 quoting your Inquiry ID, which is <strong>{{ inquiry_id }}</strong>{% endif %}.</p>

<p>{% trans "In good health," %}</p>

<p>{{ organisation.program_name }}</p>
{% endblock content %}
