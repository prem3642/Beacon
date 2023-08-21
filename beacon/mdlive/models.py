# -*- coding: utf-8 -*-
# Third Party Stuff
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import JSONField
from django.utils.translation import gettext_lazy as _

# beacon Stuff
from beacon.base.models import TimeStampedUUIDModel, UUIDModel

USER = get_user_model()


class Provider(TimeStampedUUIDModel):
    MALE = "Male"
    FEMALE = "Female"
    SYSTEM = "System"
    GENDER_CHOICES = (
        (MALE, "Male"),
        (FEMALE, "Female"),
        (SYSTEM, "System"),
    )

    mdlive_id = models.PositiveIntegerField(_("Provider id on mdlive"), db_index=True)
    fullname = models.CharField(_("Full Name"), max_length=100)
    prefix = models.CharField(_("prefix"), max_length=50, null=True, blank=True)
    gender = models.CharField(_("Gender"), max_length=6, choices=GENDER_CHOICES)
    speciality = models.CharField(_("Speciality"), max_length=50, null=True, blank=True)
    specialities = JSONField(_("Specialities"), null=True, blank=True)
    photo_url = models.CharField(_("Image Url"), max_length=100, null=True, blank=True)
    photo_url_absolute = models.URLField(null=True, blank=True)
    photo_in_binary_data = models.TextField(null=True, blank=True)
    photo_format = models.CharField(null=True, blank=True, max_length=5)

    class Meta:
        db_table = "provider"
        verbose_name = _("provider")
        ordering = [
            "-created_at",
        ]

    def __str__(self):
        return f"{self.mdlive_id}-{self.fullname}"


class UserDocument(TimeStampedUUIDModel):
    RECORD_TYPE_CHOICES = (
        ("Behavioral", "Behavioral"),
        ("Exam-Face2Face", "Exam-Face2Face"),
        ("Patient Record", "Patient Record"),
        ("Test Result", "Test Result"),
        ("Wellness Panel Results", "Wellness Panel Results"),
    )

    user = models.ForeignKey(USER, on_delete=models.CASCADE, related_name="documents")
    mdlive_id = models.PositiveIntegerField(
        _("Mdlive doc id"), db_index=True, null=True, blank=True
    )
    extension = models.CharField(_("Extension"), max_length=6, null=True, blank=True)
    document_name = models.CharField(_("document name with extension"), max_length=200)
    mime_type = models.CharField(_("mime type of document"), max_length=20)
    record_type = models.CharField(
        _("record type"), max_length=25, choices=RECORD_TYPE_CHOICES
    )

    class Meta:
        db_table = "user_document"
        verbose_name = _("user document")
        ordering = [
            "-created_at",
        ]

    def __str__(self):
        return f"{self.user}-{self.document_name}"


class Message(UUIDModel):
    USER_MESSAGE = "user_message"
    PROVIDER_MESSAGE = "provider_message"
    MESSAGE_TYPES = (
        (USER_MESSAGE, "User Message"),
        (PROVIDER_MESSAGE, "Provider Message"),
    )

    mdlive_id = models.PositiveIntegerField(_("Mdlive message id"), db_index=True)
    message_type = models.CharField(
        _("Message Type"), max_length=18, default=USER_MESSAGE, choices=MESSAGE_TYPES
    )
    subject = models.CharField(_("Subject"), max_length=256)
    message = models.TextField(_("Message"))
    is_read = models.BooleanField(
        _("Is Read"),
        default=False,
        help_text="Designates weather user have read the message or not!",
    )
    replied_to_message_id = models.PositiveIntegerField(
        _("Replied to mdlive message id"), null=True, blank=True
    )
    datetime = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)
    documents = models.ManyToManyField(
        UserDocument, related_name="messages", through="MessageDocument"
    )
    reply_allowed = models.BooleanField(_("Reply Allowed"), default=False)

    class Meta:
        db_table = "message"
        verbose_name = _("message")
        ordering = [
            "-datetime",
        ]

    def __str__(self):
        return f"{self.mdlive_id}-{self.subject}"


