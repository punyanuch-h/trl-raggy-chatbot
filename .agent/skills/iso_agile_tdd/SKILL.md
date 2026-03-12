---
name: agile_tdd_development
description: Rules and guidelines for practicing Agile (2-week sprint) and TDD within an ISO 29110 project structure.
---

# Agile & TDD Guidelines for ISO 29110

You are operating under an Agile methodology (2-week sprints) combined with Test-Driven Development (TDD) while strictly adhering to the ISO 29110 Basic Profile. 

## 1. Test-Driven Development (TDD) Execution
When modifying or adding features to the codebase, you MUST follow the Red-Green-Refactor cycle:
- **Red (Test First)**: Before writing any implementation code, write the test case(s) describing the requirement. Place tests in `SI\04_Test_Cases_and_Procedures`. Run the tests to confirm they fail.
- **Green (Implement)**: Write the minimal amount of code in `SI\03_Source_Code` needed to pass the tests. Run tests and document the successful run in `SI\05_Test_Reports`.
- **Refactor (Improve)**: Improve the code structure without altering behavior. If architectural changes are made, update documentation in `SI\02_Software_Design`.

## 2. Agile (2-Week Sprint) Cadence & Artifact Mapping
- **Sprint Planning**: At the start of the 2-week sprint, establish the work to be done. Update the Sprint Plan and backlog inside `PM\01_Project_Plan`.
- **Requirements Tracking**: Selected user stories must be translated into functional requirements in `SI\01_Requirements_Specification`.
- **Progress Tracking**: Document daily/weekly sprint progress, meeting notes, and blockers in `PM\02_Progress_Status_Record`.
- **Sprint Review**: At the end of the 2-week sprint, the software increment must be built and placed in `SI\07_Product_Release`. Ensure `SI\06_User_Manual` is updated with instructions for the new features.
