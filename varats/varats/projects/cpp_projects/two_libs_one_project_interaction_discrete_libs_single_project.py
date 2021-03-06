"""Project implementation for the
TwoLibsOneProjectInteractionDiscreteLibsSingleProject library analysis
repository."""
import typing as tp

import benchbuild as bb
from benchbuild.utils.cmd import cmake, make, mkdir
from benchbuild.utils.settings import get_number_of_jobs
from plumbum import local

from varats.paper_mgmt.paper_config import project_filter_generator
from varats.project.project_util import (
    VaraTestRepoSource,
    ProjectBinaryWrapper,
    wrap_paths_to_binaries,
    BinaryType,
    VaraTestRepoSubmodule,
)
from varats.utils.settings import bb_cfg


class TwoLibsOneProjectInteractionDiscreteLibsSingleProject(
    bb.Project  # type: ignore
):
    """Class to analyse interactions between two discrete libraries and one
    project."""

    NAME = 'TwoLibsOneProjectInteractionDiscreteLibsSingleProject'
    GROUP = 'cpp_projects'
    DOMAIN = 'library-testproject'

    SOURCE = [
        VaraTestRepoSource(
            remote="LibraryAnalysisRepos"
            "/TwoLibsOneProjectInteractionDiscreteLibsSingleProject"
            "/Elementalist",
            local="TwoLibsOneProjectInteractionDiscreteLibsSingleProject"
            "/Elementalist",
            refspec="HEAD",
            limit=None,
            shallow=False,
            version_filter=project_filter_generator(
                "TwoLibsOneProjectInteractionDiscreteLibsSingleProject"
            )
        ),
        VaraTestRepoSubmodule(
            remote="LibraryAnalysisRepos"
            "/TwoLibsOneProjectInteractionDiscreteLibsSingleProject"
            "/fire_lib",
            local="TwoLibsOneProjectInteractionDiscreteLibsSingleProject"
            "/fire_lib",
            refspec="HEAD",
            limit=None,
            shallow=False,
            version_filter=project_filter_generator(
                "TwoLibsOneProjectInteractionDiscreteLibsSingleProject"
            )
        ),
        VaraTestRepoSubmodule(
            remote="LibraryAnalysisRepos"
            "/TwoLibsOneProjectInteractionDiscreteLibsSingleProject"
            "/water_lib",
            local="TwoLibsOneProjectInteractionDiscreteLibsSingleProject"
            "/water_lib",
            refspec="HEAD",
            limit=None,
            shallow=False,
            version_filter=project_filter_generator(
                "TwoLibsOneProjectInteractionDiscreteLibsSingleProject"
            )
        )
    ]

    @property
    def binaries(self) -> tp.List[ProjectBinaryWrapper]:
        """Return a list of binaries generated by the project."""
        version_source = local.path(self.source_of_primary)

        return wrap_paths_to_binaries([(
            version_source / "build/test_prog/elementalist/elementalist",
            BinaryType.executable
        )])

    def run_tests(self) -> None:
        pass

    def compile(self) -> None:
        """Contains instructions on how to build the project."""

        version_source = local.path(self.source_of_primary)
        c_compiler = bb.compiler.cc(self)
        cxx_compiler = bb.compiler.cxx(self)
        mkdir(version_source / "build")

        with local.cwd(version_source / "build"):
            with local.env(CC=str(c_compiler), CXX=str(cxx_compiler)):
                bb.watch(cmake)("-G", "Unix Makefiles", "..")
            bb.watch(make)("-j", get_number_of_jobs(bb_cfg()))
