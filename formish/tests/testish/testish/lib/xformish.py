"""
General purpose formish extensions.
"""

from formish import validation, widgets, Form
from convertish.convert import ConvertError


class DateParts(widgets.DateParts):

    def __init__(self, **k):
        k['day_first'] = k.pop('l10n').is_day_first()
        super(DateParts, self).__init__(**k)


class ApproximateDateParts(widgets.DateParts):

    _template = 'ApproximateDateParts'

    def pre_render(self, schema_type, data):
        if data is None:
            return {'year': [''], 'month': [''], 'day': ['']}
        parts = [i for i in data.split('-')]
        parts.extend(['']*(3-len(parts)))
        return {'year': [parts[0]], 'month': [parts[1]], 'day': [parts[2]]}

    def convert(self, schema_type, data):
        # Collect all the parts from the request.
        parts = (data['year'][0].strip(), data['month'][0], data['day'][0])
        if not parts[0] and (parts[1] or parts[2]):
            raise ConvertError("Invalid date")
        elif not parts[1] and parts[2]:
            raise ConvertError("Invalid date")
        # Discard the unspecified parts
        parts = [p for p in parts if p]
        # Ensure they're all integers (don't record the result, we don't care).
        try:
            [int(p) for p in parts]
        except ValueError:
            raise ConvertError("Invalid date")
        return '-'.join(parts)

