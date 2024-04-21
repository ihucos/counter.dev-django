from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from uuid import UUID

from . import models

ITEM_KEYS = ["user", "domain", "date", "dimension", "member", "count"]


@api_view(["POST"])
def save_count_batch(request):

    #
    # Find out which user keys are uuids and which are usernames
    #
    used_uuids = set()
    used_usernames = set()
    for user_key in request.data["user"]:

        try:
            uuid_obj = UUID(user_key)
        except ValueError:
            is_uuid = False
        else:
            is_uuid = str(uuid_obj) == user_key

        if is_uuid:
            used_uuids.add(user_key)
        else:
            used_usernames.add(user_key)

    #
    # Resolve user names and uuids to an user id
    #
    user_by_username = {
        uuid: user_id
        for uuid, user_id in get_user_model()
        .objects.filter(username__in=used_usernames)
        .values("username", "id")
    }
    user_by_uuid = {
        uuid: user_id
        for uuid, user_id in models.UserData.objects.filter(
            uuid__in=used_uuids,
        ).values_list("uuid", "user_id")
    }
    user_by_user_key = {**user_by_username, **user_by_uuid}

    #
    # Create domains
    #
    domain_objs = []
    for (user_key, name) in set(zip(request.data["user"], request.data["domain"])):

        try:
            user_id = user_by_user_key[user_key]
        except KeyError:
            continue
        domain_objs.append(models.Domain(user_id=user_id, name=name))
    indexed_domains = {
        (d.user, d.name) for d in models.Domain.objects.bulk_create(domain_objs)
    }

    #
    # Create domain counts
    #
    domain_count_objs = []
    for item_values in zip(*(request.data[key] for key in ITEM_KEYS)):
        item = {key: item_values[ITEM_KEYS.index(key)] for key in ITEM_KEYS}
        domain_count_objs.append(
            domain=indexed_domains[(item["user"], item["domain"])],
            date=item["date"],
            dimension=item["dimension"],
            member=item["member"],
            count=item["count"],
        )

    models.DomainCount.objects.bulk_create(domain_count_objs)
    #
    # Commpress domain counts
    #

    #
    # Return nothing
    #

    return Response(serializer.data, status=status.HTTP_204_NO_DATA)
