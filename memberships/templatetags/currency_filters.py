from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


@register.filter
def cop_currency(value):
    try:
        amount = Decimal(value)
    except (TypeError, InvalidOperation):
        return "0 COP"

    integer_amount = int(amount)
    formatted = f"{integer_amount:,}".replace(",", ".")
    return f"{formatted} COP"
