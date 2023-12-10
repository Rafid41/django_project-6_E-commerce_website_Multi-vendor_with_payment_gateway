from django import template
from App_Order.models import Order

register = template.Library()


@register.filter
def cart_total(user):
    # ei user er payment kora sara kono order ase kina dekhbe
    order = Order.objects.filter(user=user, ordered= False)

    if order.exists():
        return order[0].orderitems.count()
    else:
        return 0