# -*- coding: utf-8 -*-
# Third Party Stuff
from django.core.management.base import BaseCommand

# beacon Stuff
from beacon.answers import constants
from beacon.questionnaire.models import (
    IntakeQuestionTemplate,
    Option,
    Question,
    TemplateQuestionMapping,
)
from beacon.users.choices import STATE_CHOICES


def create_f2f_counselor_notes():
    f2f_counselor_notes_question = Question.objects.create(
        kind=Question.TEXT_BOX,
        is_required=False,
        text="Is there anything else we should know?",
        subheading="For example, do you have a preferred language, counselor name, accessibility requirement, etc.?",
        max_length=1000,
        next_question=None,
        user_response_attribute=None,
        user_appointment_attribute=constants.F2F_COUNSELOR_NOTES,
    )
    return f2f_counselor_notes_question


def create_f2f_okay_to_leave_voicemail_question(next_question):
    f2f_okay_to_leave_voicemail_options = [(True, "Yes"), (False, "No")]
    f2f_okay_to_leave_voicemail_question = Question.objects.create(
        kind=Question.RADIO,
        is_required=True,
        text="Your privacy is important to us. If you are not available, is it okay to leave a voicemail?",
        next_question=next_question,
        user_response_attribute=None,
        user_appointment_attribute=constants.F2F_OKAY_TO_LEAVE_VOICEMAIL,
    )
    for value, text in f2f_okay_to_leave_voicemail_options:
        Option.objects.create(
            text=text,
            text_mapped_value=value,
            question=f2f_okay_to_leave_voicemail_question,
        )

    return f2f_okay_to_leave_voicemail_question


def create_f2f_preferred_contact_question(counselor_notes_question, voicemail_question):
    f2f_preferred_contact_question = Question.objects.create(
        kind=Question.RADIO,
        text="How would you prefer we contact you with recommended counselors?",
        placeholder="(We'll ask for your contact info later)",
        next_question=None,
        user_response_attribute=None,
        user_appointment_attribute=constants.F2F_PREFERRED_CONTACT,
    )

    email_option = Option.objects.create(
        text="Email",
        text_mapped_value=constants.F2F_EMAIL,
        question=f2f_preferred_contact_question,
        next_question=counselor_notes_question,
    )

    phone_option = Option.objects.create(
        text="Phone",
        text_mapped_value=constants.F2F_PHONE,
        question=f2f_preferred_contact_question,
        next_question=voicemail_question,
    )
    return f2f_preferred_contact_question, email_option, phone_option


def create_f2f_address_question(next_question):
    f2f_address_question = Question.objects.create(
        kind=Question.MULTIPLE_QUESTIONS,
        text="Enter your address",
        next_question=next_question,
        user_response_attribute=None,
        user_appointment_attribute=None,
    )
    # Creating in reverse order as BE api returns questions in descending order of creation time
    Question.objects.create(
        kind=Question.REGEX,
        text="Zip",
        placeholder="Zip",
        max_length=10,
        min_length=5,
        next_question=None,
        user_response_attribute=None,
        user_appointment_attribute=constants.F2F_ZIP,
        leader_question=f2f_address_question,
        regex=r"^\d{5}(?:-\d{4})?$",
        regex_error_message="Enter a zip code in the format XXXXX or XXXXX-XXXX.",
    )
    f2f_state_question = Question.objects.create(
        kind=Question.DROPDOWN,
        text="State",
        placeholder="State",
        max_length=3,
        next_question=None,
        user_response_attribute=None,
        user_appointment_attribute=constants.F2F_STATE,
        leader_question=f2f_address_question,
    )
    Question.objects.create(
        kind=Question.TEXT,
        text="City",
        placeholder="City",
        max_length=35,
        next_question=None,
        user_response_attribute=None,
        user_appointment_attribute=constants.F2F_CITY,
        leader_question=f2f_address_question,
    )
    Question.objects.create(
        kind=Question.TEXT,
        text="Address Line Two",
        placeholder="Address Line Two",
        is_required=False,
        max_length=50,
        next_question=None,
        user_response_attribute=None,
        user_appointment_attribute=constants.F2F_ADDRESS2,
        leader_question=f2f_address_question,
    )
    Question.objects.create(
        kind=Question.TEXT,
        text="Address Line One",
        placeholder="Address Line One",
        max_length=50,
        next_question=None,
        user_response_attribute=None,
        user_appointment_attribute=constants.F2F_ADDRESS1,
        leader_question=f2f_address_question,
    )
    for value, text in STATE_CHOICES:
        Option.objects.create(
            text=text, text_mapped_value=value, question=f2f_state_question
        )

    return f2f_address_question


def create_counselor_search_address_question(next_question, default_question):
    f2f_counselor_search_address_question = Question.objects.create(
        kind=Question.RADIO,
        text="We will find counselors as close to your location as possible. "
        "Please let us know where to start our search.",
        next_question=default_question,
        user_response_attribute=None,
        user_appointment_attribute=constants.F2F_COUNSELOR_SEARCH_ADDRESS,
    )

    home_address_option = Option.objects.create(
        text="Search near my home address",
        text_mapped_value=constants.F2F_HOME_ADDRESS,
        question=f2f_counselor_search_address_question,
        next_question=default_question,
    )
    other_address_option = Option.objects.create(
        text="Search near a different address (e.g. work)",
        text_mapped_value=constants.F2F_OTHER_ADDRESS,
        question=f2f_counselor_search_address_question,
        next_question=next_question,
    )
    return (
        f2f_counselor_search_address_question,
        home_address_option,
        other_address_option,
    )


