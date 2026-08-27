import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from pipeline import robust_pipeline as rp


class RobustPipelineTests(unittest.TestCase):
    def test_atomic_json_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            rp.atomic_json(path, {"answer": 42})
            self.assertEqual(json.loads(path.read_text())["answer"], 42)
            self.assertFalse(list(Path(directory).glob(".*.tmp")))

    def test_state_machine_rejects_publish_before_verify(self):
        ledger = {"episodes": {"009": {"status": "rendered", "transitions": []}}}
        with self.assertRaises(ValueError):
            rp.transition(ledger, "009", "published")
        rp.transition(ledger, "009", "verified")
        rp.transition(ledger, "009", "published")
        self.assertEqual(ledger["episodes"]["009"]["status"], "published")

    def test_lock_reports_active_and_releases(self):
        with tempfile.TemporaryDirectory() as directory:
            lock_path = Path(directory) / "pipeline.lock"
            with rp.PipelineLock(lock_path):
                self.assertTrue(rp.lock_status(lock_path)["active"])
                # A second owner cannot acquire the same lock immediately.
                with self.assertRaises(RuntimeError):
                    with rp.PipelineLock(lock_path):
                        pass
            with rp.PipelineLock(lock_path):
                pass
            self.assertFalse(rp.lock_status(lock_path)["active"])

    def test_review_gate_requires_three_passes(self):
        good = """# Review\n## Reviewer 1 — One\nInitial verdict: revise, then pass.\nRequired revisions: none after revision.\n## Reviewer 2 — Two\nInitial verdict: revise, then pass.\nRequired revisions: none after revision.\n## Reviewer 3 — Three\nInitial verdict: revise, then pass.\nRequired revisions: none after revision.\n## Revision record\nAll revisions completed.\n"""
        with tempfile.TemporaryDirectory() as directory:
            panel = Path(directory) / "review.md"
            panel.write_text(good)
            result = rp.review_gate("009", panel)
            self.assertTrue(result["ok"], result)
            panel.write_text(good.replace("Reviewer 3", "Reviewer 2"))
            self.assertFalse(rp.review_gate("009", panel)["ok"])

    def test_preflight_is_deterministic_and_checks_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            episode = root / "episodes" / "009"
            episode.mkdir(parents=True)
            (root / "pipeline").mkdir()
            (root / "pipeline" / "manifest.json").write_text(json.dumps({"episodes": {"009": {"sources": ["ABCDEFGH"]}}}))
            (episode / "script.md").write_text("""# Episode\n\n**Host:** Welcome.\n**Rowan:** I am a fictional composite correspondent. This is an AI-generated summary.\n**Rowan:** The complete citations are in the show notes, with links to the Zotero files when you have been granted access.\n""")
            (episode / "episode-notes.md").write_text("""# Notes\n\n1. Author Name. “A Complete Source Title.” Journal of Testing, 2024. [Zotero](https://www.zotero.org/djgagnon/items/ABCDEFGH)\n\nThe complete citations are in the show notes, with links to the Zotero files when you have been granted access.\n""")
            with mock.patch.object(rp, "ROOT", root), mock.patch.object(rp, "MANIFEST_PATH", root / "pipeline" / "manifest.json"):
                result = rp.preflight("009", enforce_review=False)
            self.assertTrue(result["ok"], result)

    def test_verify_feed_checks_local_enclosure_length(self):
        with tempfile.TemporaryDirectory() as directory:
            site = Path(directory)
            audio = site / "episode.mp3"
            audio.write_bytes(b"not really mp3, but a non-empty fixture")
            feed = site / "feed.xml"
            feed.write_text("""<?xml version='1.0'?><rss><channel><item><guid>x</guid><enclosure url='https://example.invalid/episode.mp3' length='39' type='audio/mpeg'/></item></channel></rss>""")
            result = rp.verify_feed(feed)
            self.assertTrue(result["ok"], result)


if __name__ == "__main__":
    unittest.main()
