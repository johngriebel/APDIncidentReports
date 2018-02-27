import logging
from django.contrib.auth import get_user_model
from address.models import _to_python, Address
from rest_framework import serializers
from rest_framework.settings import api_settings
from .models import (Officer, Incident,
                     Offense, IncidentInvolvedParty,
                     IncidentFile)
User = get_user_model()
logger = logging.getLogger('cases')


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "email")
        read_only_fields = ("id",)


class OfficerSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    def to_internal_value(self, data):
        if isinstance(data, int):
            try:
                return Officer.objects.get(id=data)
            except Officer.DoesNotExist:
                logger.debug(f"Tried to find officer with ID: {data}")
                message = self.error_messages['invalid'].format(
                    datatype=type(data).__name__
                )
                raise serializers.ValidationError({
                    api_settings.NON_FIELD_ERRORS_KEY: [message]
                }, code='invalid')
        else:
            return super(OfficerSerializer, self).to_internal_value(data=data)

    class Meta:
        model = Officer
        fields = ("id", "officer_number", "supervisor", "user")
        read_only_fields = ("id",)

    def create(self, validated_data):
        logger.debug(validated_data)
        officer = Officer.objects.create(user=validated_data['user'],
                                         officer_number=validated_data['officer_number'],
                                         supervisor=validated_data['supervisor'])
        return officer


class OffenseSerializer(serializers.ModelSerializer):

    def to_internal_value(self, data):
        if isinstance(data, int):
            try:
                return Offense.objects.get(id=data)
            except Offense.DoesNotExist:
                logger.debug(f"Tried to find offense with ID: {data}")
                message = self.error_messages['invalid'].format(
                    datatype=type(data).__name__
                )
                raise serializers.ValidationError({
                    api_settings.NON_FIELD_ERRORS_KEY: [message]
                }, code='invalid')
        else:
            return super(OffenseSerializer, self).to_internal_value(data=data)

    class Meta:
        model = Offense
        fields = "__all__"


class IncidentSerializer(serializers.ModelSerializer):
    offenses = OffenseSerializer(many=True)
    reporting_officer = OfficerSerializer()
    reviewed_by_officer = OfficerSerializer()
    investigating_officer = OfficerSerializer()
    officer_making_report = OfficerSerializer()
    supervisor = OfficerSerializer()
    location = AddressSerializer()

    def validate_location(self, value):
        for addr_field in ["raw", "country", "country_code", "state",
                           "state_code", "postal_code", "street_number",
                           "route", "locality"]:
            if addr_field not in value:
                raise serializers.ValidationError(f"Missing field {addr_field} from location.")
        address_obj = _to_python(value)
        return address_obj

    def create(self, validated_data):
        logger.debug("in the serializer's create method")
        logger.debug(validated_data)
        offenses = validated_data.pop("offenses")
        incident = Incident.objects.create(**validated_data)
        offense_objects = Offense.objects.filter(id__in=offenses)
        for offense in offense_objects:
            incident.offenses.add(offense)
        return incident

    class Meta:
        model = Incident
        fields = "__all__"


class IncidentInvolvedPartySerializer(serializers.ModelSerializer):
    class Meta:
        model = IncidentInvolvedParty
        exclude = ("display_sequence",)


class IncidentFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncidentFile
        fields = ("incident", "file",)
