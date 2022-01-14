import config, utils
from utils import CandidateUtils, LinkExtractor
import os
import logging
import json

_Logger = logging.getLogger(__name__)


class Privacy_Policy_Check:
    bag_of_words = ["privacy", "terms", "conditions", "notice", "statement", "disclosure"]

    def __init__(self):
        # self.save_links = config.SAVE_PRIVACY_POLICY_LINKS
        self.candidates = CandidateUtils.load_candidates()

    # def get_candidate_website_folder(self, candidate_name):
    #     html_folder = config.HTML_FOLDER
    #     website_path = os.path.join(html_folder, candidate_name)
    #     return website_path

    # def get_webpages(self, website_path):
    #     if not os.path.isdir(website_path):
    #         return
    #     for webpage in os.listdir(website_path):
    #         yield os.path.join(website_path, webpage)

    def get_privacy_links(self):
        utils.create_results_folder()

        # to save privacy policy files in a separate folder
        if config.COPY_PRIVACY_POLICY_FILE:
            import shutil

            utils.create_privacy_policy_folder()
            keywords = ["privacy", "policy"]

        privacy_links = set()
        candidate_map = dict()
        for candidate, candidate_office, website in self.candidates:
            _Logger.debug(f"Working on {candidate}, {candidate_office}")
            privacy_flag = False
            privacy_policy_moved = False
            for webpage in CandidateUtils.get_webpages(candidate, candidate_office):
                links_with_texts = LinkExtractor.get_links_with_texts(webpage)
                for link in links_with_texts:
                    privacy_link = [
                        v
                        for k, v in link.items()
                        for word in self.bag_of_words
                        if word.lower() in k.lower() or word.lower() in v.lower()
                    ]
                    if privacy_link:
                        privacy_flag = True
                        privacy_links.add(privacy_link[0])

                if config.COPY_PRIVACY_POLICY_FILE and not privacy_policy_moved:
                    is_file = True
                    html_file = webpage.split(os.path.sep)[-1]
                    for keyword in keywords:
                        if keyword not in html_file:
                            is_file = False
                            break
                    if is_file:
                        office_folder = os.path.join(config.PRIVACY_POLICY_FOLDER, candidate_office)
                        if not os.path.isdir(office_folder):
                            os.mkdir(office_folder)
                        shutil.copy(webpage, office_folder)
                        privacy_policy_moved = True

            candidate_map[candidate] = {
                "office": candidate_office,
                "website": website,
                "privacy_links": list(privacy_links),
                "privacy_present": privacy_flag,
            }
        return candidate_map


def start():
    analyzer = Privacy_Policy_Check()
    _Logger.info("Starting privacy policy presence analysis.")
    candidate_with_privacy_links = analyzer.get_privacy_links()
    with open(config.PRIVACY_POLICY_RESULTS, "w") as f:
        json.dump(candidate_with_privacy_links, f, indent=1)

    _Logger.info(f"Privacy Policy presence analysis completed. Results at {config.PRIVACY_POLICY_RESULTS}..")
