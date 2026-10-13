import re
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOMEPAGE = ROOT / "index.html"


def normalize(parts):
    return re.sub(r"\s+", " ", "".join(parts)).strip()


class HomepageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.publications = []
        self.news_items = []
        self.section_heading = ""
        self._heading_parts = None
        self._news_parts = None
        self._publication = None
        self._title_parts = None
        self._link = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        classes = set(attributes.get("class", "").split())

        if tag == "h2":
            self._heading_parts = []
        elif tag == "li" and self.section_heading == "News":
            self._news_parts = []

        if tag == "article" and "paper" in classes:
            self._publication = {"text_parts": [], "links": []}
        elif self._publication is not None:
            if tag == "h3":
                self._title_parts = []
            elif tag == "a":
                self._link = {"href": attributes.get("href"), "text_parts": []}

    def handle_data(self, data):
        if self._heading_parts is not None:
            self._heading_parts.append(data)
        if self._news_parts is not None:
            self._news_parts.append(data)
        if self._publication is not None:
            self._publication["text_parts"].append(data)
        if self._title_parts is not None:
            self._title_parts.append(data)
        if self._link is not None:
            self._link["text_parts"].append(data)

    def handle_endtag(self, tag):
        if tag == "h2" and self._heading_parts is not None:
            self.section_heading = normalize(self._heading_parts)
            self._heading_parts = None
        elif tag == "li" and self._news_parts is not None:
            self.news_items.append(normalize(self._news_parts))
            self._news_parts = None

        if self._publication is None:
            return

        if tag == "a" and self._link is not None:
            self._publication["links"].append(
                (normalize(self._link["text_parts"]), self._link["href"])
            )
            self._link = None
        elif tag == "h3" and self._title_parts is not None:
            self._publication["title"] = normalize(self._title_parts)
            self._title_parts = None
        elif tag == "article":
            self._publication["text"] = normalize(self._publication.pop("text_parts"))
            self.publications.append(self._publication)
            self._publication = None


class HomepageContentTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parser = HomepageParser()
        cls.parser.feed(HOMEPAGE.read_text(encoding="utf-8"))

    def publication(self, title):
        return next(
            publication
            for publication in self.parser.publications
            if publication.get("title") == title
        )

    def test_corl_2026_papers_lead_publications_in_requested_order(self):
        expected_titles = [
            "TeleDexter: Towards Human-level Dexterous Teleoperation",
            "ArtManip: Category-Level Articulated In-Hand Manipulation",
            "OpenDexGrasp: Open-vocabulary Task-Oriented Dexterous Grasping",
        ]
        actual_titles = [
            publication.get("title") for publication in self.parser.publications[:3]
        ]
        self.assertEqual(actual_titles, expected_titles)

    def test_each_leading_paper_shows_corl_2026_venue(self):
        for title in (
            "TeleDexter: Towards Human-level Dexterous Teleoperation",
            "ArtManip: Category-Level Articulated In-Hand Manipulation",
            "OpenDexGrasp: Open-vocabulary Task-Oriented Dexterous Grasping",
        ):
            with self.subTest(title=title):
                publication = self.publication(title)
                self.assertIn(
                    "[CoRL 2026] Conference on Robot Learning 2026",
                    publication["text"],
                )

    def test_news_leads_with_three_corl_2026_acceptances(self):
        self.assertEqual(
            self.parser.news_items[0],
            "[2026/09] 🎉 Three papers were accepted to CoRL 2026, with OpenDexGrasp selected for an Oral presentation (one of 21 oral presentations among 687 accepted papers, selected from 2,094 submissions).",
        )

    def test_yingying_wu_has_profile_link_in_each_authored_paper(self):
        expected_url = "https://win-yingying.github.io/"
        for title in (
            "TeleDexter: Towards Human-level Dexterous Teleoperation",
            "ArtManip: Category-Level Articulated In-Hand Manipulation",
        ):
            with self.subTest(title=title):
                links = {
                    text.rstrip("*"): href
                    for text, href in self.publication(title)["links"]
                }
                self.assertEqual(links.get("Yingying Wu"), expected_url)


if __name__ == "__main__":
    unittest.main()