def create_comfortable_language_question(next_question):
    f2f_comfortable_language_option = [
        ("English", "English"),
        ("German", "German"),
        ("Spanish", "Spanish"),
        ("French", "French"),
        ("Italian", "Italian"),
        ("Kashmiri", "Kashmiri"),
        ("Haitian Creole", "Haitian Creole"),
        ("Polish", "Polish"),
        ("Portuguese", "Portuguese"),
    ]

    f2f_comfortable_language_question = Question.objects.create(
        kind=Question.DROPDOWN,
        text="What language do you feel most comfortable speaking?",
        next_question=next_question,
        user_response_attribute=None,
        user_appointment_attribute=constants.F2F_COMFORTABLE_LANGUAGE,
    )

    for value, text in f2f_comfortable_language_option:
        Option.objects.create(
            text=text,
            text_mapped_value=value,
            question=f2f_comfortable_language_question,
        )

    return f2f_comfortable_language_question


def create_gender_preference_question(next_question):
    f2f_gender_preference_option = [
        ("None", "I don't have a preference"),
        ("M", "Male"),
        ("F", "Female"),
    ]

    f2f_gender_preference_question = Question.objects.create(
        kind=Question.RADIO,
        text="Do you have a gender preference for your counselor?",
        next_question=next_question,
        user_response_attribute=None,
        user_appointment_attribute=constants.F2F_GENDER_PREFERENCE,
    )

    for value, text in f2f_gender_preference_option:
        Option.objects.create(
            text=text, text_mapped_value=value, question=f2f_gender_preference_question
        )
    return f2f_gender_preference_question


def create_f2f_confirm_question(next_question):
    f2f_confirm_options = [
        (
            "video_or_phone",
            "Timeliness is most important to me. I want to see a counselor as "
            "soon as possible, and I’m okay with talking to someone "
            "face-to-face through video or on the phone.",
            None,
        ),
        (
            "face_to_face",
            "I prefer to travel to a safe space where I can talk to a counselor "
            "in person.",
            next_question,
        ),
    ]

    f2f_confirm_question = Question.objects.create(
        kind=Question.RADIO,
        text="Between these two factors, which is more important to you",
        next_question=None,
        user_response_attribute=None,
        user_appointment_attribute=constants.F2F_CONFIRM,
    )

    for value, text, next_question in f2f_confirm_options:
        Option.objects.create(
            text=text,
            text_mapped_value=value,
            question=f2f_confirm_question,
            next_question=next_question,
        )
    return f2f_confirm_question


def create_appointment_method_question(next_question):
    appointment_method_question = Question.objects.create(
        kind=Question.DROPDOWN,
        text="How would you like to talk to your counselor?",
        next_question=None,
        user_response_attribute=None,
        user_appointment_attribute=constants.APPOINTMENT_METHOD,
        is_appointment_start=True,
    )

    video_option = Option.objects.create(
        text="Video", text_mapped_value="video", question=appointment_method_question
    )
    phone_option = Option.objects.create(
        text="Phone", text_mapped_value="phone", question=appointment_method_question
    )
    face_to_face_option = Option.objects.create(
        text="Face To Face",
        text_mapped_value="face_to_face",
        question=appointment_method_question,
        next_question=next_question,
    )
    return appointment_method_question, face_to_face_option, phone_option, video_option


def create_number_of_days_missed_work_question(next_question=None):
    number_of_days_missed_work_question = Question.objects.create(
        kind=Question.NUMBER,
        text="During the past 30 days, how many days did you miss from your job "
        "because of your behavioral health issues?",
        min_length=0,
        max_length=30,
        user_response_attribute=constants.NUMBER_OF_DAYS_MISSED_WORK,
        next_question=next_question,
    )
    return number_of_days_missed_work_question


def create_number_of_days_less_productive_question(next_question):
    number_of_days_less_productive_question = Question.objects.create(
        kind=Question.NUMBER,
        text="During the past 30 days, how many days were you less productive at work than usual?",
        min_length=0,
        max_length=30,
        next_question=next_question,
        user_response_attribute=constants.NUMBER_OF_DAYS_LESS_PRODUCTIVE,
    )
    return number_of_days_less_productive_question


def create_resources_to_manage_question(next_question):
    resources_to_manage_options = [
        (5, "Very true"),
        (4, "Often true"),
        (3, "Sometimes true"),
        (2, "Rarely true"),
        (1, "Not true at all"),
    ]

    resources_to_manage_question = Question.objects.create(
        kind=Question.RADIO,
        text="I have the tools to manage life challenges",
        next_question=next_question,
        user_response_attribute=constants.RESOURCES_TO_MANAGE,
    )

    for value, text in resources_to_manage_options:
        Option.objects.create(
            text=text, text_mapped_value=value, question=resources_to_manage_question
        )
    return resources_to_manage_question


def create_people_support_question(next_question):
    resources_to_manage_options = [
        (5, "Very true"),
        (4, "Often true"),
        (3, "Sometimes true"),
        (2, "Rarely true"),
        (1, "Not true at all"),
    ]

    people_support_question = Question.objects.create(
        kind=Question.RADIO,
        text="I have people that support me in my life",
        next_question=next_question,
        user_response_attribute=constants.PEOPLE_SUPPORT,
    )

    for value, text in resources_to_manage_options:
        Option.objects.create(
            text=text, text_mapped_value=value, question=people_support_question
        )
    return people_support_question


def create_comfortable_in_managing_finances_question(next_question):
    resources_to_manage_options = [
        (5, "Very true"),
        (4, "Often true"),
        (3, "Sometimes true"),
        (2, "Rarely true"),
        (1, "Not true at all"),
    ]

    comfortable_in_managing_finances_question = Question.objects.create(
        kind=Question.RADIO,
        text="I feel comfortable with the way I am managing my finances",
        next_question=next_question,
        user_response_attribute=constants.COMFORTABLE_IN_MANAGING_FINANCES,
    )

    for value, text in resources_to_manage_options:
        Option.objects.create(
            text=text,
            text_mapped_value=value,
            question=comfortable_in_managing_finances_question,
        )
    return comfortable_in_managing_finances_question


