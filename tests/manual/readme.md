## Functional tests openvcloud

Manual test plans for checking the OpenvCloud functionality.
Currently two sets of tests are foreseen:
* Tests from an end user perspective ( [Normal](end_user.md) - [Extended](end_user_extended.md) )
* Tests from an operator perspective ( [Normal](operator.md) - [Extended](operator.md) )

Each test set has a quick (normal) test and an extended test. The normal test is intended to be performed on a daily basis and for quick validation of environments.
The extended tests are to be executed for validation a software release as they check functionality that is more code related rather then being influenced by the environment setup.

To execute the tests, be sure to pull the latest version from git. Modify the testresults as appropriate and be sure to add a comment or a youtrack issue link for failing ones.
Commit and push after finishing. Git will track who executed the tests, when they were performed and the history.