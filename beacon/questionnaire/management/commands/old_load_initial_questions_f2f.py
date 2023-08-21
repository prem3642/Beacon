# -*- coding: utf-8 -*-
# Third Party Stuff
from django.core.management.base import BaseCommand

# beacon Stuff
from beacon.answers import constants
from beacon.questionnaire.models import Option, Question
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


def create_f2f_preferred_contact_question(next_questions_list):
    f2f_preferred_contact_option = [
        ("email", "Email", next_questions_list[0]),
        ("phone", "Phone", next_questions_list[1]),
    ]

    f2f_preferred_contact_question = Question.objects.create(
        kind=Question.RADIO,
        text="How would you prefer we contact you with recommended counselors?",
        placeholder="(We'll ask for your contact info later)",
        next_question=None,
        user_response_attribute=None,
        user_appointment_attribute=constants.F2F_PREFERRED_CONTACT,
    )

    for value, text, next_question in f2f_preferred_contact_option:
        Option.objects.create(
            text=text,
            text_mapped_value=value,
            question=f2f_preferred_contact_question,
            next_question=next_question,
        )
    return f2f_preferred_contact_question


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
    f2f_counselor_search_address_option = [
        ("home_address", "Search near my home address", default_question),
        ("other_address", "Search near a different address (e.g. work)", next_question),
    ]

    f2f_counselor_search_address_question = Question.objects.create(
        kind=Question.RADIO,
        text="We will find counselors as close to your location as possible. "
        "Please let us know where to start our search.",
        next_question=default_question,
        user_response_attribute=None,
        user_appointment_attribute=constants.F2F_COUNSELOR_SEARCH_ADDRESS,
    )

    for value, text, next_question in f2f_counselor_search_address_option:
        Option.objects.create(
            text=text,
            text_mapped_value=value,
            question=f2f_counselor_search_address_question,
            next_question=next_question,
        )

    return f2f_counselor_search_address_question


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
    appointment_method_options = [
        ("video", "Video", None),
        ("phone", "Phone", None),
        ("face_to_face", "Face To Face", next_question),
    ]

    appointment_method_question = Question.objects.create(
        kind=Question.DROPDOWN,
        text="How would you like to talk to your counselor?",
        next_question=None,
        user_response_attribute=None,
        user_appointment_attribute=constants.APPOINTMENT_METHOD,
        is_appointment_start=True,
    )

    for value, text, next_question in appointment_method_options:
        Option.objects.create(
            text=text,
            text_mapped_value=value,
            question=appointment_method_question,
            next_question=next_question,
        )
    return appointment_method_question


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


def create_get_emotional_support_question(
    how_often_nervous_question,
    how_often_less_interest_in_things_question,
    felt_cut_down_drinking_question,
):
    secondary_complaint_options = [
        ("Anxiety", "Anxiety"),
        ("Depression", "Depression"),
        ("Family Issues", "Family Issues"),
        ("Grief or Loss", "Grief or Loss"),
        ("Relationship Issues", "Relationship Issues"),
        ("Stress", "Stress"),
        ("Alcohol or Drug use", "Alcohol or Drug use"),
    ]
    and_question = Question.objects.create(
        kind=Question.DROPDOWN,
        user_response_attribute=constants.CHIEF_COMPLAINT2,
        text="and",
    )
    for value, text in secondary_complaint_options:
        Option.objects.create(text=text, text_mapped_value=value, question=and_question)

    primary_complaint__options = [
        ("Anxiety", "Anxiety", how_often_nervous_question),
        ("Depression", "Depression", how_often_less_interest_in_things_question),
        ("Family Issues", "Family Issues", how_often_less_interest_in_things_question),
        ("Grief or Loss", "Grief or Loss", how_often_less_interest_in_things_question),
        (
            "Relationship Issues",
            "Relationship Issues",
            how_often_less_interest_in_things_question,
        ),
        ("Stress", "Stress", how_often_nervous_question),
        ("Alcohol or Drug use", "Alcohol or Drug use", felt_cut_down_drinking_question),
    ]

    for_question = Question.objects.create(
        kind=Question.DROPDOWN,
        text="for",
        user_response_attribute=constants.CHIEF_COMPLAINT1,
        nested_question=and_question,
    )
    for value, text, next_question in primary_complaint__options:
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
    return get_emotional_support_question


class Command(BaseCommand):
    help = "Load initial questions"

    def handle(self, *args, **options):
        # Delete existing questions:
        Question.objects.all().delete()

        f2f_counselor_notes = create_f2f_counselor_notes()
        f2f_okay_to_leave_voicemail_question = (
            create_f2f_okay_to_leave_voicemail_question(f2f_counselor_notes)
        )
        f2f_preferred_contact_question = create_f2f_preferred_contact_question(
            [f2f_counselor_notes, f2f_okay_to_leave_voicemail_question]
        )
        f2f_address_question = create_f2f_address_question(
            f2f_preferred_contact_question
        )
        f2f_counselor_search_address_question = (
            create_counselor_search_address_question(
                f2f_address_question, f2f_preferred_contact_question
            )
        )
        # f2f_comfortable_language_question = create_comfortable_language_question(
        # f2f_counselor_search_address_question)
        # f2f_gender_preference_question = create_gender_preference_question(f2f_comfortable_language_question)
        f2f_gender_preference_question = create_gender_preference_question(
            f2f_counselor_search_address_question
        )
        appointment_method_question = create_appointment_method_question(
            f2f_gender_preference_question
        )
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
        get_emotional_support_question = create_get_emotional_support_question(
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

        self.stdout.write(self.style.SUCCESS("Successfully created question!"))
