import logging
import pytz
from datetime import datetime
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers
from rest_framework.settings import api_settings
from rest_framework.fields import empty
from cases.models import (Officer, Incident,
                          Offense, IncidentInvolvedParty,
                          IncidentFile, Address, State,
                          City)
from cases.utils import (convert_date_string_to_object,
                         handle_incident_foreign_keys_for_creation,
                         parse_and_create_address)
User = get_user_model()
logger = logging.getLogger('cases')


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ("abbreviation",)


class CitySerializer(serializers.ModelSerializer):
    state = StateSerializer()

    class Meta:
        model = City
        fields = ("name", "state")


class AddressSerializer(serializers.ModelSerializer):

    city = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()

    def to_internal_value(self, data):
        state_abbr = data.pop("state")
        state, created = State.objects.get_or_create(abbreviation=state_abbr)

        if created:
            logger.debug(f"Created a new state: {state}")

        city_name = data.pop("city")
        city, created = City.objects.get_or_create(name=city_name, state=state)

        if created:
            logger.debug(f"Created a new city: {city}")

        address = Address(**data, city=city)
        address.save()
        return address

    def get_city(self, obj):
        if isinstance(obj, dict):
            logger.debug(obj.keys())
            return obj['city']['name']
        else:
            return obj.city.name

    def get_state(self, obj):
        return obj.city.state.abbreviation

    class Meta:
        model = Address
        fields = "__all__"


class DateTimeSerializer(serializers.Field):

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
        internal = convert_date_string_to_object(f"{data['date']} {data['time']}")
        logger.debug(f"INTERNAL VALUE: {type(internal)}")
        return internal


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "email", "username")
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
    report_datetime = DateTimeSerializer()
    approved_datetime = DateTimeSerializer(required=False, allow_null=True)
    reviewed_datetime = DateTimeSerializer(required=False, allow_null=True)
    earliest_occurrence_datetime = DateTimeSerializer()
    latest_occurrence_datetime = DateTimeSerializer()

    def create(self, validated_data):
        offenses = validated_data.pop("offenses")
        incident = Incident.objects.create(**validated_data)
        for offense in offenses:
            incident.offenses.add(offense)
        return incident

    def update(self, instance, validated_data):
        offenses = validated_data.pop("offenses", [])

        for offense in offenses:
            if offense not in instance.offenses.all():
                instance.offenses.add(offense)

        for attr, value in validated_data.items():
            logger.debug(f"Updating attr: {attr} to value:{value}")
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
    incident = serializers.PrimaryKeyRelatedField(queryset=Incident.objects.all())
    officer_signed = serializers.PrimaryKeyRelatedField(queryset=Officer.objects.all())
    home_address = AddressSerializer(required=False, allow_null=True)
    employer_address = AddressSerializer(required=False, allow_null=True)

    def update(self, instance, validated_data):
        logger.debug(f"Validated data: {validated_data}")
        logger.debug(f"instance.ID: {instance.id}")
        # home_address = validated_data.pop("home_address", None)
        # employer_address = validated_data.pop("employer_address", None)

        for attr in validated_data:
            setattr(instance, attr, validated_data[attr])

        instance.save()
        return instance

    def create(self, validated_data, party_type):
        self.instance = IncidentInvolvedParty.objects.create(**validated_data, party_type=party_type)

    class Meta:
        model = IncidentInvolvedParty
        exclude = ("display_sequence",)
        read_only_fields = ("id", "incident", "party_type")


class IncidentFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncidentFile
        fields = ("incident", "file",)
