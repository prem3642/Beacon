# -*- coding: utf-8 -*-
# Third Party Stuff
from rest_framework import serializers

from . import constants, services


class SCCBaseSerializer(serializers.Serializer):
    providerId = serializers.CharField(max_length=20)
    vendorId = serializers.CharField(max_length=20)
    class Meta:
        fields = (
            "memberId",
            "mdLiveMemberID",
            "emailAddress",
            "addressLine1",
            "addressLine2",
            "addressCity",
            "addressStateCode",
            "addressZipCode",
            "phoneNumberAreaCode",
            "phoneNumberCentralOfficeCode",
            "phoneNumberExchange",
            "parentCode",
            "groupNumber",
            "benefitPackage",
            "relationshipStatus",
            "employmentStatus",
            "jobTitle",
            "primaryPresentingProblem",
            "secondaryPresentingProblem",
            "depressionScreenerQuestion3A ",
            "depressionScreenerQuestion3B",
            "anxietyScreenerQuestion5A",
            "anxietyScreenerQuestion5B",
            "substanceUseQuestion7A",
            "substanceUseQuestion7B",
            "wellbeingDomainQuestion8",
            "wellbeingDomainQuestion9",
            "wellbeingDomainQuestion10",
            "wellbeingDomainQuestion11 ",
            "wellbeingDomainQuestion12",
            "outcomesESDQuestion1",
            "outcomesESDQuestion2",
            "providerId",
            "vendorId"
        )

    def validate(self, attributes):
        """
        Verifies that corresponding BWB mapping exists for the incoming SCC data.
        """
        validated_data = super().validate(attributes)
        for attribute, value in attributes.items():
            if value is not None:
                attribute_mapping = constants.SCC_KEYS_MAPPING.get(attribute)
                if attribute_mapping and value not in attribute_mapping.keys():
                    raise serializers.ValidationError(
                        {
                            attribute: f"Invalid value. Mapping not found for value '{value}'."
                        }
                    )
        return validated_data


class SCCUserForceSyncSerializer(SCCBaseSerializer):
    memberId = serializers.CharField(required=False)
    mdLiveMemberID = serializers.CharField(required=False, allow_null=True)
    emailAddress = serializers.CharField(required=False)
    addressLine1 = serializers.CharField(required=False)
    addressLine2 = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    addressCity = serializers.CharField(required=False)
    addressStateCode = serializers.CharField(required=False)
    addressZipCode = serializers.CharField(required=False)
    phoneNumberAreaCode = serializers.CharField(max_length=3, required=False)
    phoneNumberCentralOfficeCode = serializers.CharField(max_length=4, required=False)
    phoneNumberExchange = serializers.CharField(max_length=4, required=False)
    parentCode = serializers.CharField(required=False)
    groupNumber = serializers.CharField(required=False)
    benefitPackage = serializers.CharField(required=False)
    relationshipStatus = serializers.CharField(required=False, allow_null=True)
    employmentStatus = serializers.CharField(required=False, allow_null=True)
    jobTitle = serializers.CharField(required=False, allow_null=True)
    primaryPresentingProblem = serializers.CharField(required=False)
    secondaryPresentingProblem = serializers.CharField(required=False, allow_null=True)
    depressionScreenerQuestion3A = serializers.CharField(
        required=False, allow_null=True
    )
    depressionScreenerQuestion3B = serializers.CharField(
        required=False, allow_null=True
    )
    anxietyScreenerQuestion5A = serializers.CharField(required=False, allow_null=True)
    anxietyScreenerQuestion5B = serializers.CharField(required=False, allow_null=True)
    substanceUseQuestion7A = serializers.CharField(required=False, allow_null=True)
    substanceUseQuestion7B = serializers.CharField(required=False, allow_null=True)
    wellbeingDomainQuestion8 = serializers.CharField(required=False, allow_null=True)
    wellbeingDomainQuestion9 = serializers.CharField(required=False, allow_null=True)
    wellbeingDomainQuestion10 = serializers.CharField(required=False, allow_null=True)
    wellbeingDomainQuestion11 = serializers.CharField(required=False, allow_null=True)
    wellbeingDomainQuestion12 = serializers.CharField(required=False, allow_null=True)
    outcomesESDQuestion1 = serializers.CharField(required=False, allow_null=True)
    outcomesESDQuestion2 = serializers.CharField(required=False, allow_null=True)


class SCCUserSyncSerializer(SCCBaseSerializer):
    firstName = serializers.CharField(required=True, allow_blank=True)
    lastName = serializers.CharField(required=True, allow_blank=True)
    dateOfBirth = serializers.CharField(min_length=7, max_length=7, required=True)
    gender = serializers.CharField(required=True)

    memberId = serializers.CharField(required=True)
    emailAddress = serializers.CharField(required=True)
    addressLine1 = serializers.CharField(required=True)
    addressCity = serializers.CharField(required=True)
    addressStateCode = serializers.CharField(required=True)
    addressZipCode = serializers.CharField(required=True)
    phoneNumberAreaCode = serializers.CharField(max_length=3, required=True)
    phoneNumberCentralOfficeCode = serializers.CharField(max_length=4, required=True)
    phoneNumberExchange = serializers.CharField(max_length=4, required=True)
    parentCode = serializers.CharField(required=True)
    groupNumber = serializers.CharField(required=True)
    benefitPackage = serializers.CharField(required=True)
    primaryPresentingProblem = serializers.CharField(required=True)

    # Nullable attributes
    addressLine2 = serializers.CharField(
        required=True, allow_null=True, allow_blank=True
    )
    mdLiveMemberID = serializers.CharField(required=True, allow_null=True)
    relationshipStatus = serializers.CharField(required=True, allow_null=True)
    employmentStatus = serializers.CharField(required=True, allow_null=True)
    jobTitle = serializers.CharField(required=True, allow_null=True)
    secondaryPresentingProblem = serializers.CharField(required=True, allow_null=True)
    depressionScreenerQuestion3A = serializers.CharField(required=True, allow_null=True)
    depressionScreenerQuestion3B = serializers.CharField(required=True, allow_null=True)
    anxietyScreenerQuestion5A = serializers.CharField(required=True, allow_null=True)
    anxietyScreenerQuestion5B = serializers.CharField(required=True, allow_null=True)
    substanceUseQuestion7A = serializers.CharField(required=True, allow_null=True)
    substanceUseQuestion7B = serializers.CharField(required=True, allow_null=True)
    wellbeingDomainQuestion8 = serializers.CharField(required=True, allow_null=True)
    wellbeingDomainQuestion9 = serializers.CharField(required=True, allow_null=True)
    wellbeingDomainQuestion10 = serializers.CharField(required=True, allow_null=True)
    wellbeingDomainQuestion11 = serializers.CharField(required=True, allow_null=True)
    wellbeingDomainQuestion12 = serializers.CharField(required=True, allow_null=True)
    outcomesESDQuestion1 = serializers.CharField(required=True, allow_null=True)
    outcomesESDQuestion2 = serializers.CharField(required=True, allow_null=True)

    class Meta(SCCBaseSerializer.Meta):
        fields = SCCBaseSerializer.Meta.fields + (
            "firstName",
            "lastName",
            "dateOfBirth",
            "gender",
        )

    def validate_dateOfBirth(self, value):
        services.validate_ibm_date_format(value)
        return value
