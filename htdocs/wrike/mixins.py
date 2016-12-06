from datetime import datetime
import pytz
import logging

from django.shortcuts import render, redirect
from django.views.generic import TemplateView


logger = logging.getLogger(__name__)


class FilterMixin(TemplateView):

    def post(self, request, *args, **kwargs):
        start = request.POST.get("start", None)
        end = request.POST.get("end", None)

        if start:
            start_date = datetime.strptime(start, "%Y-%m-%d")
            start = start_date.replace(tzinfo=pytz.UTC)
        if end:
            end_date = datetime.strptime(end, "%Y-%m-%d")
            end = end_date.replace(tzinfo=pytz.UTC)

        kwargs['criteria'] = {'start': start, 'end': end}
        context = self.get_context_data(**kwargs)
        return super(FilterMixin, self).render_to_response(context)