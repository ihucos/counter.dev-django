from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from uuid import UUID

from . import models

ITEM_KEYS = ["user_id", "user_uuid", "domain", "date", "dimension", "member", "count"]


@api_view(["POST"])
def save_count_batch(request):

    user_by_username = {
        username: user_id
        for username, user_id in get_user_model()
        .objects.filter(username__in=set(i for i in request.data["user_id"] if i))
        .values_list("username", "id")
    }

    user_by_uuid = {
        username: user_id
        for username, user_id in get_user_model()
        .objects.filter(uuid__in=set(i for i in request.data["user_uuid"] if i))
        .values_list("uuid", "id")
    }

    domain_counts = []
    for item_values in zip(*(request.data[key] for key in ITEM_KEYS)):
        item = {key: item_values[ITEM_KEYS.index(key)] for key in ITEM_KEYS}

        user_username = item.pop("user_id")
        user_uuid = item.pop("user_uuid")
        try:
            if user_username:
                user_id = user_by_username[user_username]
            else:
                user_id = user_by_uuid[user_uuid]
        except KeyError:
            continue

        domain_counts.append(
            models.DomainCount(
                user_id=user_id,
                domain=item["domain"],
                date=item["date"],
                dimension=item["dimension"],
                member=item["member"],
                count=item["count"],
            )
        )

    models.DomainCount.objects.bulk_create(domain_counts)

    return Response(status=status.HTTP_204_NO_CONTENT)
