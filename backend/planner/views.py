import json
import logging
import os

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from planner.errors import PlanError
from planner.services.plan import build_plan

logger = logging.getLogger(__name__)


@require_GET
def config_view(request):
    # Tiles load in the browser, so this key has to be readable there.
    # Treat it as a publishable key and restrict the domains in Stadia.
    response = JsonResponse({"map_key": os.environ.get("STADIA_API_KEY", "").strip()})
    response["Cache-Control"] = "no-store"
    return response


@csrf_exempt
@require_POST
def plan_view(request):
    if request.content_type != "application/json":
        return JsonResponse({"error": "Request body must be JSON."}, status=415)

    try:
        body = json.loads(request.body.decode() or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Request body must be JSON."}, status=400)

    try:
        result = build_plan(body)
    except PlanError as exc:
        return JsonResponse({"error": str(exc)}, status=exc.status)
    except Exception:
        logger.exception("plan failed")
        return JsonResponse({"error": "Something went wrong while building the plan."}, status=500)
    return JsonResponse(result)
