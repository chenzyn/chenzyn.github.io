import html
import json
import os
import re
import shutil
import subprocess
import unittest
from pathlib import Path


PROBE = Path(__file__).with_name("layout_probe.html")
DEFAULT_CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")


def find_chrome():
    configured = os.environ.get("CHROME_BIN")
    if configured:
        candidate = Path(configured)
        return candidate if candidate.is_file() else None

    candidates = [
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
        DEFAULT_CHROME,
    ]
    return next(
        (Path(candidate) for candidate in candidates if candidate and Path(candidate).is_file()),
        None,
    )


class HomepageLayoutTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        chrome = find_chrome()
        if chrome is None:
            raise unittest.SkipTest(
                "Chrome/Chromium is required for rendered layout checks; "
                "set CHROME_BIN to its executable"
            )

        try:
            result = subprocess.run(
                [
                    str(chrome),
                    "--headless=new",
                    "--disable-background-networking",
                    "--disable-component-update",
                    "--disable-extensions",
                    "--disable-gpu",
                    "--incognito",
                    "--no-default-browser-check",
                    "--no-first-run",
                    "--allow-file-access-from-files",
                    "--virtual-time-budget=3000",
                    "--dump-dom",
                    PROBE.as_uri(),
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )
        except subprocess.TimeoutExpired as error:
            raise AssertionError("Chrome layout probe timed out after 30 seconds") from error

        chrome_output = result.stdout
        chrome_errors = result.stderr

        if result.returncode < 0:
            raise unittest.SkipTest(
                "Chrome could not start in this environment "
                f"(signal {-result.returncode}); run with browser permission"
            )
        if result.returncode:
            raise AssertionError(
                f"Chrome exited with status {result.returncode}:\n{chrome_errors[-2000:]}"
            )

        match = re.search(r'<pre id="result">([^<]+)</pre>', chrome_output)
        if not match:
            raise AssertionError(
                "Layout probe did not return browser measurements. "
                f"Chrome stderr:\n{chrome_errors[-2000:]}"
            )
        cls.layout = json.loads(html.unescape(match.group(1)))
        if "error" in cls.layout:
            raise AssertionError(f"Layout probe failed: {cls.layout['error']}")

    def assert_two_columns(self, layout):
        cards = layout["cards"]
        for index in range(0, len(cards) - 1, 2):
            with self.subTest(row=index // 2 + 1):
                left = cards[index]["card"]
                right = cards[index + 1]["card"]
                self.assertAlmostEqual(left["top"], right["top"], delta=2)
                self.assertGreater(right["left"], left["right"])

        for index in range(2, len(cards), 2):
            with self.subTest(row=index // 2 + 1):
                self.assertGreaterEqual(
                    cards[index]["card"]["top"],
                    cards[index - 2]["card"]["bottom"],
                )

    def assert_one_column(self, layout):
        cards = layout["cards"]
        for index, card in enumerate(cards):
            with self.subTest(card=index + 1):
                self.assertAlmostEqual(card["card"]["left"], 0, delta=2)
                self.assertLessEqual(card["card"]["right"], layout["viewportWidth"])

        for index in range(1, len(cards)):
            with self.subTest(card=index + 1):
                self.assertGreaterEqual(
                    cards[index]["card"]["top"],
                    cards[index - 1]["card"]["bottom"],
                )

    def test_all_publications_fill_two_column_rows_on_desktop(self):
        self.assert_two_columns(self.layout["desktop"])

    def test_all_publications_stack_on_mobile(self):
        self.assert_one_column(self.layout["mobile"])

    def test_mobile_layout_has_no_horizontal_overflow(self):
        mobile = self.layout["mobile"]
        self.assertEqual(mobile["scrollWidth"], mobile["viewportWidth"])

    def test_every_card_places_media_above_details(self):
        for viewport in ("desktop", "mobile"):
            for index, card in enumerate(self.layout[viewport]["cards"]):
                with self.subTest(viewport=viewport, card=index + 1):
                    self.assertLessEqual(card["media"]["bottom"], card["details"]["top"])

    def test_layout_switches_to_one_column_at_760_pixels(self):
        self.assert_two_columns(self.layout["aboveBreakpoint"])
        self.assert_one_column(self.layout["atBreakpoint"])


if __name__ == "__main__":
    unittest.main()
