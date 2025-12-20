answerset
---------

When pygacity is used to build multidocuments (e.g., a set of assignments or exams with multiple versions), the ``answerset`` subcommand can be used to generate an answer-set document. This document contains the answers to all questions across all versions of the assignments or exams.

By default, pygacity will build an answer-set document if the ``build`` attribute in the YAML configuration file sets the ``answer-file`` attribute. However, if you need to generate the answer-set document separately, you can use the following command:

``pygacity answerset <config_file.yaml>``

where ``<config_file.yaml>`` is the path to the YAML configuration file used for the original multidocument build.