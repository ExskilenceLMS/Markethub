from exceptions import ValidationException


def validate_requested_quantity(quantity: int) -> None:
    if quantity <= 0:
        raise ValidationException("Quantity must be greater than zero", details=["quantity"])
