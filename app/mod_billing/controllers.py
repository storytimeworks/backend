from flask import Blueprint, request
from flask_login import current_user
from stripe import Customer, Charge

from app.utils import check_body

mod_billing = Blueprint("billing", __name__, url_prefix="/billing")

@mod_billing.route("/charge", methods=["POST"])
def charge():
    if not check_body(request, ["plan", "transaction"]):
        return errors.missing_charge_parameters()

    plan = int(request.json["plan"])
    token = request.json["transaction"]["id"]

    amount = [499, 2748, 4992][plan]

    customer = Customer.create(
        email=current_user.email,
        source=token
    )

    charge = Charge.create(
        customer=customer.id,
        amount=amount,
        currency="usd",
        description="Flask Charge"
    )

    return "", 204
