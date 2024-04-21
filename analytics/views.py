
import asyncio
from django.http import HttpResponse
from django.views import View


class SaveStatItems(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse("Hello async world!")


    ```
       INSERT INTO HotReport (user_identify, domain, date, dimension, member, count)
       SELECT * FROM UNNEST($1::TEXT[], $2::TEXT[], $3::TEXT[], $4::TEXT[], $5::TEXT[], $6::int[])
       ON CONFLICT (user_identify, domain, date, dimension, member)
       DO UPDATE SET count = HotReport.count + 1;`)
    ```
