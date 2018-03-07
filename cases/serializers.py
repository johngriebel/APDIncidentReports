import logging
import pytz
from datetime import datetime
from django.contrib.auth import get_user_model
from django.utils import timezone
from address.models import _to_python, Address
from rest_framework import serializers
from rest_framework.settings import api_settings
from rest_framework.fields import empty
from .models import (Officer, Incident,
                     Offense, IncidentInvolvedParty,
                     IncidentFile)
from .utils import convert_date_string_to_object
User = get_user_model()
logger = logging.getLogger('cases')


class AddressSerializer(serializers.ModelSerializer):

    def run_validation(self, data=empty):
        if data != empty:
            address_obj = _to_python(data)
            return address_obj

    class Meta:
        model = Address
        fields = "__all__"


class DateTimeAsObjectField(serializers.Field):

    def to_representation(self, value):
        local_datetime = timezone.localtime(value,
                                            timezone=pytz.timezone("US/Eastern"))
        date_string = local_datetime.date().strftime("%Y-%m-%d")
        time_string = local_datetime.time().strftime("%H:%M")
        date_obj = {'date': date_string,
                    'time': time_string}
        return date_obj

    def to_internal_value(self, data):
        if isinstance(data, datetime):
            return data
        logger.debug("ARMADILLO")
        internal = convert_date_string_to_object(f"{data['date']} {data['time']}")
        logger.debug(f"INTERNAL VALUE: {type(internal)}")
        return internal


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "email")
        read_only_fields = ("id",)


class OfficerSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    def to_internal_value(self, data):
        if isinstance(data, int) or (isinstance(data, str) and data.isdigit()):
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
        if isinstance(data, int) or (isinstance(data, str) and data.isdigit()):
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
    report_datetime = DateTimeAsObjectField()
    approved_datetime = DateTimeAsObjectField(required=False, allow_null=True)
    earliest_occurrence_datetime = DateTimeAsObjectField()
    latest_occurrence_datetime = DateTimeAsObjectField()

    def get_report_datetime(self, obj: Incident):
        # TODO: Make the timezone a settingzz
        local_datetime = timezone.localtime(obj.report_datetime,
                                            timezone=pytz.timezone("US/Eastern"))
        date_string = local_datetime.date().strftime("%Y-%m-%d")
        time_string = local_datetime.time().strftime("%H:%M")
        logger.debug(f"Date String: {date_string}")
        date_obj = {'date': date_string,
                    'time': time_string}
        return date_obj

    def create(self, validated_data):
        offenses = validated_data.pop("offenses")
        logger.debug(f"Validated data: {validated_data}")

        for field in validated_data.keys():
            if "officer" in field or "supervisor" in field:
                validated_data[field] = Officer.objects.get(id=validated_data[field])

        incident = Incident.objects.create(**validated_data)
        offense_objects = Offense.objects.filter(id__in=offenses)
        for offense in offense_objects:
            incident.offenses.add(offense)
        return incident

    def update(self, instance, validated_data):
        offenses = validated_data.pop("offenses")
        offense_objects = Offense.objects.filter(id__in=offenses)
        for offense in offense_objects:
            if offense not in instance.offenses.all():
                instance.offenses.add(offense)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance

    def validate_incident_number(self, value):
        existing = Incident.objects.filter(incident_number=value).first()
        if existing is not None:
            if not self.instance:
                raise serializers.ValidationError("An Incident with that incident "
                                                  "number already exists")
            if value != self.instance.incident_number:
                    raise serializers.ValidationError("An Incident with that incident "
                                                      "number already exists")
            else:
                return value

    class Meta:
        model = Incident
        fields = "__all__"


class IncidentInvolvedPartySerializer(serializers.ModelSerializer):
    officer_signed = OfficerSerializer()
    home_address = AddressSerializer(required=False)
    employer_address = AddressSerializer(required=False)

    def create(self, validated_data):
        for addr in ["home_address", "employer_address"]:
            address_attrs = validated_data.get(addr)
            if address_attrs is not None:
                address_obj = _to_python(validated_data.pop(addr))
                validated_data[addr] = address_obj

        validated_data['incident'] = Incident.objects.get(pk=validated_data['incident'])
        validated_data['officer_signed'] = Officer.objects.get(pk=validated_data['officer_signed'])

        self.instance = IncidentInvolvedParty.objects.create(**validated_data)

    class Meta:
        model = IncidentInvolvedParty
        exclude = ("display_sequence",)
        read_only_fields = ("id", "incident","party_type")


class IncidentFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncidentFile
        fields = ("incident", "file",)
