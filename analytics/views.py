from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from uuid import UUID

from . import models

ITEM_KEYS = ["user", "domain", "date", "dimension", "member", "count"]


def expand_callables(dic_lst):
    new_lst = []
    for dic in dic_lst:
        for key in dic.keys():
            if callable(dic[key]):
                try:
                    dic[key] = dic[key]()
                except KeyError:
                    continue
                new_lst.append(dic)
    return new_lst


@api_view(["POST"])
def save_count_batch(request):

    indexed_domains = {}
    domain_count = []
    used_uuids = set()
    used_usernames = set()

    for item_values in zip(*(request.data[key] for key in ITEM_KEYS)):
        item = {key: item_values[ITEM_KEYS.index(key)] for key in ITEM_KEYS}

        domain_count.append(
            dict(
                # domain_id=lambda item=item: indexed_domains[(item["user"], item["domain"])],
                domain_id=(item["user"], item["domain"]),
                date=item["date"],
                dimension=item["dimension"],
                member=item["member"],
                count=item["count"],
            )
        )

        # domain_key = (item["user"]), item["domain"]
        # if not domain_key in indexed_domains:
        #     indexed_domains[domain_key] = {
        #         "user_id": lambda item=item: user_by_user_key[item["user"]],
        #         "name": item["domain"],
        #     }
        try:
            user_id = user_by_user_key[item["user"]]
        except KeyError:
            continue


        try:
            uuid_obj = UUID(item["user"])
        except ValueError:
            is_uuid = False
        else:
            is_uuid = str(uuid_obj) == item["user"]

        if is_uuid:
            used_uuids.add(item["user"])
        else:
            used_usernames.add(item["user"])

    user_by_username = {
        username: user_id
        for username, user_id in get_user_model()
        .objects.filter(username__in=used_usernames)
        .values_list("username", "id")
    }
    user_by_uuid = {
        uuid: user_id
        for uuid, user_id in models.UserData.objects.filter(
            uuid__in=used_uuids,
        ).values_list("uuid", "user_id")
    }
    user_by_user_key = {**user_by_username, **user_by_uuid}

    indexed_domains = {
        (d.user.id, d.name): d
        for d in models.Domain.objects.bulk_create(
            (models.Domain(**i) for i in expand_callables(indexed_domains.values())),
            ignore_conflicts=True
        )
    }

    assert 0, (
        indexed_domains,

        domain_count,
               )
    models.DomainCount.objects.bulk_create(
        models.DomainCount(**i) for i in expand_callables(domain_count)
    )

    # #
    # # Find out which user keys are uuids and which are usernames
    # #
    # used_uuids = set()
    # used_usernames = set()
    # for user_key in request.data["user"]:
    #
    #     try:
    #         uuid_obj = UUID(user_key)
    #     except ValueError:
    #         is_uuid = False
    #     else:
    #         is_uuid = str(uuid_obj) == user_key
    #
    #     if is_uuid:
    #         used_uuids.add(user_key)
    #     else:
    #         used_usernames.add(user_key)
    #
    # #
    # # Resolve user names and uuids to an user id
    # #
    # user_by_username = {
    #     username: user_id
    #     for username, user_id in get_user_model()
    #     .objects.filter(username__in=used_usernames)
    #     .values_list("username", "id")
    # }
    # user_by_uuid = {
    #     uuid: user_id
    #     for uuid, user_id in models.UserData.objects.filter(
    #         uuid__in=used_uuids,
    #     ).values_list("uuid", "user_id")
    # }
    # user_by_user_key = {**user_by_username, **user_by_uuid}
    #
    # #
    # # Create domains
    # #
    # domains = set()
    # for (user_key, name) in set(zip(request.data["user"], request.data["domain"])):
    #
    #     try:
    #         user_id = user_by_user_key[user_key]
    #     except KeyError:
    #         continue
    #     domains.add((user_id, name))
    # assert 0, domains
    # indexed_domains = {
    #     (d.user, d.name): d for d in models.Domain.objects.bulk_create(domain_objs)
    # }
    #
    # #
    # # Create domain counts
    # #
    # domain_count_objs = []
    # for item_values in zip(*(request.data[key] for key in ITEM_KEYS)):
    #     item = {key: item_values[ITEM_KEYS.index(key)] for key in ITEM_KEYS}
    #
    #     try:
    #         domain_obj = indexed_domains[(item["user"], item["domain"])]
    #     except KeyError:
    #         # No such user
    #         continue
    #
    #     domain_count_objs.append(
    #         domain=domain_obj,
    #         date=item["date"],
    #         dimension=item["dimension"],
    #         member=item["member"],
    #         count=item["count"],
    #     )
    #
    # models.DomainCount.objects.bulk_create(domain_count_objs)
    # #
    # # Commpress domain counts
    # #
    #
    # #
    # # Return nothing
    # #

    return Response("", status=status.HTTP_204_NO_CONTENT)
