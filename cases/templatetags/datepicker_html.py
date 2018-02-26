import logging
import json
from django.utils import timezone
from django import template
register = template.Library()
logger = logging.getLogger('cases')

DATETIME_HTML = (
"""
<div class="input-group date" id="{field_name}" data-target-input="#id_{field_name}">
    <input id="id_{field_name}" name="{field_name}" type="text" class="form-control datetimepicker-input" data-target="#{field_name}"/>
    <div class="input-group-append" data-target="#{field_name}" data-toggle="datetimepicker">
        <div class="input-group-text"><i class="fa fa-calendar"></i></div>
    </div>
</div>
<script type="text/javascript">
    $(function () {{
        $('#{field_name}').datetimepicker({options});
    }});
</script>
""")


def datepicker_html(value, prefix=None):
    logger.debug(f"Which field? {value.name}")
    logger.debug(f"Prefix: {prefix}")

    if prefix:
        field_name = prefix + value.name
    else:
        field_name = value.name

    logger.debug(f"Full field name: {field_name}")

    pyt_strformat = "%m/%d/%Y"
    if value.form.is_bound:
        date_time_obj = value.form.cleaned_data[value.name]
    else:
        date_time_obj = None
    if "datetime" in value.name:
        date_time_format = "MM/DD/YYYY HH:mm"
        pyt_strformat += " %H:%m"

        if date_time_obj is None:
            date_time_obj = timezone.now()

        options = {'format': date_time_format,
                   'inline': True,
                   'sideBySide': True,
                   'defaultDate': date_time_obj.strftime(pyt_strformat),
                   'icons': {'time': "fa fa-clock-o",
                             'date': "fa fa-calendar",
                             'up': "fa fa-arrow-up",
                             'down': "fa fa-arrow-down"
                             }
                   }
    else:
        if date_time_obj:
            date_value = date_time_obj.strftime(pyt_strformat)
        else:
            date_value = "null"
        options = {'format': "L",
                   'date': date_value}

    substituted_html = DATETIME_HTML.format(field_name=field_name,
                                            options=json.dumps(options))
    return substituted_html

register.filter('datepicker_html', datepicker_html)

