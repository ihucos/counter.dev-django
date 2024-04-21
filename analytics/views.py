from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from uuid import UUID

from . import models

ITEM_KEYS = ["user", "domain", "date", "dimension", "member", "count"]


def is_valid_uuid(uuid_to_test):

    try:
        uuid_obj = UUID(uuid_to_test)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test


@api_view(["POST"])
def save_count_batch(request):
    #
    # resolve user names
    #
    user_by_username = {
        uuid: user_id
        for uuid, user_id in get_user_model()
        .objects.filter(username__in=request.data["user"])
        .values("username", "id")
    }

    #
    # resolve uuids
    #
    user_by_uuid = {
        uuid: user_id
        for uuid, user_id in models.UserData.objects.filter(
            uuid__in=(is_valid_uuid(i) for i in request.data["user"])
        ).values_list("uuid", "user_id")
    }

    #
    # Create domains
    #
    loaded_domains = models.Domain.objects.bulk_create(
        models.Domain(user_id=user, name=name)
        for (user, name) in set(zip(request.data["user"], request.data["domain"]))
    )
    indexed_domains = {(d.user, d.name) for d in loaded_domains}

    #
    # Create domain counts
    #
    count_items = []
    for item_values in zip(*(request.data[key] for key in ITEM_KEYS)):
        item = {key: item_values[ITEM_KEYS.index(key)] for key in ITEM_KEYS}
        count_items.append(item)

    models.DomainCount.objects.bulk_create(
        DomainCount(
            domain=domains[(i["user"], i["domain"])],
            date=i["date"],
            dimension=i["dimension"],
            member=i["member"],
            count=i["count"],
        )
    )

    #
    # Commpress domain counts
    #

    #
    # Return nothing
    #

    return Response(serializer.data, status=status.HTTP_204_NO_DATA)
