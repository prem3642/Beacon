# -*- coding: utf-8 -*-
# Third Party Stuff
from django.contrib.admin import FieldListFilter


class NullFieldListFilter(FieldListFilter):
    """
    Use this filter to show a field filter as All or Null
    e.g. list_filter = ('field_name', ('field_name2', NullFieldListFilter))
    """

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg = "%s__isnull" % field_path
        self.lookup_val = params.get(self.lookup_kwarg)
        super().__init__(field, request, params, model, model_admin, field_path)

    def expected_parameters(self):
        return [self.lookup_kwarg]

    def choices(self, changelist):
        yield {
            "selected": self.lookup_val is None,
            "query_string": changelist.get_query_string({self.lookup_kwarg: None}),
            "display": "All",
        }
        if self.field.null:
            yield {
                "selected": self.lookup_val == "True",
                "query_string": changelist.get_query_string(
                    {self.lookup_kwarg: "True"}
                ),
                "display": "Null",
            }
