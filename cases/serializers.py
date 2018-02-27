from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import (Officer, Incident,
                     Offense, IncidentInvolvedParty,
                     IncidentFile)
User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "email")
        read_only_fields = ("id",)


class OfficerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Officer
        fields = ("id", "officer_number", "supervisor", "user")
        read_only_fields = ("id",)


class OffenseSerializer(serializers.ModelSerializer):
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
