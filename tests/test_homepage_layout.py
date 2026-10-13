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

    def assert_one_column(self, layout):
        cards = layout["cards"]
        for index, card in enumerate(cards):
            with self.subTest(card=index + 1):
                self.assertAlmostEqual(card["card"]["left"], cards[0]["card"]["left"], delta=2)
                self.assertLessEqual(card["card"]["right"], layout["viewportWidth"])

        for index in range(1, len(cards)):
            with self.subTest(card=index + 1):
                self.assertGreaterEqual(
                    cards[index]["card"]["top"],
                    cards[index - 1]["card"]["bottom"],
                )

    def test_all_publications_stack_on_desktop(self):
        self.assert_one_column(self.layout["desktop"])

    def test_all_publications_stack_on_mobile(self):
        self.assert_one_column(self.layout["mobile"])

    def test_mobile_layout_has_no_horizontal_overflow(self):
        mobile = self.layout["mobile"]
        self.assertEqual(mobile["scrollWidth"], mobile["viewportWidth"])

    def test_publication_oral_labels_render_red(self):
        for viewport in ("desktop", "mobile"):
            colors = self.layout[viewport]["oralColors"]
            self.assertEqual(len(colors), 2)
            self.assertTrue(all(color == "rgb(249, 3, 3)" for color in colors), colors)

    def test_desktop_places_media_left_of_details(self):
        for viewport in ("desktop", "aboveBreakpoint"):
            for card in self.layout[viewport]["cards"]:
                self.assertLessEqual(card["media"]["right"], card["details"]["left"])

    def test_mobile_places_media_above_details(self):
        for viewport in ("mobile", "atBreakpoint"):
            self.assert_one_column(self.layout[viewport])
            for card in self.layout[viewport]["cards"]:
                self.assertLessEqual(card["media"]["bottom"], card["details"]["top"])


if __name__ == "__main__":
    unittest.main()
