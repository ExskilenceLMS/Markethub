from flask import Blueprint

from services.health_service import HealthService
from utils.response import success_response

health_bp = Blueprint("health", __name__, url_prefix="/api")


@health_bp.get("/health")
def health():
    payload = HealthService().get_status()
    return success_response(data=payload, message="Service is healthy")