def create_how_physical_health_question(next_question):
    how_physical_health_options = [
        (5, "Excellent"),
        (4, "Good"),
        (3, "Average"),
        (2, "Poor"),
        (1, "Very Poor"),
    ]

    how_physical_health_question = Question.objects.create(
        kind=Question.RADIO,
        text="How would you describe your current physical health?",
        next_question=next_question,
        user_response_attribute=constants.HOW_PHYSICAL_HEALTH,
    )

    for value, text in how_physical_health_options:
        Option.objects.create(
            text=text, text_mapped_value=value, question=how_physical_health_question
        )
    return how_physical_health_question


def create_how_emotionally_doing_question(next_question):
    how_physical_health_options = [
        (5, "Excellent"),
        (4, "Good"),
        (3, "Average"),
        (2, "Poor"),
        (1, "Very Poor"),
    ]

    how_emotionally_doing_question = Question.objects.create(
        kind=Question.RADIO,
        text="How would you say you're doing emotionally today?",
        next_question=next_question,
        user_response_attribute=constants.HOW_EMOTIONALLY_DOING,
    )

    for value, text in how_physical_health_options:
        Option.objects.create(
            text=text, text_mapped_value=value, question=how_emotionally_doing_question
        )
    return how_emotionally_doing_question


def create_difficulty_in_keeping_drinking_linking_question(next_question):
    difficulty_in_keeping_drinking_limit_question = Question.objects.create(
        kind=Question.YES_NO,
        text="When you drink or use drugs, do you find that you have difficulty stopping or "
        "keeping the limit you set for yourself?",
        yes_button_text="Yes",
        no_button_text="No",
        show_safety_screen=True,
        next_question=next_question,
        user_response_attribute=constants.DIFFICULTY_IN_KEEPING_DRINKING_LIMIT,
    )
    return difficulty_in_keeping_drinking_limit_question


def create_felt_cut_down_drinking_question(next_question):
    felt_cut_down_drinking_question = Question.objects.create(
        kind=Question.YES_NO,
        text="In the past year, have you felt or someone else expressed you "
        "should cut down on your drinking or drug use?",
        yes_button_text="Yes",
        no_button_text="No",
        show_safety_screen=True,
        next_question=next_question,
        user_response_attribute=constants.FELT_CUT_DOWN_DRINKING,
    )
    return felt_cut_down_drinking_question


def create_how_often_worry_question(next_question):
    how_often_worry_options = [
        (4, "Not at all"),
        (3, "Several Days"),
        (2, "More than half the days"),
        (1, "Nearly every day"),
    ]

    how_often_worry_question = Question.objects.create(
        kind=Question.RADIO,
        text="Over the past 2 weeks, how often have you felt you have not been able to stop or control worrying?",
        next_question=next_question,
        user_response_attribute=constants.HOW_OFTEN_WORRY,
    )

    for value, text in how_often_worry_options:
        Option.objects.create(
            text=text, text_mapped_value=value, question=how_often_worry_question
        )
    return how_often_worry_question


def create_how_often_nervous_question(next_question):
    how_often_nervous_options = [
        (4, "Not at all"),
        (3, "Several Days"),
        (2, "More than half the days"),
        (1, "Nearly every day"),
    ]

    how_often_nervous_question = Question.objects.create(
        kind=Question.RADIO,
        text="Over the past 2 weeks, how often have you felt nervous, anxious or on edge?",
        next_question=next_question,
        user_response_attribute=constants.HOW_OFTEN_NERVOUS,
    )

    for value, text in how_often_nervous_options:
        Option.objects.create(
            text=text, text_mapped_value=value, question=how_often_nervous_question
        )
    return how_often_nervous_question


def create_how_often_depressed_question(next_question):
    how_often_depressed_options = [
        (4, "Not at all"),
        (3, "Several Days"),
        (2, "More than half the days"),
        (1, "Nearly every day"),
    ]

    how_often_depressed_question = Question.objects.create(
        kind=Question.RADIO,
        text="Over the past 2 weeks, how often have you felt down, depressed, or hopeless?",
        next_question=next_question,
        user_response_attribute=constants.HOW_OFTEN_DEPRESSED,
    )

    for value, text in how_often_depressed_options:
        Option.objects.create(
            text=text, text_mapped_value=value, question=how_often_depressed_question
        )
    return how_often_depressed_question


def create_how_often_less_interest_in_things_question(next_question):
    how_often_less_interest_in_things_options = [
        (4, "Not at all"),
        (3, "Several Days"),
        (2, "More than half the days"),
        (1, "Nearly every day"),
    ]

    how_often_less_interest_in_things_question = Question.objects.create(
        kind=Question.RADIO,
        text="Over the past 2 weeks, how often have you had little interest or pleasure in doing things?",
        next_question=next_question,
        user_response_attribute=constants.HOW_OFTEN_LESS_INTEREST_IN_THINGS,
    )

    for value, text in how_often_less_interest_in_things_options:
        Option.objects.create(
            text=text,
            text_mapped_value=value,
            question=how_often_less_interest_in_things_question,
        )
    return how_often_less_interest_in_things_question