class MessageDocument(UUIDModel):
    message = models.ForeignKey(
        Message, related_name="message_documents", on_delete=models.CASCADE
    )
    document = models.ForeignKey(
        UserDocument, related_name="message_documents", on_delete=models.CASCADE
    )

    class Meta:
        db_table = "message_document"
        verbose_name = _("message document")

    def __str__(self):
        return f"{self.message}-{self.document}"


class ProviderMessage(UUIDModel):
    message = models.OneToOneField(
        Message, on_delete=models.CASCADE, related_name="provider_message"
    )
    message_from = models.ForeignKey(
        Provider, on_delete=models.CASCADE, related_name="messages"
    )
    message_to = models.ForeignKey(
        USER, on_delete=models.CASCADE, related_name="providers_messages"
    )

    class Meta:
        db_table = "provider_message"
        verbose_name = _("provider message")
        verbose_name_plural = _("providers messages")
        ordering = [
            "id",
        ]

    def __str__(self):
        return f"{self.message_from}-{self.message_to}"


class UserMessage(UUIDModel):
    message = models.OneToOneField(
        Message, on_delete=models.CASCADE, related_name="user_message"
    )
    message_from = models.ForeignKey(
        USER, on_delete=models.CASCADE, related_name="messages"
    )
    message_to = models.ForeignKey(
        Provider, on_delete=models.CASCADE, related_name="users_messages"
    )

    class Meta:
        db_table = "user_message"
        verbose_name = _("user message")
        verbose_name_plural = _("users messages")
        ordering = [
            "id",
        ]

    def __str__(self):
        return f"{self.message_from}-{self.message_to}"


class Contact(TimeStampedUUIDModel):
    user = models.ForeignKey(USER, on_delete=models.CASCADE, related_name="providers")
    provider = models.ForeignKey(
        Provider, on_delete=models.CASCADE, related_name="users"
    )

    class Meta:
        db_table = "contact"
        verbose_name = _("contact")
        ordering = [
            "-created_at",
        ]

    def __str__(self):
        return f"{self.user}-{self.provider}"


class AppointmentSlotQuery(TimeStampedUUIDModel):
    APPOINTMENT_METHOD_CHOICES = (
        ("phone", "phone"),
        ("video", "video"),
    )
    PREFERRED_TIME_CHOICES = (
        ("morning", "morning"),
        ("first available", "first available"),
        ("afternoon", "afternoon"),
        ("evening", "evening"),
    )
    user = models.ForeignKey(
        USER, on_delete=models.CASCADE, related_name="appointment_requests"
    )
    mdlive_id = models.PositiveIntegerField(
        _("Mdlive appointment request id"), db_index=True, null=True
    )
    provider_id = models.PositiveIntegerField(
        _("Provider id"), db_index=True, null=True
    )
    preferred_time = models.CharField(
        _("preferred time"), max_length=15, choices=PREFERRED_TIME_CHOICES
    )
    appointment_method = models.CharField(
        _("appointment method"), max_length=5, choices=APPOINTMENT_METHOD_CHOICES
    )
    appointment_date = models.DateField(_("appointment date"))
    chief_complaint = models.CharField(_("chief complaint"), max_length=50, null=True)
    chief_complaint_comments = models.CharField(
        _("chief complaint comments"), max_length=150, null=True
    )
    contact_number = models.CharField(_("contact number"), max_length=15, null=True)
    appointment_request_state = models.CharField(
        _("appointment request state"), max_length=2, null=True
    )
    is_cancelled = models.BooleanField(_("cancelled"), default=False)

    class Meta:
        db_table = "appointment_slot_query"
        verbose_name = _("appointment slot query")
        verbose_name_plural = _("appointment slot queries")
        ordering = [
            "-created_at",
        ]

    def __str__(self):
        return f"{self.mdlive_id}-{self.user}-{self.provider_id}"
