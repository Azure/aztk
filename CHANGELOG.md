
# Changelog

##  0.7.0 (2018-05-01)

[AZTK is now published on pip!](https://pypi.org/project/aztk/) [Documentation has migrated to readthedocs](aztk.readthedocs.io)

This release includes a number of breaking changes. [Please follow the migration for upgrading from 0.6.0.](https://aztk.readthedocs.io/en/v0.7.0/80-migration.html).

**Breaking Changes**

- Moved `docker_repo` under a new `toolkit` key. `docker_repo` is now only used for custom Docker images. Use toolkit for supported images.
- Docker images have been refactored and moved to a different Dockerhub repository. The new supported images are not backwards compatible. See [the documentation on configuration files.](https://aztk.readthedocs.io/en/v0.7.0/13-configuration.html#cluster-yaml)

**Deprecated Features**
- Custom scripts have been removed in favor of Plugins, which are more robust. See, [the documenation on Plugins.](https://aztk.readthedocs.io/en/v0.7.0/15-plugins.html)

**Added Features**
* add internal flag to node commands (#482) ([1eaa1b6](https://github.com/Azure/aztk/commit/1eaa1b6)), closes [#482](https://github.com/Azure/aztk/issues/482)
* Added custom scripts functionality for plugins with the cli(Deprecate custom scripts) (#517 ([c98df7d](https://github.com/Azure/aztk/commit/c98df7d)), closes [#517](https://github.com/Azure/aztk/issues/517)
* disable msrestazure keyring log (#509) ([3cc43c3](https://github.com/Azure/aztk/commit/3cc43c3)), closes [#509](https://github.com/Azure/aztk/issues/509)
* enable mixed mode for jobs (#442) ([8d00a2c](https://github.com/Azure/aztk/commit/8d00a2c)), closes [#442](https://github.com/Azure/aztk/issues/442)
* getting started script (#475) ([7ef721f](https://github.com/Azure/aztk/commit/7ef721f)), closes [#475](https://github.com/Azure/aztk/issues/475)
* JupyterLab plugin (#459) ([da61337](https://github.com/Azure/aztk/commit/da61337)), closes [#459](https://github.com/Azure/aztk/issues/459)
* managed storage for clusters and jobs (#443) ([8aa1843](https://github.com/Azure/aztk/commit/8aa1843)), closes [#443](https://github.com/Azure/aztk/issues/443)
* match cluster submit exit code in cli (#478) ([8889059](https://github.com/Azure/aztk/commit/8889059)), closes [#478](https://github.com/Azure/aztk/issues/478)
* Plugin V2: Running plugin on host (#461) ([de78983](https://github.com/Azure/aztk/commit/de78983)), closes [#461](https://github.com/Azure/aztk/issues/461)
* Plugins (#387) ([c724d94](https://github.com/Azure/aztk/commit/c724d94)), closes [#387](https://github.com/Azure/aztk/issues/387)
* Pypi auto deployement  (#428) ([c237501](https://github.com/Azure/aztk/commit/c237501)), closes [#428](https://github.com/Azure/aztk/issues/428)
* Readthedocs support (#497) ([e361c3b](https://github.com/Azure/aztk/commit/e361c3b)), closes [#497](https://github.com/Azure/aztk/issues/497)
* refactor docker images (#510) ([779bffb](https://github.com/Azure/aztk/commit/779bffb)), closes [#510](https://github.com/Azure/aztk/issues/510)
* Spark add output logs flag (#468) ([32de752](https://github.com/Azure/aztk/commit/32de752)), closes [#468](https://github.com/Azure/aztk/issues/468)
* spark debug tool (#455) ([44a0765](https://github.com/Azure/aztk/commit/44a0765)), closes [#455](https://github.com/Azure/aztk/issues/455)
* spark ui proxy plugin (#467) ([2e995b4](https://github.com/Azure/aztk/commit/2e995b4)), closes [#467](https://github.com/Azure/aztk/issues/467)
* Spark vnet custom dns hostname fix (#490) ([61e7c59](https://github.com/Azure/aztk/commit/61e7c59)), closes [#490](https://github.com/Azure/aztk/issues/490)
* New Toolkit configuration (#507) ([7a7e63c](https://github.com/Azure/aztk/commit/7a7e63c)), closes [#507](https://github.com/Azure/aztk/issues/507)

**Bug Fixes**
* add gitattributes file (#470) ([82ad029](https://github.com/Azure/aztk/commit/82ad029)), closes [#470](https://github.com/Azure/aztk/issues/470)
* add plugins to cluster_install_cmd call (#423) ([216f63d](https://github.com/Azure/aztk/commit/216f63d)), closes [#423](https://github.com/Azure/aztk/issues/423)
* add spark.history.fs.logDirectory to required keys (#456) ([4ef3dd0](https://github.com/Azure/aztk/commit/4ef3dd0)), closes [#456](https://github.com/Azure/aztk/issues/456)
* add support for jars, pyfiles, files in Jobs (#408) ([2dd7891](https://github.com/Azure/aztk/commit/2dd7891)), closes [#408](https://github.com/Azure/aztk/issues/408)
* add timeout handling to cluster_run and copy  (#524) ([47000a5](https://github.com/Azure/aztk/commit/47000a5)), closes [#524](https://github.com/Azure/aztk/issues/524)
* azure file share not being shared with container (#521) ([07ac9b7](https://github.com/Azure/aztk/commit/07ac9b7)), closes [#521](https://github.com/Azure/aztk/issues/521)
* Dependency issue with keyring not having good dependencies (#504) ([5e79a2c](https://github.com/Azure/aztk/commit/5e79a2c)), closes [#504](https://github.com/Azure/aztk/issues/504)
* filter job submission clusters out of cluster list (#409) ([1c31335](https://github.com/Azure/aztk/commit/1c31335)), closes [#409](https://github.com/Azure/aztk/issues/409)
* fix aztk cluster submit paths, imports (#464) ([c1f43c7](https://github.com/Azure/aztk/commit/c1f43c7)), closes [#464](https://github.com/Azure/aztk/issues/464)
* fix broken spark init command (#486) ([a33bdbc](https://github.com/Azure/aztk/commit/a33bdbc)), closes [#486](https://github.com/Azure/aztk/issues/486)
* fix job submission cluster data issues (#533) ([9ccc1c6](https://github.com/Azure/aztk/commit/9ccc1c6)), closes [#533](https://github.com/Azure/aztk/issues/533)
* fix spark job submit path (#474) ([ee1e61b](https://github.com/Azure/aztk/commit/ee1e61b)), closes [#474](https://github.com/Azure/aztk/issues/474)
* make node scripts upload in memory (#519) ([0015e22](https://github.com/Azure/aztk/commit/0015e22)), closes [#519](https://github.com/Azure/aztk/issues/519)
* pypi long description (#450) ([db7a2ef](https://github.com/Azure/aztk/commit/db7a2ef)), closes [#450](https://github.com/Azure/aztk/issues/450)
* remove unnecessary example (#417) ([f1e3f7a](https://github.com/Azure/aztk/commit/f1e3f7a)), closes [#417](https://github.com/Azure/aztk/issues/417)
* Remove unused ssh plugin flags (#488) ([be8cd2a](https://github.com/Azure/aztk/commit/be8cd2a)), closes [#488](https://github.com/Azure/aztk/issues/488)
* set explicit file open encoding (#448) ([5761a36](https://github.com/Azure/aztk/commit/5761a36)), closes [#448](https://github.com/Azure/aztk/issues/448)
* Spark shuffle service worker registration fail (#492) ([013f6e4](https://github.com/Azure/aztk/commit/013f6e4)), closes [#492](https://github.com/Azure/aztk/issues/492)
* throw error if submitting before master elected (#479) ([a59fe8b](https://github.com/Azure/aztk/commit/a59fe8b)), closes [#479](https://github.com/Azure/aztk/issues/479)
* hdfs using wrong conditions (#515) ([a00dbb7](https://github.com/Azure/aztk/commit/a00dbb7)), closes [#515](https://github.com/Azure/aztk/issues/515)
* AZTK_IS_MASTER not set on worker and failing (#506) ([b8a3fcc](https://github.com/Azure/aztk/commit/b8a3fcc)), closes [#506](https://github.com/Azure/aztk/issues/506)
* VNet required error now showing if using mixed mode without it (#440) ([9253aac](https://github.com/Azure/aztk/commit/9253aac)), closes [#440](https://github.com/Azure/aztk/issues/440)
* Worker on master flag ignored and standardize boolean environment (#514) ([5579d95](https://github.com/Azure/aztk/commit/5579d95)), closes [#514](https://github.com/Azure/aztk/issues/514)
* Fix job configuration option for `aztk spark job submit` command (#435) ([4be5ac2](https://github.com/Azure/aztk/commit/4be5ac2)), closes [#435](https://github.com/Azure/aztk/issues/435)
* Fix keyring (#505) ([12450fb](https://github.com/Azure/aztk/commit/12450fb)), closes [#505](https://github.com/Azure/aztk/issues/505)
* Fix the endpoint (#437) ([bcefca3](https://github.com/Azure/aztk/commit/bcefca3)), closes [#437](https://github.com/Azure/aztk/issues/437)
* Fix typo in command_builder 'expecity' -> 'explicitly' (#447) ([27822f4](https://github.com/Azure/aztk/commit/27822f4)), closes [#447](https://github.com/Azure/aztk/issues/447)
* Fix typo load_aztk_screts -> load_aztk_secrets (#421) ([6827181](https://github.com/Azure/aztk/commit/6827181)), closes [#421](https://github.com/Azure/aztk/issues/421)
* Update file to point at master branch (#501) ([4ba3c9d](https://github.com/Azure/aztk/commit/4ba3c9d)), closes [#501](https://github.com/Azure/aztk/issues/501)
* Update storage sdk from 0.33.0 to 1.1.0 (#439) ([f2eb1a4](https://github.com/Azure/aztk/commit/f2eb1a4)), closes [#439](https://github.com/Azure/aztk/issues/439)

**Internal Changes**
* Internal: Cluster data helpers and upload_node_script into cluster_data module (#401) ([2bed496](https://github.com/Azure/aztk/commit/2bed496)), closes [#401](https://github.com/Azure/aztk/issues/401)
* Internal: Move node scripts under aztk and upload all aztk to cluster (#433) ([dfbfead](https://github.com/Azure/aztk/commit/dfbfead)), closes [#433](https://github.com/Azure/aztk/issues/433)

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
