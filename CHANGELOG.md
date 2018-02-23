# Changelog

## 0.6.0 Mixed Mode, Cluster Run & Copy

**Features:**
- `aztk spark init` customization flags
- `aztk spark cluster run` command added
- `aztk spark cluster copy` command added
- enable Spark dynamic allocation by default
- add SDK support for file-like objects
- add Spark integration tests
- add flag `worker_on_master` option for cluster and job submission mode
- Spark driver runs on master node for single application job submission mode

**Bug Fixes:**
- load jars in `.aztk/jars/` in job submission mode
- replace outdated error in cluster_create
- fix type error crash if not jars are specificed in job submission
- stop using mutable default parameters
- print job application code if exit_code is 0
- job submission crash if executor or driver cores specified
- wrong error thrown if user added before master node picked

## 0.5.1 Job Submission, AAD, VNET

Major Features:
- [Job Submission](docs/70-jobs.md)
- AAD Support, see [Getting Started](docs/00-getting-started.md)
- VNET Support

**Breaking changes:**
* `SecretsConfiguration` inputs changed. Check in [SDK](docs/50-sdk.md) for the new format

## 0.5.0 SDK
## 0.3.1 List cluster only list spark cluster
## 0.3.0 New CLI with one command `aztk`
## 0.2.0 Spark use start task instead of
## 0.1.0 Initial
