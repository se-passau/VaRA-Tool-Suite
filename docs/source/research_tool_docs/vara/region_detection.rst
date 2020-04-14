****************
Region Detection
****************

VaRA offers different region detection passes, that translate extra information, store in meta-data, into in memory representations for further analysis.
Each pass walks over the IR, analysing the IR structure and region related higher-level semantic data, and creates regions of it's specific type.
These region detection passes can range from a simple meta-data extraction up to a data-flow based extraction, where the semantic of the region is based on data-flow dependencies between instructions.
The following list gives an overview of different region detections currently supported by VaRA.

* Commit-Region Detection

  Extract the stored information from commit annotations, see :ref:`Commit Region <commit-regions-annotation>`.
  To run this detection add ``-vara-CD`` to our opt run line.

  .. code-block:: bash

    opt -vara-CD example.ll

* Taint-Analysis based Feature Detection

  The Taint Feature Detection extracts certain IR-code regions related to a feature variable, using a taint analysis. These regions can then be used for other analyses.
  We need to generate an LLVM-IR file. This is done by calling clang with the options -S, -emit-llvm. If we want to load our own feature config file we specify it with -mllvm -feature-config.

  .. code-block:: bash

    clang -S -emit-llvm -fvara-IFA foo.c
    clang -S -emit-llvm -fvara-IFA -feature-config=PATH foo.c

  This now generates an LLVM-IR file that is enriched with feature metadata and feature condition metadata. Then we run a taint analysis to track which possible feature conditions are controlled by feature variables.
