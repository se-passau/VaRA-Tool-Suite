"""Scenario CentralCode."""
import typing as tp

import benchbuild as bb
from plumbum import local

from varats.paper_mgmt.paper_config import project_filter_generator
from varats.project.project_util import (
    ProjectBinaryWrapper,
    wrap_paths_to_binaries,
    BinaryType,
    VaraTestRepoSource,
)


class SZZBase(bb.Project):  # type: ignore
    """
    Scenario SZZ base.

    A scenario with a bug that SZZ should be able to identify. Scenario adapted
    from Kim et. al. 2006 "Automatic Identification of Bug-Introducing Changes"
    """

    NAME = 'szz_base'
    DOMAIN = 'testing'
    GROUP = 'test_projects'

    SOURCE = [
        VaraTestRepoSource(
            remote="BlameAnalysisRepos/Scenarios/SZZBase",
            local="CentralCode",
            refspec="HEAD",
            limit=None,
            version_filter=project_filter_generator(NAME)
        )
    ]

    @property
    def binaries(self) -> tp.List[ProjectBinaryWrapper]:
        return wrap_paths_to_binaries([("main", BinaryType.executable)])

    def run_tests(self) -> None:
        pass

    def compile(self) -> None:
        """Compile the project."""
        source = local.path(self.source_of_primary)

        clang = bb.compiler.cc(self)  # type: ignore
        with local.cwd(source):
            bb.watch(clang)("main.c", "-o", "main")  # type: ignore