def create_employee_details_question():
    employee_details_question = Question.objects.create(
        kind=Question.MULTIPLE_QUESTIONS,
        text="Please confirm the following details for the employee in question",
        next_question=None,
        user_response_attribute=None,
        user_appointment_attribute=None,
    )
    # Creating in reverse order as BE api returns questions in descending order of creation time
    Question.objects.create(
        kind=Question.ORGANISATION,
        text="Location",
        placeholder="Location",
        max_length=36,  # This is going to be uuid of organisation
        min_length=32,
        next_question=None,
        user_response_attribute=constants.EMPLOYEE_ORGANISATION_ID,
        user_appointment_attribute=None,
        leader_question=employee_details_question,
    )
    Question.objects.create(
        kind=Question.DATE,
        text="Employee DOB",
        placeholder="Employee DOB",
        next_question=None,
        user_response_attribute=constants.EMPLOYEE_BIRTH_DATE,
        user_appointment_attribute=None,
        leader_question=employee_details_question,
    )
    Question.objects.create(
        kind=Question.TEXT,
        text="Employee Name",
        placeholder="Employee Name",
        max_length=50,
        min_length=2,
        next_question=None,
        user_response_attribute=constants.EMPLOYEE_NAME,
        user_appointment_attribute=None,
        leader_question=employee_details_question,
    )

    return employee_details_question


def create_relationship_with_employee_question():
    relationship_with_employee_options = [
        ("Child", "Child"),
        ("Spouse", "Spouse"),
        ("Household Member", "Household Member"),
        ("Other Dependent", "Other Dependent"),
    ]
    relationship_with_employee_question = Question.objects.create(
        kind=Question.DROPDOWN,
        is_required=True,
        text="What is your relationship with {organisation} employee?",
        next_question=None,
        user_response_attribute=constants.RELATIONSHIP_WITH_EMPLOYEE,
        user_appointment_attribute=None,
    )
    for value, text in relationship_with_employee_options:
        Option.objects.create(
            text=text,
            text_mapped_value=value,
            question=relationship_with_employee_question,
        )

    return relationship_with_employee_question


def create_safety_screen_contact_support_question():
    contact_support = Question.objects.create(
        kind=Question.FRONTEND,
        backend_kind=Question.TERMINAL,
        text="Help is available Safety Sensitive",
        next_question=None,
        frontend_url="safety-screen",
        user_response_attribute=None,
    )
    return contact_support


def create_safety_sensitive_question():
    safety_sensitive_question = Question.objects.create(
        kind=Question.FRONTEND,
        backend_kind=Question.YES_NO_OPTIONS,
        text="Are you in a position that is engaged or connected with the movement of the train or subject to Hours",
        next_question=None,
        frontend_url="safety-screen",
        user_response_attribute=constants.SAFETY_SENSITIVE_POSITION,
    )
    yes_option = Option.objects.create(
        text="Yes", text_mapped_value=True, question=safety_sensitive_question
    )
    no_option = Option.objects.create(
        text="No", text_mapped_value=False, question=safety_sensitive_question
    )
    return safety_sensitive_question, yes_option, no_option


def create_are_you_employee_question():
    are_you_employee_question = Question.objects.create(
        kind=Question.YES_NO_OPTIONS,
        is_required=True,
        text="Are you an employee of {organisation}?",
        next_question=None,
        user_response_attribute=constants.IS_EMPLOYEE,
        user_appointment_attribute=None,
    )
    yes_option = Option.objects.create(
        text="Yes, I'm an employee",
        text_mapped_value=True,
        question=are_you_employee_question,
    )
    no_option = Option.objects.create(
        text="No, I'm a dependent of an employee",
        text_mapped_value=False,
        question=are_you_employee_question,
    )

    return are_you_employee_question, yes_option, no_option


def create_contact_support_question():
    contact_support = Question.objects.create(
        kind=Question.FRONTEND,
        backend_kind=Question.TERMINAL,
        text="Help is available",
        frontend_url="help-myself",
        next_question=None,
        user_response_attribute=None,
    )
    return contact_support


def create_self_harm_question():
    self_harm_question = Question.objects.create(
        kind=Question.FRONTEND,
        backend_kind=Question.YES_NO_OPTIONS,
        text="Help us understand a little more about what you’re going through",
        next_question=None,
        frontend_url="help-someone-else",
        user_response_attribute=constants.SELF_HARM,
    )
    yes_option = Option.objects.create(
        text="Yes, I am", text_mapped_value=True, question=self_harm_question
    )
    no_option = Option.objects.create(
        text="No, I am not", text_mapped_value=False, question=self_harm_question
    )
    return self_harm_question, yes_option, no_option


