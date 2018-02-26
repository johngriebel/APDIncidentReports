from django import template
register = template.Library()


def build_prefix(value, arg):
    return f"{value}-{arg}-"

register.filter("build_prefix", build_prefix)
