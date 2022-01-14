import website_downloader, privacy_policy_analyzer, link_extractor, form_extractor
from config import DOWNLOAD_SITES, PRIVACY_POLICY_ANALYSIS, LINK_EXTRACTOR_ANALYSIS, FORM_EXTRACTOR_ANALYSIS


def main():
    """Start the download and analysis"""

    if DOWNLOAD_SITES:
        website_downloader.start()
    if PRIVACY_POLICY_ANALYSIS:
        privacy_policy_analyzer.start()
    if LINK_EXTRACTOR_ANALYSIS:
        link_extractor.start()
    if FORM_EXTRACTOR_ANALYSIS:
        form_extractor.start()


if __name__ == "__main__":
    main()
