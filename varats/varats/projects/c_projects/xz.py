"""Project file for xz."""
import typing as tp

import benchbuild as bb
from benchbuild.utils.cmd import autoreconf, make
from benchbuild.utils.revision_ranges import (
    block_revisions,
    GoodBadSubgraph,
    RevisionRange,
)
from benchbuild.utils.settings import get_number_of_jobs
from plumbum import local

from varats.data.provider.cve.cve_provider import CVEProviderHook
from varats.paper.paper_config import project_filter_generator
from varats.utils.project_util import (
    ProjectBinaryWrapper,
    get_all_revisions_between,
    wrap_paths_to_binaries,
    get_local_project_git_path,
)
from varats.utils.settings import bb_cfg


class Xz(bb.Project, CVEProviderHook):  # type: ignore
    """Compression and decompression tool xz (fetched by Git)"""

    NAME = 'xz'
    GROUP = 'c_projects'
    DOMAIN = 'compression'

    SOURCE = [
        block_revisions([
            GoodBadSubgraph(["cf49f42a6bd40143f54a6b10d6e605599e958c0b"],
                            ["4c7ad179c78f97f68ad548cb40a9dfa6871655ae"],
                            "missing file api/lzma/easy.h"),
            GoodBadSubgraph(["335fe260a81f61ec99ff5940df733b4c50aedb7c"],
                            ["24e0406c0fb7494d2037dec033686faf1bf67068"],
                            "use of undeclared LZMA_THREADS_MAX"),
            RevisionRange(
                "5d018dc03549c1ee4958364712fb0c94e1bf2741",
                "c324325f9f13cdeb92153c5d00962341ba070ca2",
                "Initial git import without xz"
            )
        ])(
            bb.source.Git(
                remote="https://github.com/xz-mirror/xz.git",
                local="xz",
                refspec="HEAD",
                limit=None,
                shallow=False,
                version_filter=project_filter_generator("xz")
            )
        )
    ]

    @property
    def binaries(self) -> tp.List[ProjectBinaryWrapper]:
        """Return a list of binaries generated by the project."""
        xz_git_path = get_local_project_git_path(self.NAME)
        xz_version = self.version_of_primary
        with local.cwd(xz_git_path):
            old_xz_location = get_all_revisions_between(
                "5cda29b5665004fc0f21d0c41d78022a6a559ab2",
                "b2172cf823d3be34cb0246cb4cb32d105e2a34c9",
                short=True
            )
            if xz_version in old_xz_location:
                return wrap_paths_to_binaries(['src/xz/xz'])

            return wrap_paths_to_binaries(['src/xz/.libs/xz'])

    def run_tests(self) -> None:
        pass

    def compile(self) -> None:
        """Compile the project."""
        xz_git_path = get_local_project_git_path(self.NAME)
        xz_version_source = local.path(self.source_of_primary)
        xz_version = self.version_of_primary

        # dynamic linking is off by default until
        # commit f9907503f882a745dce9d84c2968f6c175ba966a
        # (fda4724 is its parent)
        with local.cwd(xz_git_path):
            revisions_wo_dynamic_linking = get_all_revisions_between(
                "5d018dc03549c1ee4958364712fb0c94e1bf2741",
                "fda4724d8114fccfa31c1839c15479f350c2fb4c",
                short=True
            )

        self.cflags += ["-fPIC"]

        clang = bb.compiler.cc(self)
        with local.cwd(xz_version_source):
            with local.env(CC=str(clang)):
                bb.watch(autoreconf)("--install")
                configure = bb.watch(local["./configure"])

                if xz_version in revisions_wo_dynamic_linking:
                    configure("--enable-dynamic=yes")
                else:
                    configure()

            bb.watch(make)("-j", get_number_of_jobs(bb_cfg()))

    @classmethod
    def get_cve_product_info(cls) -> tp.List[tp.Tuple[str, str]]:
        return [("tukaani", "xz")]