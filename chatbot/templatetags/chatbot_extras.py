from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def sub(value, arg):
    """Subtract the arg from the value."""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        try:
            return Decimal(value) - Decimal(arg)
        except:
            return 0

@register.filter
def add(value, arg):
    """Add the arg to the value."""
    try:
        return float(value) + float(arg)
    except (ValueError, TypeError):
        try:
            return Decimal(value) + Decimal(arg)
        except:
            return 0

@register.filter
def mul(value, arg):
    """Multiply the value by the arg."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        try:
            return Decimal(value) * Decimal(arg)
        except:
            return 0

@register.filter
def div(value, arg):
    """Divide the value by the arg."""
    try:
        return float(value) / float(arg) if float(arg) != 0 else 0
    except (ValueError, TypeError):
        try:
            return Decimal(value) / Decimal(arg) if Decimal(arg) != 0 else 0
        except:
            return 0

@register.filter
def float(value):
    """Convert value to float."""
    try:
        return __builtins__['float'](value)
    except (ValueError, TypeError):
        return 0