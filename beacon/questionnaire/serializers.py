# -*- coding: utf-8 -*-
# Third Party Stuff
from rest_framework import serializers

from .models import Option, Question


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ("id", "text", "next_question", "previous_question")
        read_only_fields = fields


class QuestionSerializer(serializers.ModelSerializer):
    choices = serializers.SerializerMethodField()
    multiple_questions = serializers.SerializerMethodField()
    show_safety_screen = serializers.SerializerMethodField()
    kind = serializers.SerializerMethodField()
    text = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = (
            "id",
            "kind",
            "text",
            "subheading",
            "placeholder",
            "is_required",
            "min_length",
            "max_length",
            "is_start",
            "yes_button_text",
            "no_button_text",
            "next_question",
            "previous_question",
            "show_safety_screen",
            "frontend_url",
            "frontend_meta_data",
            "choices",
            "nested_question",
            "multiple_questions",
        )
        read_only_fields = fields

    def get_kind(self, obj):
        if obj.kind == Question.YES_NO_OPTIONS:
            return Question.DROPDOWN
        return obj.kind

    def get_text(self, obj):
        organisation = self.context.get("organisation")
        if obj.text and organisation:
            return obj.text.format(organisation=organisation.location)
        return obj.text

    def get_multiple_questions(self, obj):
        if obj.kind == Question.MULTIPLE_QUESTIONS:
            follower_questions = obj.follower_questions.all()
            return self.__class__(
                follower_questions, many=True, context=self.context
            ).data
        return None

    def get_show_safety_screen(self, obj):
        organisation = self.context.get("organisation")
        if (
            organisation
            and organisation.show_safety_screen is True
            and obj.show_safety_screen is True
        ):
            return True
        return False

    def get_choices(self, obj):
        if obj.kind == Question.ORGANISATION:
            organisation = self.context.get("organisation")
            if organisation:
                child_organisations = organisation.children.all().filter(is_active=True)
                return [
                    {
                        "id": str(co.id),
                        "text": co.location,
                        "next_question": None,
                        "previous_question": None,
                    }
                    for co in child_organisations
                ]
        else:
            data = OptionSerializer(obj.choices.all(), many=True).data
            if data:
                return data
        return None


class NestedQuestionSerializer(QuestionSerializer):
    class Meta(QuestionSerializer.Meta):
        pass

    def get_fields(self):
        fields = super().get_fields()
        fields["nested_question"] = NestedQuestionSerializer()
        return fields
