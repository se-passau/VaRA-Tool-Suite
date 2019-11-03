"""
Small module that executes all experiments needed for the comparison of Phasar
and VaRA's taint propagation.
"""

import typing as tp

from benchbuild.extensions import compiler, run, time
from benchbuild.project import Project
from benchbuild.experiment import Experiment
import benchbuild.utils.actions as actions
from varats.data.reports.taint_report import TaintPropagationReport as TPR
from varats.experiments.wllvm import RunWLLVM
from varats.experiments.vara_fc_taint_analysis \
    import VaRAFileCheckTaintPropagation as VaRA
from varats.experiments.phasar_env_trace_propagation \
    import PhasarEnvTracePropagation as Phasar


class CompareTaintPropagation(Experiment):  # type: ignore
    """
    First executes VaRA's experiments regarding taint propagation and then the
    experiments of Phasar regarding environment variable tracing.
    """

    NAME = "CompareTaintPropagation"
    REPORT_TYPE = TPR

    def actions_for_project(self, project: Project) -> tp.List[actions.Step]:
        """
        Returns the specified steps to run the project(s) specified in
        the call in a fixed order.
        """

        # Add the required runtime extensions to the project(s)
        project.runtime_extension = run.RuntimeExtension(project, self) \
            << time.RunWithTime()

        # Add the required compiler extensions to the project(s)
        project.compiler_extension = compiler.RunCompiler(project, self) \
            << RunWLLVM() \
            << run.WithTimeout()

        # call VaRA's action steps as a VaRAFileCheckTaintPropagation
        analysis_actions = VaRA.actions_for_project(VaRA(), project)
        # remove the clean step from the other experiment
        del analysis_actions[-1]

        # extend the action steps as a PhasarEnvTracePropagation
        analysis_actions.extend(Phasar.actions_for_project(Phasar(), project))

        return analysis_actions
