"""
Execute showcase cpp examples with Phasar's tracing of environment variables.
We run the analysis on exemplary cpp files. The cpp examples can be
found in the https://github.com/se-passau/vara-perf-tests repository.
The result JSON is then parsed into an LLVM IR file contaning only the
instructions tainted by the environment variable of the cpp file.
"""

import json
import typing as tp

import benchbuild.utils.actions as actions
from benchbuild.settings import CFG
from benchbuild.project import Project
from benchbuild.utils.cmd import rm
from varats.experiments.phasar_env_analysis import PhasarEnvironmentTracing
from varats.data.reports.taint_report import TaintPropagationReport as TPR
from varats.data.reports.env_trace_report import EnvTraceReport as ENVR
from varats.data.report import FileStatusExtension as FSE


class ParseJSONToInstructions(actions.Step):  # type: ignore
    """
    Analyse a project with Phasar's IFDS that traces environment variables
    inside a project.
    """

    NAME = "ParseJSONToInstructions"
    DESCRIPTION = "Parses Phasar's JSON into only the tainted instructions."

    RESULT_FOLDER_TEMPLATE = "{result_dir}/{project_dir}"

    def __init__(self, project: Project):
        super(ParseJSONToInstructions, self).__init__(
            obj=project, action_fn=self.parse)

    def parse(self) -> actions.StepResult:
        """
        Parses Phasar's JSON into a file containing only tainted instructions.
        """

        if not self.obj:
            return
        project = self.obj

        # Define the output directory.
        result_folder = self.RESULT_FOLDER_TEMPLATE.format(
            result_dir=str(CFG["vara"]["outfile"]),
            project_dir=str(project.name))

        prefix = "main::"

        for binary_name in project.BIN_NAMES:

            # get the file name of the JSON Output
            old_result_file = ENVR.get_file_name(
                project_name=str(project.name),
                binary_name=binary_name,
                project_version=str(project.version),
                project_uuid=str(project.run_uuid),
                extension_type=FSE.Success)

            # write new result into a taint propagation report
            result_file = TPR.get_file_name(
                project_name=str(project.name),
                binary_name=binary_name,
                project_version=str(project.version),
                project_uuid=str(project.run_uuid),
                extension_type=FSE.Success)

            tainted_instructions = []

            # parse the old result file
            with open("{res_folder}/{old_res_file}".format(
                    res_folder=result_folder,
                    old_res_file=old_result_file)) as json_data:
                data = json.load(json_data)
                dataflow = data[0]['DataFlow']
                for instruction in dataflow:
                    facts = data[0]['DataFlow'][instruction]['Facts']
                    for fact in facts:
                        if '@getenv' in fact[0]:
                            tainted_instructions.append(
                                # remove 'main::' from the tainted instructions
                                instruction[instruction.startswith(prefix)
                                            and len(prefix):])
                            break

            rm("{res_folder}/{old_res_file}".format(
                res_folder=result_folder,
                old_res_file=old_result_file))

            with open("{res_folder}/{res_file}".format(
                    res_folder=result_folder,
                    res_file=result_file), 'w') as file:
                for instruction in tainted_instructions:
                    file.write("%s\n" % instruction)


class PhasarEnvTracePropagation(PhasarEnvironmentTracing):  # type: ignore
    """
    Generates a inter-procedural data flow analysis (IFDS) on a project's
    binaries and traces environment variables similar to the
    PhasarEnvironmentTracing experiment. The result however gets parsed, that
    FileCheck can validate the propagation against the expected result.
    """

    NAME = "PhasarEnvTracePropagation"

    REPORT_TYPE = ENVR

    def actions_for_project(self, project: Project) -> tp.List[actions.Step]:
        """
        Returns the specified steps to run the project(s) specified in
        the call in a fixed order.
        """
        analysis_actions = super().actions_for_project(project)

        # remove the clean step from the other experiment
        # del analysis_actions[-1]

        analysis_actions.append(ParseJSONToInstructions(project))
        analysis_actions.append(actions.Clean(project))

        return analysis_actions
