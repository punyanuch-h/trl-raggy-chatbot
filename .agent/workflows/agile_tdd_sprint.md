---
description: Implement a feature using Agile (2-week sprint) and TDD under the ISO 29110 standard
---

## Phase 1: Sprint Planning & Setup
1. **Identify User Story**: Select the user story or feature from the backlog to implement for the current 2-week sprint.
2. **Specify Requirements**: Document the exact functional or non-functional requirement inside `SI/01_Requirements_Specification/`.
3. **Update Plan**: Update the sprint plan and resource mapping inside `PM/01_Project_Plan/`.

## Phase 2: TDD Cycle - RED (Write Tests First)
1. **Write Test Cases**: Write testing code (or manual procedures) inside `SI/04_Test_Cases_and_Procedures/` directly mapped to the requirement.
2. **Execute Tests**: Run the test suite.
3. **Verify Failure**: Confirm that the tests fail, as the new feature hasn't been implemented yet.

## Phase 3: TDD Cycle - GREEN (Write Implementation Code)
1. **Implement Minimal Code**: Write the bare minimum code inside `SI/03_Source_Code/` needed to make the tests pass.
2. **Rerun Tests**: Execute the test suite again.
3. **Report Execution**: Save the test execution log or result report referencing the test ID to `SI/05_Test_Reports/`.

## Phase 4: TDD Cycle - REFACTOR (Optimization & Architecture)
1. **Refine Code**: Refactor the codebase to clean up the logic without changing external behavior.
2. **Verify Tests Pass**: Make sure all tests remain green.
3. **Document Architecture**: Document any complex logic, database schema changes, or API structures in `SI/02_Software_Design/`.

## Phase 5: Sprint Review & Release
1. **Prepare Release**: Build the product increment and store the binaries, dependencies, or configuration instructions in `SI/07_Product_Release/`.
2. **Update Manuals**: Document the new interface/feature instructions in `SI/06_User_Manual/`.
3. **Record Progress**: Mark the implementation task complete tracking hours/status in `PM/02_Progress_Status_Record/`.
