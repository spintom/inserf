from django import template

register = template.Library()


def _format_thousands(value: int) -> str:
    return f"{value:,}".replace(",", ".")


@register.filter(name="clp")
def clp(value):
    """
    Format a number as Chilean Peso (CLP) without decimals and with thousands separator.
    Examples:
      1234.56 -> $1.235
      1000000 -> $1.000.000
    """
    if value is None:
        return "$0"
    try:
        # Convert to integer pesos (round to nearest)
        amount = int(round(float(value)))
        return f"${_format_thousands(amount)}"
    except (ValueError, TypeError):
        return f"${value}"
