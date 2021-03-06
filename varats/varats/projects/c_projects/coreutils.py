"""Project file for the GNU coreutils."""
import typing as tp
from pathlib import Path

import benchbuild as bb
from benchbuild.utils.cmd import git, make
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


class Coreutils(bb.Project, CVEProviderHook):  # type: ignore
    """GNU coretuils / UNIX command-line tools (fetched by Git)"""

    NAME = 'coreutils'
    GROUP = 'c_projects'
    DOMAIN = 'utils'

    SOURCE = [
        bb.source.Git(
            remote="https://github.com/coreutils/coreutils.git",
            local="coreutils",
            refspec="HEAD",
            limit=None,
            shallow=False,
            version_filter=project_filter_generator("coreutils")
        )
    ]

    @property
    def binaries(self) -> tp.List[ProjectBinaryWrapper]:
        """Return a list of binaries generated by the project."""
        return wrap_paths_to_binaries([
            # figure out how to handle this file correctly in filenames
            # 'src/[',
            ('src/uniq', BinaryType.executable),
            ('src/dircolors', BinaryType.executable),
            ('src/numfmt', BinaryType.executable),
            ('src/b2sum', BinaryType.executable),
            ('src/mv', BinaryType.executable),
            ('src/fold', BinaryType.executable),
            ('src/dir', BinaryType.executable),
            ('src/mkfifo', BinaryType.executable),
            ('src/vdir', BinaryType.executable),
            ('src/sha512sum', BinaryType.executable),
            ('src/unexpand', BinaryType.executable),
            ('src/join', BinaryType.executable),
            ('src/nproc', BinaryType.executable),
            ('src/ptx', BinaryType.executable),
            ('src/printf', BinaryType.executable),
            ('src/ginstall', BinaryType.executable),
            ('src/du', BinaryType.executable),
            ('src/printenv', BinaryType.executable),
            # 'dcgen', was not found in version #961d668
            ('src/groups', BinaryType.executable),
            ('src/sync', BinaryType.executable),
            ('src/ln', BinaryType.executable),
            ('src/shuf', BinaryType.executable),
            ('src/false', BinaryType.executable),
            ('src/mkdir', BinaryType.executable),
            ('src/chmod', BinaryType.executable),
            ('src/link', BinaryType.executable),
            ('src/cat', BinaryType.executable),
            ('src/pwd', BinaryType.executable),
            ('src/chown', BinaryType.executable),
            ('src/head', BinaryType.executable),
            ('src/sleep', BinaryType.executable),
            ('src/fmt', BinaryType.executable),
            ('src/getlimits', BinaryType.executable),
            ('src/test', BinaryType.executable),
            ('src/paste', BinaryType.executable),
            ('src/comm', BinaryType.executable),
            ('src/mknod', BinaryType.executable),
            ('src/kill', BinaryType.executable),
            ('src/sha384sum', BinaryType.executable),
            ('src/sort', BinaryType.executable),
            ('src/sum', BinaryType.executable),
            ('src/sha224sum', BinaryType.executable),
            ('src/expand', BinaryType.executable),
            ('src/basenc', BinaryType.executable),
            ('src/truncate', BinaryType.executable),
            ('src/dd', BinaryType.executable),
            ('src/tail', BinaryType.executable),
            ('src/df', BinaryType.executable),
            ('src/tee', BinaryType.executable),
            ('src/tsort', BinaryType.executable),
            ('src/yes', BinaryType.executable),
            ('src/sha1sum', BinaryType.executable),
            ('src/rm', BinaryType.executable),
            ('src/make-prime-list', BinaryType.executable),
            ('src/logname', BinaryType.executable),
            ('src/pathchk', BinaryType.executable),
            ('src/whoami', BinaryType.executable),
            ('src/wc', BinaryType.executable),
            ('src/basename', BinaryType.executable),
            ('src/nohup', BinaryType.executable),
            # 'libstdbuf.so', could not find in version #961d668
            ('src/chroot', BinaryType.executable),
            ('src/users', BinaryType.executable),
            ('src/csplit', BinaryType.executable),
            # 'stdbuf',  is no tool
            ('src/hostid', BinaryType.executable),
            ('src/readlink', BinaryType.executable),
            ('src/timeout', BinaryType.executable),
            ('src/base64', BinaryType.executable),
            ('src/id', BinaryType.executable),
            ('src/nl', BinaryType.executable),
            ('src/stat', BinaryType.executable),
            ('src/cp', BinaryType.executable),
            ('src/shred', BinaryType.executable),
            ('src/who', BinaryType.executable),
            ('src/tr', BinaryType.executable),
            ('src/echo', BinaryType.executable),
            ('src/date', BinaryType.executable),
            ('src/split', BinaryType.executable),
            ('src/seq', BinaryType.executable),
            ('src/md5sum', BinaryType.executable),
            ('src/env', BinaryType.executable),
            ('src/expr', BinaryType.executable),
            ('src/true', BinaryType.executable),
            ('src/chcon', BinaryType.executable),
            ('src/chgrp', BinaryType.executable),
            ('src/mktemp', BinaryType.executable),
            ('src/unlink', BinaryType.executable),
            ('src/uname', BinaryType.executable),
            ('src/pinky', BinaryType.executable),
            ('src/stty', BinaryType.executable),
            ('src/rmdir', BinaryType.executable),
            ('src/ls', BinaryType.executable),
            ('src/runcon', BinaryType.executable),
            ('src/nice', BinaryType.executable),
            # 'blake2', is a folder
            ('src/tty', BinaryType.executable),
            ('src/factor', BinaryType.executable),
            ('src/tac', BinaryType.executable),
            ('src/realpath', BinaryType.executable),
            ('src/pr', BinaryType.executable),
            ('src/sha256sum', BinaryType.executable),
            # 'du-tests', removed due to bash script
            ('src/cksum', BinaryType.executable),
            ('src/touch', BinaryType.executable),
            ('src/cut', BinaryType.executable),
            ('src/od', BinaryType.executable),
            ('src/base32', BinaryType.executable),
            ('src/uptime', BinaryType.executable),
            ('src/dirname', BinaryType.executable),
        ])

    def run_tests(self) -> None:
        coreutils_source = local.path(self.source_of_primary)
        with local.cwd(coreutils_source):
            bb.watch(make)("-j", get_number_of_jobs(bb_cfg()), "check")

    def compile(self) -> None:
        coreutils_source = local.path(self.source_of_primary)
        compiler = bb.compiler.cc(self)
        with local.cwd(coreutils_source):
            git("submodule", "init")
            git("submodule", "update")
            with local.env(CC=str(compiler)):
                bb.watch(local["./bootstrap"])()
                bb.watch(local["./configure"])("--disable-gcc-warnings")

            bb.watch(make)("-j", get_number_of_jobs(bb_cfg()))
            for binary in self.binaries:
                if not Path("{binary}".format(binary=binary)).exists():
                    print("Could not find {binary}")

    @classmethod
    def get_cve_product_info(cls) -> tp.List[tp.Tuple[str, str]]:
        return [("gnu", "coreutils")]
