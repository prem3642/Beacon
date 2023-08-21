# -*- coding: utf-8 -*-

# Third Party Stuff
from rest_framework import serializers

from .models import AppointmentSlotQuery, Message, Provider, UserDocument


class ExtendMDLiveTokenSerializer(serializers.Serializer):
    jwt_token = serializers.CharField()

    class Meta:
        fields = ("jwt_token",)


class UserMDLiveTokenSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    gender = serializers.ChoiceField(choices=(("M", "M"), ("F", "F")), allow_null=True)
    birthdate = serializers.DateField(format="%Y-%m-%d")
    phone = serializers.CharField()
    email = serializers.EmailField()
    address1 = serializers.CharField()
    address2 = serializers.CharField(required=False, allow_null=True)
    city = serializers.CharField()
    state = serializers.CharField(max_length=2)
    zip = serializers.CharField(max_length=5)
    relationship = serializers.ChoiceField(
        choices=(
            ("Self", "Self"),
            ("Spouse", "Spouse"),
            ("Child", "Child"),
            ("Other Adult", "Other Adult"),
        )
    )

    class Meta:
        fields = (
            "first_name",
            "last_name",
            "gender",
            "birthdate",
            "subscriber_id",
            "phone",
            "email",
            "address1",
            "address2",
            "city",
            "state",
            "zip",
            "relationship",
        )


# Not in use
class PatientMDLiveSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()
    password_confirmation = serializers.CharField()
    phone = serializers.CharField()
    zip = serializers.CharField(max_length=5)
    gender = serializers.ChoiceField(choices=(("male", "male"), ("female", "female")))
    birthdate = serializers.DateField(format="%Y-%m-%d")
    affiliation_id = serializers.CharField(max_length=5)
    address1 = serializers.CharField(required=False)
    address2 = serializers.CharField(required=False, allow_null=True)
    city = serializers.CharField(required=False)
    state = serializers.CharField(max_length=2, required=False)

    class Meta:
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "password",
            "password_confirmation",
            "phone",
            "zip",
            "gender",
            "birthdate",
            "affiliation_id",
            "address1",
            "address2",
            "city",
            "state",
        )


class UserDocumentSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = UserDocument
        fields = [
            "id",
            "mdlive_id",
            "user",
            "document_name",
            "mime_type",
            "record_type",
            "extension",
        ]


class UserDocumentCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="mdlive_id")
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = UserDocument
        fields = [
            "id",
            "user",
            "document_name",
            "mime_type",
            "record_type",
            "extension",
        ]


class MessageSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    unread_status = serializers.SerializerMethodField()
    date_time = serializers.DateTimeField(source="datetime")
    from_id = serializers.SerializerMethodField()
    to = serializers.SerializerMethodField()
    to_id = serializers.SerializerMethodField()
    replied_to_message_id = serializers.IntegerField(required=False)

    class Meta:
        model = Message
        fields = (
            "id",
            "subject",
            "message",
            "unread_status",
            "replied_to_message_id",
            "date_time",
            "from",
            "from_id",
            "to",
            "to_id",
            "message_type",
            "reply_allowed",
            "documents",
        )

    def get_id(self, obj):
        return obj.mdlive_id

    def get_unread_status(self, obj):
        return not obj.is_read

    def get_from(self, obj):
        if hasattr(obj, "provider_message"):
            return obj.provider_message.message_from.fullname
        if hasattr(obj, "user_message"):
            return f"{obj.user_message.message_from.first_name} {obj.user_message.message_from.last_name}"

    def get_from_id(self, obj):
        if hasattr(obj, "provider_message"):
            return obj.provider_message.message_from.mdlive_id
        if hasattr(obj, "user_message"):
            return obj.user_message.message_from.mdlive_id

    def get_to(self, obj):
        if hasattr(obj, "provider_message"):
            return f"{obj.provider_message.message_to.first_name} {obj.provider_message.message_to.last_name}"
        if hasattr(obj, "user_message"):
            return obj.user_message.message_to.fullname

    def get_to_id(self, obj):
        if hasattr(obj, "provider_message"):
            return obj.provider_message.message_to.mdlive_id
        if hasattr(obj, "user_message"):
            return obj.user_message.message_to.mdlive_id


# Adding reserved keyword to match the MDLIVE api
MessageSerializer._declared_fields["from"] = serializers.SerializerMethodField()


class MessageSerializerDetail(MessageSerializer):
    documents = UserDocumentSerializer(many=True)

    class Meta(MessageSerializer.Meta):
        model = Message


class UserMessageSerializer(serializers.ModelSerializer):
    message_type = serializers.CharField(default="follow_up")
    to_id = serializers.IntegerField()
    documents = serializers.PrimaryKeyRelatedField(
        required=False, many=True, queryset=UserDocument.objects.all()
    )

    class Meta:
        model = Message
        fields = (
            "message_type",
            "to_id",
            "subject",
            "message",
            "replied_to_message_id",
            "documents",
        )

    def validate(self, attrs):
        documents = attrs.get("documents")
        user = self.context.get("request").user
        if user and documents:
            for doc in documents:
                if doc.user != user:
                    raise serializers.ValidationError(
                        "You are not allowed to send documents of other users!"
                    )
        return attrs


class ProviderSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    class Meta:
        model = Provider
        fields = (
            "id",
            "fullname",
            "prefix",
            "gender",
            "speciality",
            "photo_url",
            "photo_url_absolute",
        )

    def get_id(self, obj):
        return obj.mdlive_id


class AppointmentSlotQuerySerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    appointment_date = serializers.DateField(format="%Y-%m-%d")

    class Meta:
        model = AppointmentSlotQuery
        fields = (
            "id",
            "mdlive_id",
            "user",
            "provider_id",
            "preferred_time",
            "appointment_method",
            "appointment_date",
            "chief_complaint",
            "chief_complaint_comments",
            "contact_number",
            "appointment_request_state",
        )
        read_only_fields = (
            "mdlive_id",
            "chief_complaint",
            "contact_number",
            "appointment_request_state",
        )

    def validate(self, attrs):
        user = attrs.get("user")
        if user:
            user_response = user.answer if hasattr(user, "answer") else None
            attrs["contact_number"] = user.phone
            if user_response:
                attrs["chief_complaint"] = user_response.chief_complaint1
                attrs["appointment_request_state"] = user_response.appointment_state
        return attrs
