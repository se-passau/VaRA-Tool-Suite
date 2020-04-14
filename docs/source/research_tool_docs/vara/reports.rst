****************
Analysis Reports
****************

In order to further process or visualize the analysis results VaRA provides different report passes. Reports combine different analyses and persist the calculated results in a YAML file.

BlameReport
-----------

The blame report pass first runs a data-flow analysis, computing interaction between commits, second it generates a YAML report containing all results split up in different documents. The following listing shows how an example output is structured:

.. code-block:: yaml

  ---
  result-map:
    abort_gzip:
      demangled-name:  abort_gzip
      insts:           []
    abort_gzip_signal:
      demangled-name:  abort_gzip_signal
      insts:
        - base-hash:       30ba4a2b69e5ee34c3fcde12f275f80d1fbe8a59
          interacting-hashes:
            - 8b83dc0f588ccaed3bd7e37208cefab2ff4edb28
          amount:          3
        - base-hash:       30ba4a2b69e5ee34c3fcde12f275f80d1fbe8a59
          interacting-hashes:
            - a979d9c4db0adbf341eb329abaf3560aa12f10fd
          amount:          3
        - base-hash:       a979d9c4db0adbf341eb329abaf3560aa12f10fd
          interacting-hashes:
            - 30ba4a2b69e5ee34c3fcde12f275f80d1fbe8a59
          amount:          1

The report file can be generated direclty with opt.

.. code-block:: bash

  opt -vara-BD -vara-BR -vara-init-commits -vara-report-outfile=report_file.yaml example.ll
