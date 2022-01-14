from colorlog import ColoredFormatter
from urllib.parse import urlparse
import logging
import os
import tldextract
import csv
import time
import shutil
import hashlib
from bs4 import BeautifulSoup as bs

import config


def create_logger(filename="logfile.log"):
    logs_folder = config.LOGS_FOLDER
    if not os.path.isdir(logs_folder):
        os.mkdir(logs_folder)
    randomizer = str(int(time.time())) + "."
    filename = randomizer.join(filename.split("."))
    log_file = os.path.join(logs_folder, filename)

    # log config copied from HomeEndorser
    logging.basicConfig(
        format="%(levelname)s:%(message)s",
        level=logging.DEBUG,
        handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
    )
    fmt = "%(asctime)s %(levelname)s (%(threadName)s) [%(name)s] %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    colorfmt = f"%(log_color)s{fmt}%(reset)s"
    logging.getLogger().handlers[0].setFormatter(
        ColoredFormatter(
            colorfmt,
            datefmt=datefmt,
            reset=True,
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red",
            },
        )
    )


create_logger()
_Logger = logging.getLogger(__name__)


def configure_ChromeDriver():
    """Setting up the chromedriver"""

    # system = platform.system()
    chromedriver_folder = config.CHROMEDRIVER_FOLDER
    chromedriver_path = config.CHROMEDRIVER_PATH

    if not os.path.isdir(chromedriver_folder):
        os.mkdir(chromedriver_folder)
    if not os.path.isfile(chromedriver_path):
        _Logger.debug(f"Chromedriver not found. Downloading and installing at {chromedriver_folder}")
        from chromedriver import installer

        installer.install(path=chromedriver_folder)

    if os.path.isfile(chromedriver_path):
        if os.access(chromedriver_path, os.X_OK):
            _Logger.debug("Chromedriver setup successful")
            return True
        else:
            os.chmod(chromedriver_path, 0o744)
            return os.access(chromedriver_path, os.X_OK)
    else:
        _Logger.error(f"Chromedriver setup failed. Download the proper chromedriver file at {chromedriver_folder}")
        return False


# util methods to perform various small checks
def create_html_folder():
    """Checks if an html folder to store html files already exists. Creates the folder if it is not already created"""

    if not os.path.exists(config.HTML_FOLDER):
        os.mkdir(config.HTML_FOLDER)
        return False
    else:
        return True


def get_download_status():
    """returns True if there are downloaded folders in html/ else returns False"""
    if not create_html_folder():
        return False
    html_folder = config.HTML_FOLDER
    downloaded_folders = list(os.listdir(html_folder))
    if downloaded_folders:
        return True
    else:
        return False


# util functions to return file handler objects
def get_database_file():
    """returns the database file handler to write downloaded entries"""

    if not os.path.isdir(config.DATABASE_FOLDER):
        os.mkdir(config.DATABASE_FOLDER)
    if os.path.isfile(config.DATABASE_FILE):
        db_file = open(config.DATABASE_FILE, "a")
        writer = csv.writer(db_file, delimiter=",")
    else:
        db_file = open(config.DATABASE_FILE, "w")
        writer = csv.writer(db_file, delimiter=",")
        writer.writerow(["name", "url", "filepath", "depth"])
    return writer


def get_error_file():
    """returns the error file handler to log errors"""

    if os.path.isfile(config.ERROR_FILEPATH):
        db_file = open(config.ERROR_FILEPATH, "a")
        writer = csv.writer(db_file, delimiter=",")
    else:
        db_file = open(config.ERROR_FILEPATH, "w")
        writer = csv.writer(db_file, delimiter=",")
        writer.writerow(["name", "url", "depth", "error_msg"])
    return writer


def create_results_folder():
    """Checks if a results folder already exists. Creates the folder if it is not already created"""
    if not os.path.exists(config.RESULTS_FOLDER):
        os.mkdir(config.RESULTS_FOLDER)
        return False
    else:
        return True


def create_privacy_policy_folder():
    """Checks if a privacy policy folder already exists. Creates the folder if it is not already created"""
    if not os.path.exists(config.PRIVACY_POLICY_FOLDER):
        os.mkdir(config.PRIVACY_POLICY_FOLDER)
        return False
    else:
        return True


# util functions to perform various url checks
def skipUrl(url):
    """Check if a given url needs to be skipped by default e.g. mailto: or tel: urls or in-page links"""

    url = url.strip()
    if url.startswith("tel:") or url.startswith("mailto:") or url.startswith("#"):
        return True
    return False


