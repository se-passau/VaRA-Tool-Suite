"""Project file for openssl."""
import typing as tp

import benchbuild as bb
from benchbuild.utils.cmd import make
from benchbuild.utils.settings import get_number_of_jobs
from plumbum import local

from varats.paper_mgmt.paper_config import project_filter_generator
from varats.project.project_util import (
    wrap_paths_to_binaries,
    ProjectBinaryWrapper,
    BinaryType,
)
from varats.provider.cve.cve_provider import CVEProviderHook
from varats.utils.settings import bb_cfg


class OpenSSL(bb.Project, CVEProviderHook):  # type: ignore
    """TLS-framework OpenSSL (fetched by Git)"""

    NAME = 'openssl'
    GROUP = 'c_projects'
    DOMAIN = 'security'

    SOURCE = [
        bb.source.Git(
            remote="https://github.com/openssl/openssl.git",
            local="openssl",
            refspec="HEAD",
            limit=None,
            shallow=False,
            version_filter=project_filter_generator("openssl")
        )
    ]

    @property
    def binaries(self) -> tp.List[ProjectBinaryWrapper]:
        """Return a list of binaries generated by the project."""
        return wrap_paths_to_binaries([("libssl.so", BinaryType.shared_library)]
                                     )

    def run_tests(self) -> None:
        pass

    def compile(self) -> None:
        """Compile the project."""
        openssl_source = local.path(self.source_of_primary)

        compiler = bb.compiler.cc(self)
        with local.cwd(openssl_source):
            with local.env(CC=str(compiler)):
                bb.watch(local['./config'])()
            bb.watch(make)("-j", get_number_of_jobs(bb_cfg()))

    @classmethod
    def get_cve_product_info(cls) -> tp.List[tp.Tuple[str, str]]:
        return [("openssl_project", "openssl"), ("openssl", "openssl")]
