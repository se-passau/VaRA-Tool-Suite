"""
Execute showcase cpp examples with Phasar's tracing of environment variables.
We run the analysis on exemplary cpp files. The cpp examples can be
found in the https://github.com/se-passau/vara-perf-tests repository.
The result JSON is then parsed into an LLVM IR file contaning only the
instructions tainted by the environment variable of the cpp file.
"""

import json
import typing as tp

from plumbum import ProcessExecutionError

import benchbuild.utils.actions as actions
from benchbuild.settings import CFG
from benchbuild.project import Project
from benchbuild.utils.cmd import rm, echo, FileCheck
from varats.experiments.phasar_env_analysis import PhasarEnvironmentTracing
from varats.data.reports.taint_report import TaintPropagationReport as TPR
from varats.data.reports.env_trace_report import EnvTraceReport as ENVR
from varats.data.report import FileStatusExtension as FSE
from varats.utils.experiment_util import (
    exec_func_with_pe_error_handler, FunctionPEErrorWrapper,
    PEErrorHandler)


class ParseAndValidatePhasarOutput(actions.Step):  # type: ignore
    """
    Analyse a project with Phasar's IFDS that traces environment variables
    inside a project.
    """

    NAME = "ParseAndValidatePhasarOutput"
    DESCRIPTION = "Parses Phasar's JSON into only the tainted instructions."\
        + "Also the parsed results get validated with LLVM FileCheck."

    RESULT_FOLDER_TEMPLATE = "{result_dir}/{project_dir}"

    FC_FILE_SOURCE_DIR = "{tmp_dir}/{project_src}/{project_name}"
    EXPECTED_FC_FILE = "{binary_name}.txt"

    def __init__(self, project: Project):
        super(ParseAndValidatePhasarOutput, self).__init__(
            obj=project, action_fn=self.filecheck)

    def filecheck(self) -> actions.StepResult:
        """
        Compare the generated results against the expected result.
        First the result files are read, printed and piped into FileCheck.
        """

        if not self.obj:
            return
        project = self.obj

        # Define the output directory.
        result_folder = self.RESULT_FOLDER_TEMPLATE.format(
            result_dir=str(CFG["vara"]["outfile"]),
            project_dir=str(project.name))

        # The temporary directory the project is stored under
        tmp_repo_dir = self.FC_FILE_SOURCE_DIR.format(
            tmp_dir=str(CFG["tmp_dir"]),
            project_src=str(project.SRC_FILE),
            project_name=str(project.name))

        timeout_duration = '3h'

        for binary_name in project.BIN_NAMES:

            # get the file name of the JSON Output
            old_result_file = ENVR.get_file_name(
                project_name=str(project.name),
                binary_name=binary_name,
                project_version=str(project.version),
                project_uuid=str(project.run_uuid),
                extension_type=FSE.Success)

            # Define output file name of failed runs
            error_file = "phasar-" + TPR.get_file_name(
                project_name=str(project.name),
                binary_name=binary_name,
                project_version=str(project.version),
                project_uuid=str(project.run_uuid),
                extension_type=FSE.Failed,
                file_ext=TPR.FILE_TYPE)

            # The file name of the text file with the expected filecheck regex
            expected_file = self.EXPECTED_FC_FILE.format(
                binary_name=binary_name)

            # write new result into a taint propagation report
            result_file = "phasar-" + TPR.get_file_name(
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
                                instruction.split("::", 1)[1])
                            break

            # remove the no longer needed json files
            rm("{res_folder}/{old_res_file}".format(
                res_folder=result_folder,
                old_res_file=old_result_file))

            # validate the result with filecheck
            array_string = ""
            for inst in tainted_instructions:
                array_string += inst + "\n"

            file_check_cmd = FileCheck["{fc_dir}/{fc_exp_file}".format(
                fc_dir=tmp_repo_dir, fc_exp_file=expected_file)]

            cmd_chain = (echo[array_string] | file_check_cmd
                         > "{res_folder}/{res_file}".format(
                res_folder=result_folder,
                res_file=result_file))

            try:
                exec_func_with_pe_error_handler(
                    cmd_chain,
                    PEErrorHandler(result_folder, error_file,
                                   cmd_chain, timeout_duration))
            # remove the success file on error in the filecheck.
            except ProcessExecutionError:
                rm("{res_folder}/{res_file}".format(
                    res_folder=result_folder,
                    res_file=result_file))


class PhasarEnvTracePropagation(PhasarEnvironmentTracing):  # type: ignore
    """
    Generates a inter-procedural data flow analysis (IFDS) on a project's
    binaries and traces environment variables similar to the
    PhasarEnvironmentTracing experiment. The result however gets parsed, that
    FileCheck can validate the propagation against the expected result.
    """

    NAME = "PhasarEnvTracePropagation"

    REPORT_TYPE = TPR

    def actions_for_project(self, project: Project) -> tp.List[actions.Step]:
        """
        Returns the specified steps to run the project(s) specified in
        the call in a fixed order.
        """
        analysis_actions = super().actions_for_project(project)

        # remove the clean step from the other experiment
        del analysis_actions[-1]

        analysis_actions.append(ParseAndValidatePhasarOutput(project))
        analysis_actions.append(actions.Clean(project))

        return analysis_actions
