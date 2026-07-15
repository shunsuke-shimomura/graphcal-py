"""Tests for GraphcalProject discovery and module resolution."""
from pathlib import Path

import pytest

from graphcal import GraphcalError, GraphcalProject


def _write_manifest(root: Path, text: str) -> None:
    (root / "graphcal.toml").write_text(text, encoding="utf-8")


class TestDiscover:
    def test_discover_reads_package_name_and_source_dir(self, tmp_path):
        _write_manifest(tmp_path, '[package]\nname = "mission"\nsource_dir = "lib"\n')

        project = GraphcalProject.discover(start=tmp_path)

        assert project.root == tmp_path.resolve()
        assert project.package_name == "mission"
        assert project.source_dir == Path("lib")

    def test_discover_walks_up_from_nested_file(self, tmp_path):
        _write_manifest(tmp_path, '[package]\nname = "mission"\n')
        nested = tmp_path / "src" / "mission" / "transfer"
        nested.mkdir(parents=True)
        start = nested / "orbital_insertion.gcl"
        start.write_text("", encoding="utf-8")

        project = GraphcalProject.discover(start=start)

        assert project.root == tmp_path.resolve()
        assert project.source_dir == Path("src")

    def test_discover_uses_root_level_source_dir_fallback(self, tmp_path):
        _write_manifest(tmp_path, 'source_dir = "lib"\n[package]\nname = "mission"\n')

        project = GraphcalProject.discover(start=tmp_path)

        assert project.source_dir == Path("lib")

    def test_discover_without_manifest_raises(self, tmp_path):
        with pytest.raises(GraphcalError):
            GraphcalProject.discover(start=tmp_path)


class TestFileResolution:
    @pytest.fixture
    def project(self):
        return GraphcalProject(
            root=Path("/repo/mission"),
            package_name="mission",
            source_dir=Path("src"),
        )

    def test_dotted_module_resolves_under_source_dir(self, project):
        path = project.file("mission.transfer.orbital_insertion")

        assert path == Path("/repo/mission/src/mission/transfer/orbital_insertion.gcl")

    def test_dotted_module_without_package_prefix_resolves_the_same(self, project):
        path = project.file("transfer.orbital_insertion")

        assert path == Path("/repo/mission/src/mission/transfer/orbital_insertion.gcl")

    def test_relative_gcl_path_resolves_from_project_root(self, project):
        path = project.file("scene/corridor_area.gcl")

        assert path == Path("/repo/mission/scene/corridor_area.gcl")

    def test_absolute_path_is_kept(self, project):
        path = project.file("/elsewhere/model.gcl")

        assert path == Path("/elsewhere/model.gcl")
