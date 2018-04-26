# Tests

AZTK comes with a testing library that can be used for verification, and debugging. Please note that some tests will provision and test real resources in Azure, and as a result, will cost money to run. See [Integration Tests](#integration-tests) for more details.

## Integration Tests

Integration tests use the credentials given in your `.aztk/secrets.yaml` file to spin up real Clusters and Jobs to verify the functionality of the library. Please note that these tests __will__ cost money to run. All created Clusters nad Jobs will be deleted when the test completes.

Since each integration test spins up a Cluster or Job, you may want to run the tests in parallel to reduce the time needed to complete the testing library:

```sh
pytest $path_to_repo_root -n <5>
```
_Note: $path_to_repo_root represents the path to the root of the aztk repository, and is only required if you are running the tests from a different location._

Please note that the number passed to the `-n` flag determines the number of tests you wish to run in parallel. Parallelizing the tests will increase the number of CPU cores used at one time, so please verify that you have the available core quota in your Batch account.

