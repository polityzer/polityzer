import utils, config
from utils import CandidateUtils, LinkExtractor
import json
import logging
from urllib.parse import urljoin

_Logger = logging.getLogger(__name__)


class Website_LinkExtractor:
    def __init__(self) -> None:
        self.candidates = CandidateUtils.load_candidates()

    def link_extractor(self):
        candidate_links = dict()
        for candidate, candidate_office, candidate_website in self.candidates:
            _Logger.debug(f"Working on {candidate},{candidate_office}")
            inbound_links = set()
            outbound_links = set()
            inbound_counter = 0
            outbound_counter = 0

            for webpage in CandidateUtils.get_webpages(candidate, candidate_office):
                links_in_page = LinkExtractor.get_links(webpage)
                for link in links_in_page:

                    # if the link is relative, it is inbound.
                    if not utils.isAbsolute(link):
                        link = urljoin(candidate_website, link)
                        inbound_links.add(link)
                        inbound_counter += 1
                        continue

                    # if it is not relative, check if it is same domain
                    if utils.isSameDomain(link, candidate_website):
                        inbound_links.add(link)
                        inbound_counter += 1
                    else:
                        outbound_links.add(link)
                        outbound_counter += 1
            candidate_links[candidate] = {
                "office": candidate_office,
                "website": candidate_website,
                "inbound_links": list(inbound_links),
                "outbound_links": list(outbound_links),
            }
            _Logger.debug(f"{inbound_counter} inbound links, {outbound_counter} outbound links")
        return candidate_links


def start():
    analyzer = Website_LinkExtractor()
    _Logger.info("Starting link_extractor")
    candidate_links = analyzer.link_extractor()
    with open(config.LINK_EXTRACTOR_RESULTS, "w") as f:
        json.dump(candidate_links, f, indent=1)
    _Logger.info("Completed link_extractor!")
