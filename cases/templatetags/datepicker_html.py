from django import template
register = template.Library()

DATETIME_HTML = (
"""
<div class="fieldWrapper">
    <div class="input-group date" id="{field_name}" data-target-input="#id_{field_name}">
        <input id="id_{field_name}" name="{field_name}" type="text" class="form-control datetimepicker-input" data-target="#{field_name}"/>
        <div class="input-group-append" data-target="#{field_name}" data-toggle="datetimepicker">
            <div class="input-group-text"><i class="fa fa-calendar"></i></div>
        </div>
    </div>
    <script type="text/javascript">
        $(function () {{
            $('#{field_name}').datetimepicker({{
                format: "MM/DD/YYYY HH:mm",
                inline: true,
                sideBySide: true,
                icons: {{
                    time: "fa fa-clock-o",
                    date: "fa fa-calendar",
                    up: "fa fa-arrow-up",
                    down: "fa fa-arrow-down"
                }}
            }});
        }});
    </script>
</div>
""")


def datepicker_html(value, *args, **kwargs):
    print(f"Which field? {value.name}")
    substituted_html = DATETIME_HTML.format(field_name=value.name)
    return substituted_html

register.filter('datepicker_html', datepicker_html)