def create_get_emotional_support_question(
    how_often_nervous_question,
    how_often_less_interest_in_things_question,
    felt_cut_down_drinking_question,
):
    secondary_complaint_options = [
        (constants.ANXIETY, constants.ANXIETY),
        (constants.DEPRESSION, constants.DEPRESSION),
        (constants.FAMILY_ISSUES, constants.FAMILY_ISSUES),
        (constants.GRIEF, constants.GRIEF),
        (constants.RELATIONSHIP_ISSUES, constants.RELATIONSHIP_ISSUES),
        (constants.STRESS, constants.STRESS),
        (constants.ALCOHOL, constants.ALCOHOL),
    ]
    and_question = Question.objects.create(
        kind=Question.DROPDOWN,
        user_response_attribute=constants.CHIEF_COMPLAINT2,
        text="and",
    )
    for value, text in secondary_complaint_options:
        Option.objects.create(text=text, text_mapped_value=value, question=and_question)

    primary_complaint_options = [
        (constants.ANXIETY, constants.ANXIETY, how_often_nervous_question),
        (
            constants.DEPRESSION,
            constants.DEPRESSION,
            how_often_less_interest_in_things_question,
        ),
        (
            constants.FAMILY_ISSUES,
            constants.FAMILY_ISSUES,
            how_often_less_interest_in_things_question,
        ),
        (constants.GRIEF, constants.GRIEF, how_often_less_interest_in_things_question),
        (
            constants.RELATIONSHIP_ISSUES,
            constants.RELATIONSHIP_ISSUES,
            how_often_less_interest_in_things_question,
        ),
        (constants.STRESS, constants.STRESS, how_often_nervous_question),
        (constants.ALCOHOL, constants.ALCOHOL, felt_cut_down_drinking_question),
    ]

    for_question = Question.objects.create(
        kind=Question.DROPDOWN,
        text="for",
        user_response_attribute=constants.CHIEF_COMPLAINT1,
        nested_question=and_question,
    )
    for value, text, next_question in primary_complaint_options:
        Option.objects.create(
            text=text,
            text_mapped_value=value,
            question=for_question,
            next_question=next_question,
        )

    in_question = Question.objects.create(
        kind=Question.DROPDOWN,
        text="in",
        user_response_attribute=constants.APPOINTMENT_STATE,
        nested_question=for_question,
    )
    for value, text in STATE_CHOICES:
        Option.objects.create(text=text, text_mapped_value=value, question=in_question)

    get_emotional_support_question_options = [
        ("Self", "Myself"),
        ("Spouse", "My Partner"),
        ("Other Adult", "A Co-Worker"),
        ("Child", "A Dependent"),
    ]
    get_emotional_support_question = Question.objects.create(
        kind=Question.DROPDOWN,
        text="Get emotional support for",
        user_response_attribute=constants.EMOTIONAL_SUPPORT_FOR,
        nested_question=in_question,
        is_start=True,
    )
    for value, text in get_emotional_support_question_options:
        Option.objects.create(
            text=text, text_mapped_value=value, question=get_emotional_support_question
        )
    return get_emotional_support_question, in_question, for_question, and_question


def create_templates():
    IntakeQuestionTemplate.objects.all().delete()
    default_template = IntakeQuestionTemplate.objects.create(
        name="Default Template", is_default=True
    )
    template_2 = IntakeQuestionTemplate.objects.create(name="Safety Sensitive Template")
    return default_template, template_2


