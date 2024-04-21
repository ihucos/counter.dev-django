from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db import connection


from uuid import UUID

from . import models

UPDATE_DOMAIN_COUNT_QUERY = """
INSERT INTO counter_domaincount (user_id, domain, date, dimension, member, count)
SELECT * FROM unnest(%s::bigint[], %s::text[], %s::date[], %s::text[], %s::text[], %s::int[])
ON CONFLICT (user_id, domain, date, dimension, member)
DO UPDATE SET count = counter_domaincount.count + EXCLUDED.count;
"""


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

    user_ids = []
    for username, uuid in zip(request.data["user_id"], request.data["user_uuid"]):
        try:
            if username:
                user_id = user_by_username[username]
            else:
                user_id = user_by_uuid[uuid]
        except KeyError:
            continue

        user_ids.append(user_id)

    with connection.cursor() as cursor:
        cursor.execute(
            UPDATE_DOMAIN_COUNT_QUERY,
            [
                user_ids,
                request.data["domain"],
                request.data["date"],
                request.data["dimension"],
                request.data["member"],
                request.data["count"],
            ],
        )

    return Response(status=status.HTTP_204_NO_CONTENT)
