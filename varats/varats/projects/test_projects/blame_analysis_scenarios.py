"""Example project demonstrating how to use a repo from the vara-test-repos."""
import typing as tp

import benchbuild as bb
from benchbuild.utils.cmd import cmake, make
from benchbuild.utils.settings import get_number_of_jobs
from plumbum import local

from varats.paper_mgmt.paper_config import project_filter_generator
from varats.project.project_util import (
    ProjectBinaryWrapper,
    wrap_paths_to_binaries,
    BinaryType,
    LocalGit,
)
from varats.utils.settings import bb_cfg


class BlameAnalysisScenarios(bb.Project):  # type: ignore
    """Example project demonstrating how to use a repo from the vara-test-
    repos."""

    NAME = 'ba_scenarios'
    DOMAIN = 'testing'
    GROUP = 'test_projects'

    SOURCE = [
        LocalGit(
            remote="/dev/null",
            local="BlameAnalysisScenarios",
            refspec="HEAD",
            limit=None,
            version_filter=project_filter_generator(NAME)
        )
    ]

    @property
    def binaries(self) -> tp.List[ProjectBinaryWrapper]:
        return wrap_paths_to_binaries([("calculator", BinaryType.executable)])

    def run_tests(self) -> None:
        pass

    def compile(self) -> None:
        """Compile the example project."""
        source = local.path(self.source_of_primary)

        clang = bb.compiler.cxx(self)  # type: ignore
        with local.cwd(source):
            with local.env(CXX=str(clang)):
                bb.watch(cmake)("-G", "Unix Makefiles", ".")  # type: ignore
            bb.watch(make)("-j", get_number_of_jobs(bb_cfg()))  # type: ignore