def isAbsolute(url):
    """Change a relative url to an absolute url"""

    return bool(urlparse(url).netloc)


def isSameDomain(source_link, dest_link):
    """Check if a given 'dest_link' belongs to the same domain. This is to make sure that the downloader downloads links that belong to the same domain and not deviate elsewhere"""

    if dest_link is None or len(dest_link) == 0:
        return False
    source_link = source_link.lower()
    dest_link = dest_link.lower()

    dest_domain = urlparse(dest_link).netloc
    source_domain = urlparse(source_link).netloc

    if not isAbsolute(dest_link):
        return True

    if dest_domain == source_domain:
        return True

    dest_root = tldextract.extract(dest_domain).domain
    source_root = tldextract.extract(source_domain).domain
    return dest_root == source_root


# moving attachments to a folder in root
def attachment_cleaner():
    """Move attachments to attachments folder"""

    attachment_folder = "attachments"
    if not os.path.isdir(attachment_folder):
        os.mkdir(attachment_folder)

    for filename in os.listdir(os.getcwd()):
        if os.path.isdir(filename):
            continue
        # allowed_extensions = ['.py','.sh']

        if filename.endswith(".py") or filename.endswith(".sh"):
            continue
        randomized_filename = "".join([filename, str(time.time())])
        os.rename(filename, randomized_filename)
        _Logger.debug(f"moving {randomized_filename} to {attachment_folder}")
        shutil.move(randomized_filename, attachment_folder)


class LinkExtractor:
    """returns a list containing links from a single webpage"""

    @staticmethod
    def get_links(webpage) -> list:
        with open(webpage) as html:
            try:
                soup = bs(html, "html.parser")
            except Exception:
                return []
        links = soup.find_all("a")
        all_links = []
        for link in links:
            if link is None:
                continue
            # href = link.xpath("@href").extract_first()
            href = link.get("href")
            if not href:
                continue
            if skipUrl(href):
                continue
            if href not in all_links:
                all_links.append(href)
        return all_links

    @staticmethod
    def get_links_with_texts(webpage) -> list[dict]:
        """returns a list containing linktext:links from a single webpage"""

        with open(webpage) as html_file:
            try:
                soup = bs(html_file, "html.parser")
            except Exception:
                return []
        links = soup.find_all("a")
        all_links = []
        for link in links:
            if link is None:
                continue
            href = link.get("href")
            href_text = link.text.strip() if link.text.strip() else ""
            if not href:
                continue
            to_append = {href_text: href}
            if to_append not in all_links:
                all_links.append(to_append)
        return all_links


def get_hashcode(input_string):
    if input_string is None:
        return
    return hashlib.sha256(input_string.encode("utf-8")).hexdigest()


class CandidateUtils:
    @staticmethod
    def load_candidates():
        """Load the candidates and their metadata from the database"""
        with open(config.CANDIDATE_OFFICE_WEBSITE) as f:
            reader = csv.DictReader(f, delimiter=",")
            for candidate in reader:
                candidate_name = candidate["name"]
                candidate_office = candidate["office"]
                candidate_website = candidate["website"]

                yield candidate_name, candidate_office, candidate_website

    @staticmethod
    def get_candidate_website_folder(candidate_name, candidate_office):
        """returns the downloaded html folder path for a given candidate"""
        html_folder = config.HTML_FOLDER
        website_path = os.path.join(html_folder, candidate_office, candidate_name)
        return website_path

    @staticmethod
    def get_webpages(candidate_name, candidate_office):
        """returns a generator that generates the downloaded webpages of a given candidate's name"""

        website_path = CandidateUtils.get_candidate_website_folder(candidate_name, candidate_office)
        if not os.path.isdir(website_path):
            return
        for webpage in os.listdir(website_path):
            yield os.path.join(website_path, webpage)

    @staticmethod
    def get_form_fields(candidate_name, candidate_office):
        input_fields = set()
        for html_file in CandidateUtils.get_webpages(candidate_name, candidate_office):
            with open(html_file) as hfile:
                try:
                    soup = bs(hfile, "html.parser")
                except Exception:
                    continue
                forms = soup.find_all("form")
                if not forms:
                    return []
                for form in forms:
                    if form.find_all("input"):
                        labels = form.find_all("label")
                        for label in labels:
                            input_fields.add(label.text)
        return list(input_fields)
