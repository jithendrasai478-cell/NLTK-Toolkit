import sys
import time
import nltk
from flask import Blueprint
from backend.utils.error_handlers import api_success

health_bp = Blueprint("health", __name__, url_prefix="/api/v1")

@health_bp.route("/health", methods=["GET"])
def check_health():
    """Health check endpoint returning system status and resource readiness."""
    # Check essential NLTK resources
    resources = {
        "punkt": True,
        "stopwords": True,
        "vader_lexicon": True,
        "wordnet": True
    }
    for res_name in resources.keys():
        found = False
        for prefix in [f"corpora/{res_name}", f"tokenizers/{res_name}", f"sentiment/{res_name}", f"corpora/{res_name}.zip", f"tokenizers/{res_name}.zip", f"sentiment/{res_name}.zip", f"tokenizers/{res_name}_tab"]:
            try:
                nltk.data.find(prefix)
                found = True
                break
            except LookupError:
                continue
        resources[res_name] = found

    data = {
        "status": "healthy",
        "service": "NLTK Toolkit Backend",
        "api_version": "v1.0.0",
        "python_version": sys.version.split()[0],
        "nltk_resources": resources,
        "timestamp": int(time.time()),
    }
    return api_success(data)
