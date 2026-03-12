# ISO 29110 Test Reporting Protocol (DoD)

## Directory Purpose
This directory (`SI/05_Test_Reports/`) exists to strictly enforce the **Definition of Done (DoD)** outlined in the Sprint 1 Plan. Under ISO 29110, an Agile TDD software increment must maintain chronological proof of testing success.

## Test Logging Script Instructions
During **Sprint 1, Ticket 1**, a test automation script (e.g., `run_tests.bat`) will be developed at the root of the project.

This script must be executed before a sprint ticket is marked "Done". It will automatically capture the raw output of `pytest` and pipe it into this directory.

A standard log will look like: 
`test_log_YYYYMMDD_HHMMSS.txt`

The log MUST confirm 100% test coverage for the developed feature to satisfy the DoD.
