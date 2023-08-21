{% extends "email/base_email.html" %}
{% load i18n %}
{% load resolve_frontend_url_for_organisation from urls_extra %}
{% load get_absolute_url from urls_extra %}

{# ======== Subject of email #}
{% block subject %}Welcome to {{ organisation.program_name | default:"Carelon Wellbeing" }}!{% endblock %}

{% block body %}
{# ======== plain text version of email body #}
{% blocktrans %}Hello {{ first_name }},{% endblocktrans %}

{% trans "Welcome to " %}{{ organisation.program_name | default:"Carelon Wellbeing" }}!
{% trans "We've created a new online account just for you. Here is some information to help you get started with your online resources." %}

{% trans "First, log in to verify your new account." %}

{% trans "Log in here:" %} {% resolve_frontend_url_for_organisation "login" organisation=organisation %}

{% blocktrans %}Password: {{ password }}{% endblocktrans %}

  - {% blocktrans %}Looking for a new verification code? Use the "Resend" option to send a new email from your login page. Your code will be sent in a separate email.{% endblocktrans %}
  - Need to change your password? Use the "Forgot" option at login, or click here: {% resolve_frontend_url_for_organisation 'recover-password' organisation=organisation %}

Explore the benefits and resources available to you online, at your convenience.

  - {% blocktrans %}Find expert advice and guidance to help you navigate life events and reach personal goals.{% endblocktrans %}
  - {% blocktrans %}Browse available video or phone sessions with licensed counselors, or request an appointment that works for your schedule.{% endblocktrans %}
  - {% blocktrans %}Request a list of counselors in your area who offer in-person appointments.{% endblocktrans %}
  - {% blocktrans %}Learn more about the benefits and resources available to you.{% endblocktrans %}

{% blocktrans %}For any questions regarding your benefits or accessing your account, please call us {% endblocktrans %}{% if organisation.phone %}at {{ organisation.phone }}{% endif %} {% blocktrans %}for assistance.{% endblocktrans %}

Best of health,
{{ organisation.program_name | default:"Carelon Wellbeing" }} Team

{% endblock body %}


{% block logo %}
{% endblock logo %}

{% block content %}
{# ======== html version of email body #}

<p>{% blocktrans %}Hello {{ first_name }},{% endblocktrans %}</p>

<p><strong>{% trans "Welcome to" %} {{ organisation.program_name | default:"Carelon Wellbeing" }}!</strong>
{% trans "We've created a new online account just for you. Here is some information to help you get started with your online resources." %}</p>

<p><strong>{% trans "First, log in to verify your new account." %}</strong></p>

<p>&nbsp;&nbsp;&nbsp;&nbsp;{% trans "Log in here:" %} <a href="{% resolve_frontend_url_for_organisation "login" organisation=organisation %}">{% resolve_frontend_url_for_organisation "login" organisation=organisation %}</a><br />
{% blocktrans %}&nbsp;&nbsp;&nbsp;&nbsp;Password: {{ password }}{% endblocktrans %}</p>

<ul>
  <li><em><small>{% blocktrans %}Looking for a new verification code? Use the "Resend" option to send a new email from your login page. Your code will be sent in a separate email.{% endblocktrans %}</small></em></li>
  <li><em><small>Need to change your password? Use the "Forgot" option at login, or click <a href="{% resolve_frontend_url_for_organisation 'recover-password' organisation=organisation %}">here</a></em></small></li>
</ul>

<p><strong>Explore the benefits and resources available to you online, at your convenience.</strong></p>

<ul>
  <li>{% blocktrans %}Find expert advice and guidance to help you navigate life events and reach personal goals.{% endblocktrans %}</li>
  <li>{% blocktrans %}Browse available video or phone sessions with licensed counselors, or request an appointment that works for your schedule.{% endblocktrans %}</li>
  <li>{% blocktrans %}Request a list of counselors in your area who offer in-person appointments.{% endblocktrans %}</li>
  <li>{% blocktrans %}Learn more about the benefits and resources available to you.{% endblocktrans %}</li>
</ul>
<p><em>{% blocktrans %}For any questions regarding your benefits or accessing your account, please call us {% endblocktrans %}{% if organisation.phone %}at {{ organisation.phone }}{% endif %} {% blocktrans %}for assistance.{% endblocktrans %}</em></p>
{% endblock content %}
{% block valediction %}
<p>Best of health,<br />
<strong>{{ organisation.program_name | default:"Carelon Wellbeing" }} Team</strong></p>
{% endblock valediction %}
