from rest_framework import serializers

from froide.publicbody.api_views import SimplePublicBodySerializer

from .models import Subject, State, Curriculum


class SubjectSerializer(serializers.HyperlinkedModelSerializer):
    resource_uri = serializers.HyperlinkedIdentityField(
        view_name="api:examsubject-detail", lookup_field="pk"
    )

    class Meta:
        model = Subject
        fields = ("resource_uri", "id", "name", "slug")


class SimpleStateSerializer(serializers.HyperlinkedModelSerializer):
    resource_uri = serializers.HyperlinkedIdentityField(
        view_name="api:examstate-detail", lookup_field="pk"
    )

    class Meta:
        model = State
        fields = (
            "resource_uri",
            "id",
            "name",
            "slug",
            "description",
            "legal_status",
        )


class StateSerializer(serializers.HyperlinkedModelSerializer):
    resource_uri = serializers.HyperlinkedIdentityField(
        view_name="api:examstate-detail", lookup_field="pk"
    )
    publicbody = SimplePublicBodySerializer(read_only=True)

    class Meta:
        model = State
        fields = (
            "resource_uri",
            "id",
            "name",
            "slug",
            "publicbody",
            "description",
            "legal_status",
        )


class CurriculumSerializer(serializers.HyperlinkedModelSerializer):
    resource_uri = serializers.HyperlinkedIdentityField(
        view_name="api:examcurriculum-detail", lookup_field="pk"
    )
    subjects = SubjectSerializer(read_only=True, many=True)
    state = SimpleStateSerializer(read_only=True)

    class Meta:
        model = Curriculum
        fields = (
            "resource_uri",
            "id",
            "name",
            "slug",
            "start_year",
            "end_year",
            "subjects",
            "state",
        )
