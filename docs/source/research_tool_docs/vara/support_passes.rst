**************
Support Passes
**************

Git meta-data rewriter
----------------------

VaRA's different git annotations embed repository specific meta-data into bitcode files.
One data point that allows further analyses to find the related git repository are system specific paths.
These paths need to be adapted when the generated bitcode file is move to different machine.
To make changing this meta-data simple, VaRA offers a rewriter pass that can adapt the system specific details.

.. code-block:: bash

  opt -vara-rewriteMD -vara-git-mappings="RepoName:NewPath" ...
