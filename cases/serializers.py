import logging
import pytz

from typing import Dict, Union
from datetime import datetime
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers
from rest_framework.settings import api_settings
from cases.models import (Officer, Incident,
                          Offense, IncidentInvolvedParty,
                          IncidentFile, Address, State,
                          City)
from cases.utils import convert_date_string_to_object
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

    def to_internal_value(self, data: Dict) -> Address:
        """
        Converts a python dict object into an Address Django model
        :param data: A dict containing information received from the API client.
        :return: An Address object containing the specified data.
        """
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

    def get_city(self, obj: Union[Dict, Address]) -> str:
        """
        Returns the address' city, regardless of whether or not serialization has occurred.
        :param obj: The dict/Address to extract city from.
        :return: String representing the city name.
        """
        if isinstance(obj, dict):
            return obj['city']['name']
        else:
            return obj.city.name

    def get_state(self, obj: Address) -> str:
        """Returns the address' state abbreviation"""
        return obj.city.state.abbreviation

    class Meta:
        model = Address
        fields = "__all__"


# WTF is this about?
class DateTimeSerializer(serializers.Field):

    def to_representation(self, value: datetime) -> Dict:
        """
        Given a datetime object, serialize it.
        :param value: The datetime object to be serialized.
        :return: A dict representation of the datetime.
        """
        local_datetime = timezone.localtime(value,
                                            timezone=pytz.timezone("US/Eastern"))
        date_string = local_datetime.date().strftime("%Y-%m-%d")
        time_string = local_datetime.time().strftime("%H:%M")
        date_repr = {'date': date_string,
                     'time': time_string}
        return date_repr

    def to_internal_value(self, data: Dict) -> datetime:
        """
        Converts JSON data received from the API client into a python datetime object.
        :param data: Python dict containing the date and time info.
        :return: Python datetime object.
        """
        if isinstance(data, datetime):
            return data
        internal = convert_date_string_to_object(f"{data['date']} {data['time']}")
        return internal


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "email", "username")
        read_only_fields = ("id",)


class OfficerSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    def to_internal_value(self, data: Union[int, str, Dict]) -> Officer:
        """
        For some reason that has now been forgotten, the OfficerSerializer can
        (or at one time could) receive an ID as *either* an int, or a string, OR
        a dict containing information received from the API client. This will be rectified soon.
        :param data: Some form of definition of the Officer to be converted to a python object.
        :return: An officer object.
        """
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
        fields = ("id", "created_timestamp", "updated_timestamp", "officer_number", "supervisor", "user")
        read_only_fields = ("id", "created_timestamp", "updated_timestamp",)

    def create(self, validated_data: Dict) -> Officer:
        """
        Given valid data, creates and returns an Officer object.
        :param validated_data: A python dict that defines the officer.
        :return: Officer object.
        """
        logger.debug(validated_data)
        officer = Officer.objects.create(user=validated_data['user'],
                                         officer_number=validated_data['officer_number'],
                                         supervisor=validated_data['supervisor'])
        return officer


class OffenseSerializer(serializers.ModelSerializer):
    def to_internal_value(self, data: Union[int, str, Dict]):
        """
        For some reason that has now been forgotten, the OffenseSerializer can
        (or at one time could) receive an ID as *either* an int, or a string, OR
        a dict containing information received from the API client. This will be rectified soon.
        :param data: Some form of definition of the Offense to be converted to a python object.
        :return: An Offense object.
        """
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
        read_only_fields = ("id", "created_timestamp", "updated_timestamp")


class IncidentSerializer(serializers.ModelSerializer):
    # Is there a reason I specified all these explicitly?
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

    def create(self, validated_data: Dict) -> Incident:
        """
        Given validated data received from the API client, create the Incident object.
        :param validated_data: A python dict which defines the Incident.
        :return: The Incident object.
        """
        offenses = validated_data.pop("offenses")
        incident = Incident.objects.create(**validated_data)
        for offense in offenses:
            incident.offenses.add(offense)
        return incident

    def update(self, instance: Incident, validated_data: Dict) -> Incident:
        """
        After the input data has been validated, update the Incident object as appropriate.
        :param instance: Instance object to be modified.
        :param validated_data: Python dict containing information to be updated on the Incident.
        :return: The updated Incident object.
        """
        offenses = validated_data.pop("offenses", [])

        for offense in offenses:
            if offense not in instance.offenses.all():
                instance.offenses.add(offense)

        for attr, value in validated_data.items():
            logger.debug(f"Updating attr: {attr} to value:{value}")
            setattr(instance, attr, value)

        instance.save()

        return instance

    def validate_incident_number(self, value: str) -> str:
        """
        Ensures that when creating an incident an incident_number is not being duplicated,
        and when updating an incident that the incident_number is not being changed to one
        that already exists elsewhere.
        :param value: The incident number to validate.
        :return: The validated incident number.
        """
        existing = Incident.objects.filter(incident_number=value).first()
        if existing is not None:
            if not self.instance:
                raise serializers.ValidationError("An Incident with that incident "
                                                  "number already exists")
            if value != self.instance.incident_number:
                raise serializers.ValidationError("An Incident with that incident number already exists")
        return value

    class Meta:
        model = Incident
        fields = "__all__"
        read_only_fields = ("id", "created_timestamp", "updated_timestamp",)


class IncidentInvolvedPartySerializer(serializers.ModelSerializer):
    incident = serializers.PrimaryKeyRelatedField(queryset=Incident.objects.all())
    officer_signed = serializers.PrimaryKeyRelatedField(queryset=Officer.objects.all())
    home_address = AddressSerializer(required=False, allow_null=True)
    employer_address = AddressSerializer(required=False, allow_null=True)

    def create(self, validated_data: Dict, party_type: str) -> IncidentInvolvedParty:
        """
        Given data received from the API client, create an IncidentInvolvedParty object
        of the specified party type.
        :param validated_data: Python dict defining the IncidentInvolvedParty
        :param party_type: A string whose value is either VICTIM or SUSPECT
        :return: The IncidentInvolvedParty object.
        """
        self.instance = IncidentInvolvedParty.objects.create(**validated_data, party_type=party_type)
        return self.instance

    class Meta:
        model = IncidentInvolvedParty
        exclude = ("display_sequence",)
        read_only_fields = ("id", "created_timestamp", "updated_timestamp", "incident", "party_type")


class IncidentFileSerializer(serializers.ModelSerializer):
    file_name = serializers.SerializerMethodField()

    def get_file_name(self, obj: IncidentFile) -> str:
        """
        Returns the name (not the path) on disk of the IncidentFile
        :param obj: The IncidentFile name
        :return: String representing the file's name
        """
        parts = obj.file.name.split("/")
        if len(parts) > 1 and parts[0] == obj.incident.incident_number:
            return obj.file.name.replace(f"{obj.incident.incident_number}/",
                                         "")
        else:
            return obj.file.name

    class Meta:
        model = IncidentFile
        fields = ("id", "created_timestamp", "updated_timestamp", "incident", "file", "file_name")
        read_only_fields = ("id", "created_timestamp", "updated_timestamp",)


def jwt_response_payload_handler(token: str, user: User) -> Dict:
    """
    Returns both the Officer's data, as well as the serialized authentication token.
    :param token: JWT
    :param user: User object that corresponds with the Officer whose data we want.
    :return:
    """
    officer = user.officer_set.first()
    officer_data = OfficerSerializer(officer).data
    return {
        'token': token,
        'officer': officer_data
    }