class Command(BaseCommand):
    help = "Load initial questions"

    def handle(self, *args, **options):
        # Delete existing questions:
        Question.objects.all().delete()

        f2f_counselor_notes = create_f2f_counselor_notes()
        f2f_okay_to_leave_voicemail_question = (
            create_f2f_okay_to_leave_voicemail_question(f2f_counselor_notes)
        )
        (
            f2f_preferred_contact_question,
            f2f_email_option,
            f2f_phone_option,
        ) = create_f2f_preferred_contact_question(
            f2f_counselor_notes, f2f_okay_to_leave_voicemail_question
        )
        f2f_address_question = create_f2f_address_question(
            f2f_preferred_contact_question
        )
        (
            f2f_counselor_search_address_question,
            f2f_home_address_option,
            f2f_other_address_option,
        ) = create_counselor_search_address_question(
            f2f_address_question, f2f_preferred_contact_question
        )
        # f2f_comfortable_language_question = create_comfortable_language_question(
        # f2f_counselor_search_address_question)
        # f2f_gender_preference_question = create_gender_preference_question(f2f_comfortable_language_question)
        f2f_gender_preference_question = create_gender_preference_question(
            f2f_counselor_search_address_question
        )
        (
            appointment_method_question,
            appointment_method_face_to_face_option,
            _,
            _,
        ) = create_appointment_method_question(f2f_gender_preference_question)
        number_of_days_missed_work_question = (
            create_number_of_days_missed_work_question()
        )
        num_days_less_productive = create_number_of_days_less_productive_question(
            number_of_days_missed_work_question
        )
        resources_to_manage_question = create_resources_to_manage_question(
            num_days_less_productive
        )
        people_support_question = create_people_support_question(
            resources_to_manage_question
        )
        comfortable_in_managing_finances_question = (
            create_comfortable_in_managing_finances_question(people_support_question)
        )
        how_physical_health_question = create_how_physical_health_question(
            comfortable_in_managing_finances_question
        )
        how_emotionally_doing_question = create_how_emotionally_doing_question(
            how_physical_health_question
        )
        difficulty_in_keeping_drinking_limit_question = (
            create_difficulty_in_keeping_drinking_linking_question(
                how_emotionally_doing_question
            )
        )
        felt_cut_down_drinking_question = create_felt_cut_down_drinking_question(
            difficulty_in_keeping_drinking_limit_question
        )
        how_often_worry_question = create_how_often_worry_question(
            felt_cut_down_drinking_question
        )
        how_often_nervous_question = create_how_often_nervous_question(
            how_often_worry_question
        )
        how_often_depressed_question = create_how_often_depressed_question(
            felt_cut_down_drinking_question
        )
        how_often_less_interest_in_things_question = (
            create_how_often_less_interest_in_things_question(
                how_often_depressed_question
            )
        )
        relationship_with_employee_question = (
            create_relationship_with_employee_question()
        )
        employee_details_question = create_employee_details_question()
        (
            is_employee_question,
            is_employee_yes_option,
            is_employee_no_option,
        ) = create_are_you_employee_question()
        safety_screen_contact_support_question = (
            create_safety_screen_contact_support_question()
        )
        (
            safety_screen_question,
            safety_screen_yes_option,
            safety_screen_no_option,
        ) = create_safety_sensitive_question()
        contact_support_question = create_contact_support_question()
        (
            self_harm_question,
            self_harm_yes_option,
            self_harm_no_option,
        ) = create_self_harm_question()
        (
            get_emotional_support_question,
            in_question,
            for_question,
            and_question,
        ) = create_get_emotional_support_question(
            how_often_nervous_question,
            how_often_less_interest_in_things_question,
            felt_cut_down_drinking_question,
        )

        # Setting previous question
        felt_cut_down_drinking_question.previous_question = (
            get_emotional_support_question
        )
        felt_cut_down_drinking_question.save()

        how_often_nervous_question.previous_question = get_emotional_support_question
        how_often_nervous_question.save()

        how_often_less_interest_in_things_question.previous_question = (
            get_emotional_support_question
        )
        how_often_less_interest_in_things_question.save()

        how_physical_health_question.previous_question = how_emotionally_doing_question
        how_physical_health_question.save()

        how_emotionally_doing_question.previous_question = (
            difficulty_in_keeping_drinking_limit_question
        )
        how_emotionally_doing_question.save()

        comfortable_in_managing_finances_question.previous_question = (
            how_physical_health_question
        )
        comfortable_in_managing_finances_question.save()

        people_support_question.previous_question = (
            comfortable_in_managing_finances_question
        )
        people_support_question.save()

        resources_to_manage_question.previous_question = people_support_question
        resources_to_manage_question.save()

        num_days_less_productive.previous_question = resources_to_manage_question
        num_days_less_productive.save()

        number_of_days_missed_work_question.previous_question = num_days_less_productive
        number_of_days_missed_work_question.save()

        difficulty_in_keeping_drinking_limit_question.previous_question = (
            felt_cut_down_drinking_question
        )
        difficulty_in_keeping_drinking_limit_question.save()

        how_often_worry_question.previous_question = how_often_nervous_question
        how_often_worry_question.save()

        how_often_depressed_question.previous_question = (
            how_often_less_interest_in_things_question
        )
        how_often_depressed_question.save()

        appointment_method_question.previous_question = (
            number_of_days_missed_work_question
        )
        appointment_method_question.save()

        f2f_gender_preference_question.previous_question = appointment_method_question
        f2f_gender_preference_question.save()

        # f2f_comfortable_language_question.previous_question = f2f_gender_preference_question
        # f2f_comfortable_language_question.save()

        # f2f_counselor_search_address_question.previous_question = f2f_comfortable_language_question
        f2f_counselor_search_address_question.previous_question = (
            f2f_gender_preference_question
        )
        f2f_counselor_search_address_question.save()

        f2f_address_question.previous_question = f2f_counselor_search_address_question
        f2f_address_question.save()

        f2f_preferred_contact_question.previous_question = f2f_address_question
        f2f_preferred_contact_question.save()

        f2f_okay_to_leave_voicemail_question.previous_question = (
            f2f_preferred_contact_question
        )
        f2f_okay_to_leave_voicemail_question.save()

        f2f_counselor_notes.previous_question = f2f_okay_to_leave_voicemail_question
        f2f_counselor_notes.save()

        default_template, safety_sensitive_template = create_templates()

        TemplateQuestionMapping.objects.create(
            template=default_template,
            question=get_emotional_support_question,
            option=None,
            next_question=self_harm_question,
            previous_question=None,
            next_question_service=None,
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=default_template,
            question=in_question,
            option=None,
            next_question=self_harm_question,
            previous_question=None,
            next_question_service=None,
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=default_template,
            question=for_question,
            option=None,
            next_question=self_harm_question,
            previous_question=None,
            next_question_service=None,
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=default_template,
            question=and_question,
            option=None,
            next_question=self_harm_question,
            previous_question=None,
            next_question_service=None,
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=default_template,
            question=self_harm_question,
            option=self_harm_yes_option,
            next_question=contact_support_question,
            previous_question=get_emotional_support_question,
            next_question_service=None,
            previous_question_service=None,
        )
        #
        # TemplateQuestionMapping.objects.create(template=default_template,
        #                                        question=self_harm_question,
        #                                        option=self_harm_no_option,
        #                                        next_question=is_employee_question,
        #                                        previous_question=get_emotional_support_question,
        #                                        next_question_service=None,
        #                                        previous_question_service=None)

        TemplateQuestionMapping.objects.create(
            template=default_template,
            question=self_harm_question,
            option=self_harm_no_option,
            next_question=None,
            previous_question=get_emotional_support_question,
            next_question_service="starting_question_next_service",
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=default_template,
            question=is_employee_question,
            option=is_employee_yes_option,
            next_question=None,
            previous_question=get_emotional_support_question,
            next_question_service="starting_question_next_service",
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=default_template,
            question=is_employee_question,
            option=is_employee_no_option,
            next_question=relationship_with_employee_question,
            previous_question=get_emotional_support_question,
            next_question_service=None,
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=default_template,
            question=relationship_with_employee_question,
            option=None,
            next_question=employee_details_question,
            previous_question=is_employee_question,
            next_question_service=None,
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=default_template,
            question=employee_details_question,
            option=None,
            next_question=None,
            previous_question=relationship_with_employee_question,
            next_question_service="starting_question_next_service",
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=default_template,
            question=how_often_less_interest_in_things_question,
            option=None,
            next_question=how_often_depressed_question,
            previous_question=None,
            next_question_service=None,
            previous_question_service="starting_question_previous_service",
        )

        TemplateQuestionMapping.objects.create(
            template=default_template,
            question=how_often_depressed_question,
            option=None,
            next_question=felt_cut_down_drinking_question,
            previous_question=how_often_less_interest_in_things_question,
            next_question_service=None,
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=default_template,
            question=how_often_nervous_question,
            option=None,
            next_question=how_often_worry_question,
            previous_question=None,
            next_question_service=None,
            previous_question_service="starting_question_previous_service",
        )

        TemplateQuestionMapping.objects.create(
            template=default_template,
            question=how_often_worry_question,
            option=None,
            next_question=felt_cut_down_drinking_question,
            previous_question=how_often_nervous_question,
            next_question_service=None,
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=default_template,
            question=felt_cut_down_drinking_question,
            option=None,
            next_question=difficulty_in_keeping_drinking_limit_question,
            previous_question=None,
            next_question_service=None,
            previous_question_service="starting_question_previous_service",
        )

        TemplateQuestionMapping.objects.create(
            template=default_template,
            question=difficulty_in_keeping_drinking_limit_question,
            option=None,
            next_question=how_emotionally_doing_question,
            previous_question=felt_cut_down_drinking_question,
            next_question_service=None,
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=default_template,
            question=how_emotionally_doing_question,
            option=None,
            next_question=how_physical_health_question,
            previous_question=difficulty_in_keeping_drinking_limit_question,
            next_question_service=None,
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=default_template,
            question=how_physical_health_question,
            option=None,
            next_question=comfortable_in_managing_finances_question,
            previous_question=how_emotionally_doing_question,
            next_question_service=None,
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=default_template,
            question=comfortable_in_managing_finances_question,
            option=None,
            next_question=people_support_question,
            previous_question=how_physical_health_question,
            next_question_service=None,
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=default_template,
            question=people_support_question,
            option=None,
            next_question=resources_to_manage_question,
            previous_question=comfortable_in_managing_finances_question,
            next_question_service=None,
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=default_template,
            question=resources_to_manage_question,
            option=None,
            next_question=num_days_less_productive,
            previous_question=people_support_question,
            next_question_service=None,
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=default_template,
            question=num_days_less_productive,
            option=None,
            next_question=number_of_days_missed_work_question,
            previous_question=resources_to_manage_question,
            next_question_service=None,
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=default_template,
            question=number_of_days_missed_work_question,
            option=None,
            next_question=appointment_method_question,
            previous_question=num_days_less_productive,
            next_question_service=None,
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=default_template,
            question=appointment_method_question,
            option=appointment_method_face_to_face_option,
            next_question=f2f_gender_preference_question,
            previous_question=number_of_days_missed_work_question,
            next_question_service=None,
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=default_template,
            question=f2f_gender_preference_question,
            option=None,
            next_question=f2f_counselor_search_address_question,
            previous_question=appointment_method_question,
            next_question_service=None,
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=default_template,
            question=f2f_counselor_search_address_question,
            option=f2f_home_address_option,
            next_question=f2f_preferred_contact_question,
            previous_question=f2f_gender_preference_question,
            next_question_service=None,
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=default_template,
            question=f2f_counselor_search_address_question,
            option=f2f_other_address_option,
            next_question=f2f_address_question,
            previous_question=f2f_gender_preference_question,
            next_question_service=None,
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=default_template,
            question=f2f_address_question,
            option=None,
            next_question=f2f_preferred_contact_question,
            previous_question=f2f_counselor_search_address_question,
            next_question_service=None,
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=default_template,
            question=f2f_preferred_contact_question,
            option=f2f_email_option,
            next_question=f2f_counselor_notes,
            previous_question=None,
            next_question_service=None,
            previous_question_service="f2f_search_address_previous_service",
        )

        TemplateQuestionMapping.objects.create(
            template=default_template,
            question=f2f_preferred_contact_question,
            option=f2f_phone_option,
            next_question=f2f_okay_to_leave_voicemail_question,
            previous_question=None,
            next_question_service=None,
            previous_question_service="f2f_search_address_previous_service",
        )

        TemplateQuestionMapping.objects.create(
            template=default_template,
            question=f2f_okay_to_leave_voicemail_question,
            option=None,
            next_question=f2f_counselor_notes,
            previous_question=f2f_preferred_contact_question,
            next_question_service=None,
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=default_template,
            question=f2f_counselor_notes,
            option=None,
            next_question=None,
            previous_question=None,
            next_question_service=None,
            previous_question_service="f2f_counselor_notes_previous_service",
        )

        TemplateQuestionMapping.objects.create(
            template=safety_sensitive_template,
            question=how_emotionally_doing_question,
            option=None,
            next_question=self_harm_question,
            previous_question=None,
            next_question_service=None,
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=safety_sensitive_template,
            question=self_harm_question,
            option=self_harm_yes_option,
            next_question=contact_support_question,
            previous_question=how_emotionally_doing_question,
            next_question_service=None,
            previous_question_service=None,
        )
        #
        # TemplateQuestionMapping.objects.create(template=safety_sensitive_template,
        #                                        question=self_harm_question,
        #                                        option=self_harm_no_option,
        #                                        next_question=is_employee_question,
        #                                        previous_question=None,
        #                                        next_question_service=None,
        #                                        previous_question_service=None)

        TemplateQuestionMapping.objects.create(
            template=safety_sensitive_template,
            question=self_harm_question,
            option=self_harm_no_option,
            next_question=None,
            previous_question=None,
            next_question_service="is_employee_question_next_service",
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=safety_sensitive_template,
            question=is_employee_question,
            option=is_employee_yes_option,
            next_question=None,
            previous_question=how_emotionally_doing_question,
            next_question_service="is_employee_question_next_service",
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=safety_sensitive_template,
            question=is_employee_question,
            option=is_employee_no_option,
            next_question=relationship_with_employee_question,
            previous_question=how_emotionally_doing_question,
            next_question_service=None,
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=safety_sensitive_template,
            question=relationship_with_employee_question,
            option=None,
            next_question=employee_details_question,
            previous_question=is_employee_question,
            next_question_service=None,
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=safety_sensitive_template,
            question=employee_details_question,
            option=None,
            next_question=None,
            previous_question=relationship_with_employee_question,
            next_question_service="starting_question_next_service",
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=safety_sensitive_template,
            question=safety_screen_question,
            option=safety_screen_yes_option,
            next_question=safety_screen_contact_support_question,
            previous_question=is_employee_question,
            next_question_service=None,
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=safety_sensitive_template,
            question=safety_screen_question,
            option=safety_screen_no_option,
            next_question=None,
            previous_question=is_employee_question,
            next_question_service="starting_question_next_service",
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=safety_sensitive_template,
            question=how_often_less_interest_in_things_question,
            option=None,
            next_question=how_often_depressed_question,
            previous_question=None,
            next_question_service=None,
            previous_question_service="starting_question_previous_service",
        )

        TemplateQuestionMapping.objects.create(
            template=safety_sensitive_template,
            question=how_often_depressed_question,
            option=None,
            next_question=felt_cut_down_drinking_question,
            previous_question=how_often_less_interest_in_things_question,
            next_question_service=None,
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=safety_sensitive_template,
            question=how_often_nervous_question,
            option=None,
            next_question=how_often_worry_question,
            previous_question=None,
            next_question_service=None,
            previous_question_service="starting_question_previous_service",
        )

        TemplateQuestionMapping.objects.create(
            template=safety_sensitive_template,
            question=how_often_worry_question,
            option=None,
            next_question=felt_cut_down_drinking_question,
            previous_question=how_often_nervous_question,
            next_question_service=None,
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=safety_sensitive_template,
            question=felt_cut_down_drinking_question,
            option=None,
            next_question=None,
            previous_question=None,
            next_question_service="safety_screen_felt_cut_down_drinking_question_next_service",
            previous_question_service="starting_question_previous_service",
        )

        TemplateQuestionMapping.objects.create(
            template=safety_sensitive_template,
            question=difficulty_in_keeping_drinking_limit_question,
            option=None,
            next_question=None,
            previous_question=felt_cut_down_drinking_question,
            next_question_service="safety_screen_difficulty_in_keeping_drinking_limit_question_next_service",
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=safety_sensitive_template,
            question=how_emotionally_doing_question,
            option=None,
            next_question=how_physical_health_question,
            previous_question=difficulty_in_keeping_drinking_limit_question,
            next_question_service=None,
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=safety_sensitive_template,
            question=how_physical_health_question,
            option=None,
            next_question=comfortable_in_managing_finances_question,
            previous_question=how_emotionally_doing_question,
            next_question_service=None,
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=safety_sensitive_template,
            question=comfortable_in_managing_finances_question,
            option=None,
            next_question=people_support_question,
            previous_question=how_physical_health_question,
            next_question_service=None,
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=safety_sensitive_template,
            question=people_support_question,
            option=None,
            next_question=resources_to_manage_question,
            previous_question=comfortable_in_managing_finances_question,
            next_question_service=None,
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=safety_sensitive_template,
            question=resources_to_manage_question,
            option=None,
            next_question=num_days_less_productive,
            previous_question=people_support_question,
            next_question_service=None,
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=safety_sensitive_template,
            question=num_days_less_productive,
            option=None,
            next_question=number_of_days_missed_work_question,
            previous_question=resources_to_manage_question,
            next_question_service=None,
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=safety_sensitive_template,
            question=number_of_days_missed_work_question,
            option=None,
            next_question=appointment_method_question,
            previous_question=num_days_less_productive,
            next_question_service=None,
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=safety_sensitive_template,
            question=appointment_method_question,
            option=appointment_method_face_to_face_option,
            next_question=f2f_gender_preference_question,
            previous_question=number_of_days_missed_work_question,
            next_question_service=None,
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=safety_sensitive_template,
            question=f2f_gender_preference_question,
            option=None,
            next_question=f2f_counselor_search_address_question,
            previous_question=appointment_method_question,
            next_question_service=None,
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=safety_sensitive_template,
            question=f2f_counselor_search_address_question,
            option=f2f_home_address_option,
            next_question=f2f_preferred_contact_question,
            previous_question=f2f_gender_preference_question,
            next_question_service=None,
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=safety_sensitive_template,
            question=f2f_counselor_search_address_question,
            option=f2f_other_address_option,
            next_question=f2f_address_question,
            previous_question=f2f_gender_preference_question,
            next_question_service=None,
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=safety_sensitive_template,
            question=f2f_address_question,
            option=None,
            next_question=f2f_preferred_contact_question,
            previous_question=f2f_counselor_search_address_question,
            next_question_service=None,
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=safety_sensitive_template,
            question=f2f_preferred_contact_question,
            option=f2f_email_option,
            next_question=f2f_counselor_notes,
            previous_question=None,
            next_question_service=None,
            previous_question_service="f2f_search_address_previous_service",
        )

        TemplateQuestionMapping.objects.create(
            template=safety_sensitive_template,
            question=f2f_preferred_contact_question,
            option=f2f_phone_option,
            next_question=f2f_okay_to_leave_voicemail_question,
            previous_question=None,
            next_question_service=None,
            previous_question_service="f2f_search_address_previous_service",
        )

        TemplateQuestionMapping.objects.create(
            template=safety_sensitive_template,
            question=f2f_okay_to_leave_voicemail_question,
            option=None,
            next_question=f2f_counselor_notes,
            previous_question=f2f_preferred_contact_question,
            next_question_service=None,
            previous_question_service=None,
        )

        TemplateQuestionMapping.objects.create(
            template=safety_sensitive_template,
            question=f2f_counselor_notes,
            option=None,
            next_question=None,
            previous_question=None,
            next_question_service=None,
            previous_question_service="f2f_counselor_notes_previous_service",
        )

        self.stdout.write(self.style.SUCCESS("Successfully created question!"))
