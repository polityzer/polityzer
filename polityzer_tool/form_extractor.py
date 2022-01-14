import config
from utils import CandidateUtils
import logging
import json

_Logger = logging.getLogger(__name__)


class FormExtractor:
    def __init__(self) -> None:
        self.candidates = CandidateUtils.load_candidates()

    def extract_formfields(self):
        candidate_fields = dict()
        for candidate, candidate_office, candidate_website in self.candidates:
            _Logger.debug(f"Working on {candidate},{candidate_office}")

            form_fields = CandidateUtils.get_form_fields(candidate, candidate_office)
            _Logger.debug(f"extracted fields for {candidate}-{candidate_office}:{str(form_fields)}")
            candidate_fields[candidate] = {
                "office": candidate_office,
                "website": candidate_website,
                "form_fields": form_fields,
            }
        return candidate_fields


def start():
    analyzer = FormExtractor()
    _Logger.info("Starting form_extractor")
    candidate_fields = analyzer.extract_formfields()
    with open(config.FORM_EXTRACTOR_RESULTS, "w") as f:
        json.dump(candidate_fields, f, indent=1)
    _Logger.info("Completed form_extractor!")
