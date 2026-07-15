"""Tests for GraphcalProject discovery and module resolution."""
import tempfile
import unittest
from pathlib import Path

from graphcal import GraphcalError, GraphcalProject


class DiscoverTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def _write_manifest(self, text):
        (self.root / "graphcal.toml").write_text(text, encoding="utf-8")

    def test_discover_reads_package_name_and_source_dir(self):
        self._write_manifest('[package]\nname = "mission"\nsource_dir = "lib"\n')

        project = GraphcalProject.discover(start=self.root)

        self.assertEqual(project.root, self.root.resolve())
        self.assertEqual(project.package_name, "mission")
        self.assertEqual(project.source_dir, Path("lib"))

    def test_discover_walks_up_from_nested_file(self):
        self._write_manifest('[package]\nname = "mission"\n')
        nested = self.root / "src" / "mission" / "transfer"
        nested.mkdir(parents=True)
        start = nested / "orbital_insertion.gcl"
        start.write_text("", encoding="utf-8")

        project = GraphcalProject.discover(start=start)

        self.assertEqual(project.root, self.root.resolve())
        self.assertEqual(project.source_dir, Path("src"))

    def test_discover_uses_root_level_source_dir_fallback(self):
        self._write_manifest('source_dir = "lib"\n[package]\nname = "mission"\n')

        project = GraphcalProject.discover(start=self.root)

        self.assertEqual(project.source_dir, Path("lib"))

    def test_discover_without_manifest_raises(self):
        with self.assertRaises(GraphcalError):
            GraphcalProject.discover(start=self.root)


class FileResolutionTest(unittest.TestCase):
    def setUp(self):
        self.project = GraphcalProject(
            root=Path("/repo/mission"),
            package_name="mission",
            source_dir=Path("src"),
        )

    def test_dotted_module_resolves_under_source_dir(self):
        path = self.project.file("mission.transfer.orbital_insertion")

        self.assertEqual(
            path, Path("/repo/mission/src/mission/transfer/orbital_insertion.gcl")
        )

    def test_dotted_module_without_package_prefix_resolves_the_same(self):
        path = self.project.file("transfer.orbital_insertion")

        self.assertEqual(
            path, Path("/repo/mission/src/mission/transfer/orbital_insertion.gcl")
        )

    def test_relative_gcl_path_resolves_from_project_root(self):
        path = self.project.file("scene/corridor_area.gcl")

        self.assertEqual(path, Path("/repo/mission/scene/corridor_area.gcl"))

    def test_absolute_path_is_kept(self):
        path = self.project.file("/elsewhere/model.gcl")

        self.assertEqual(path, Path("/elsewhere/model.gcl"))


if __name__ == "__main__":
    unittest.main()
