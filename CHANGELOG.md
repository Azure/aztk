# Changelog

##  0.10.2 (2018-12-07)

**Bug Fixes**
* Fix: Storage table never deleted (#690) ([723995c](https://github.com/Azure/aztk/commit/723995c)), closes [#690](https://github.com/Azure/aztk/issues/690)

**Internal Changes**
* Internal: Migrate off preview vsts queues (#685) ([a91690b](https://github.com/Azure/aztk/commit/a91690b)), closes [#685](https://github.com/Azure/aztk/issues/685)


##  0.10.1 (2018-11-02)

**Features**
* Include cluster creation time in cluster list and cluster get output (#678) ([a0bc2f0](https://github.com/Azure/aztk/commit/a0bc2f0)), closes [#678](https://github.com/Azure/aztk/issues/678)

**Bug Fixes**
* Verify Batch task has node_info (#681) ([385040d](https://github.com/Azure/aztk/commit/385040d)), closes [#681](https://github.com/Azure/aztk/issues/681)


##  0.10.0 (2018-10-29)

**Breaking Changes**
* Remove deprecated SDK API code (#671) ([fc50536](https://github.com/Azure/aztk/commit/fc50536)), closes [#671](https://github.com/Azure/aztk/issues/671)
* Remove custom scripts (#673) ([9e32b4b](https://github.com/Azure/aztk/commit/9e32b4b)), closes [#673](https://github.com/Azure/aztk/issues/673)
* Replaced states with Enums for ClusterState, JobState, ApplicationState (#677) ([e486536](https://github.com/Azure/aztk/commit/e486536)), closes [#677](https://github.com/Azure/aztk/issues/677)

**Features**
* Spark retry docker pull (#672) ([18b74e4](https://github.com/Azure/aztk/commit/18b74e4)), closes [#672](https://github.com/Azure/aztk/issues/672)
* Spark scheduling target (#661) ([4408c4f](https://github.com/Azure/aztk/commit/4408c4f)), closes [#661](https://github.com/Azure/aztk/issues/661)
* Spark submit scheduling internal (#674) ([8c2bf0c](https://github.com/Azure/aztk/commit/8c2bf0c)), closes [#674](https://github.com/Azure/aztk/issues/674)


##  0.9.1 (2018-10-5)
**Bug Fixes**
* Fix: pin all node dependencies not in Pipfile (#667) ([0606598](https://github.com/Azure/aztk/commit/0606598)), closes [#667](https://github.com/Azure/aztk/issues/667)
* Fix: vsts integration tests block (#657) ([4a60c8a](https://github.com/Azure/aztk/commit/4a60c8a)), closes [#657](https://github.com/Azure/aztk/issues/657)
* Fix: vsts mutliline secrets (#668) ([cb62207](https://github.com/Azure/aztk/commit/cb62207)), closes [#668](https://github.com/Azure/aztk/issues/668)


##  0.9.0 (2018-08-30)

**Breaking Changes**
* spark roll back scheduling disable (#653) ([93615d9](https://github.com/Azure/aztk/commit/93615d9)), closes [#653](https://github.com/Azure/aztk/issues/653)
* remove custom scripts (#650) ([442228a](https://github.com/Azure/aztk/commit/442228a)), closes [#650](https://github.com/Azure/aztk/issues/650)
* 0.9.0 deprecated code removal (#645) ([eef36dc](https://github.com/Azure/aztk/commit/eef36dc)), closes [#645](https://github.com/Azure/aztk/issues/645)
* SDK refactor (#622) ([b18eb69](https://github.com/Azure/aztk/commit/b18eb69)), closes [#622](https://github.com/Azure/aztk/issues/622)

**Features**
* Add ability to specify docker run options in toolkit config (#613) ([9d554c3](https://github.com/Azure/aztk/commit/9d554c3)), closes [#613](https://github.com/Azure/aztk/issues/613) [#3](https://github.com/Azure/aztk/issues/3)
* add brief flag to debug tool (#634) ([b7bdd8c](https://github.com/Azure/aztk/commit/b7bdd8c)), closes [#634](https://github.com/Azure/aztk/issues/634)
* first run docs update (#644) ([9098533](https://github.com/Azure/aztk/commit/9098533)), closes [#644](https://github.com/Azure/aztk/issues/644)
* SDK refactor (#622) ([b18eb69](https://github.com/Azure/aztk/commit/b18eb69)), closes [#622](https://github.com/Azure/aztk/issues/622)

**Bug Fixes**
* diagnostics function write error result bug (#649) ([293f297](https://github.com/Azure/aztk/commit/293f297)), closes [#649](https://github.com/Azure/aztk/issues/649)
* expose get cluster configuration API (#648) ([7c14648](https://github.com/Azure/aztk/commit/7c14648)), closes [#648](https://github.com/Azure/aztk/issues/648)
* remove bad node scripts import (#652) ([0a9ce94](https://github.com/Azure/aztk/commit/0a9ce94)), closes [#652](https://github.com/Azure/aztk/issues/652)
* typo in vsts build (#654) ([7c37b06](https://github.com/Azure/aztk/commit/7c37b06)), closes [#654](https://github.com/Azure/aztk/issues/654)
* update incompatible dependencies in setup.py (#639) ([f98d037](https://github.com/Azure/aztk/commit/f98d037)), closes [#639](https://github.com/Azure/aztk/issues/639)

**Internal Changes**
* fix pylint warnings (#651) ([828162e](https://github.com/Azure/aztk/commit/828162e)), closes [#651](https://github.com/Azure/aztk/issues/651)
* update vsts build (#635) ([6eda21e](https://github.com/Azure/aztk/commit/6eda21e)), closes [#635](https://github.com/Azure/aztk/issues/635)
* verify code formatting in build (#633) ([7730c46](https://github.com/Azure/aztk/commit/7730c46)), closes [#633](https://github.com/Azure/aztk/issues/633)


##  0.8.1 (2018-06-20)

**Bug Fixes**
* docs links version (#614) ([a8f8e92](https://github.com/Azure/aztk/commit/a8f8e92)), closes [#614](https://github.com/Azure/aztk/issues/614)
* set defaults for SparkConfiguration, add tests (#606) ([5306a2a](https://github.com/Azure/aztk/commit/5306a2a)), closes [#606](https://github.com/Azure/aztk/issues/606)
* spark debug tool filter out .venv, make debug tool testable (#612) ([4e0b1ec](https://github.com/Azure/aztk/commit/4e0b1ec)), closes [#612](https://github.com/Azure/aztk/issues/612)
* Suppress msrest warnings (#611) ([883980d](https://github.com/Azure/aztk/commit/883980d)), closes [#611](https://github.com/Azure/aztk/issues/611)


##  0.8.0 (2018-06-12)

**Deprecated Features**
* ClusterConfiguration fields vm_count and vm_count_low_pri have been renamed to size and size_low_priority
* command line flag `--size-low-pri` for `aztk spark cluster create` has been replaced with `--size-low-priority`
* `default` secrets.yaml block has been deprecated, place all child parameters directly at the root
* Spark version 1.6 has been deprecated

**Added Features**
* add cluster list quiet flag, ability to compose with delete (#581) ([88d0419](https://github.com/Azure/aztk/commit/88d0419)), closes [#581](https://github.com/Azure/aztk/issues/581)
* add node run command (#572) ([af449dc](https://github.com/Azure/aztk/commit/af449dc)), closes [#572](https://github.com/Azure/aztk/issues/572)
* Add VSTS CI (#561) ([66037fd](https://github.com/Azure/aztk/commit/66037fd)), closes [#561](https://github.com/Azure/aztk/issues/561)
* Disable scheduling on group of nodes (#540) ([8fea9ce](https://github.com/Azure/aztk/commit/8fea9ce)), closes [#540](https://github.com/Azure/aztk/issues/540)
* New Models design with auto validation, default and merging (#543) ([02f336b](https://github.com/Azure/aztk/commit/02f336b)), closes [#543](https://github.com/Azure/aztk/issues/543)
* nvBLAS and OpenBLAS plugin (#539) ([603a413](https://github.com/Azure/aztk/commit/603a413)), closes [#539](https://github.com/Azure/aztk/issues/539)
* pure python ssh (#577) ([f16aac0](https://github.com/Azure/aztk/commit/f16aac0)), closes [#577](https://github.com/Azure/aztk/issues/577)
* Support passing of remote executables via aztk spark cluster submit (#549) ([f6735cc](https://github.com/Azure/aztk/commit/f6735cc)), closes [#549](https://github.com/Azure/aztk/issues/549)
* TensorflowOnSpark python plugin (#525) ([1527929](https://github.com/Azure/aztk/commit/1527929)), closes [#525](https://github.com/Azure/aztk/issues/525)
* Conda, Apt-Get and Pip Install Plugins (#594) ([fbf1bab](https://github.com/Azure/aztk/commit/fbf1bab)), closes [#594](https://github.com/Azure/aztk/issues/594)
* Warnings show stacktrace on verbose (#587) ([b9a863b](https://github.com/Azure/aztk/commit/b9a863b)), closes [#587](https://github.com/Azure/aztk/issues/587)

**Bug Fixes**
* add toolkit to sdk docs and example ([d688c9c](https://github.com/Azure/aztk/commit/d688c9c))
* --size-low-pri being ignored (#593) ([fa3ac0e](https://github.com/Azure/aztk/commit/fa3ac0e)), closes [#593](https://github.com/Azure/aztk/issues/593)
* fix typos (#595) ([7d7a814](https://github.com/Azure/aztk/commit/7d7a814)), closes [#595](https://github.com/Azure/aztk/issues/595)
* getting started script reuse aad application (#569) ([3d16cf3](https://github.com/Azure/aztk/commit/3d16cf3)), closes [#569](https://github.com/Azure/aztk/issues/569)
* models v2 deserialization (#584) ([1eeff23](https://github.com/Azure/aztk/commit/1eeff23)), closes [#584](https://github.com/Azure/aztk/issues/584)
* optimize start task (#582) ([e5e529a](https://github.com/Azure/aztk/commit/e5e529a)), closes [#582](https://github.com/Azure/aztk/issues/582)
* remove deprecated vm_count call (#586) ([dbde8bc](https://github.com/Azure/aztk/commit/dbde8bc)), closes [#586](https://github.com/Azure/aztk/issues/586)
* Remove old spark-defaults.conf jars (#567) ([8b8cd62](https://github.com/Azure/aztk/commit/8b8cd62)), closes [#567](https://github.com/Azure/aztk/issues/567)
* set logger to stdout (#588) ([3f0c8f9](https://github.com/Azure/aztk/commit/3f0c8f9)), closes [#588](https://github.com/Azure/aztk/issues/588)
* switch create user to pool wide (#574) ([49a890a](https://github.com/Azure/aztk/commit/49a890a)), closes [#574](https://github.com/Azure/aztk/issues/574)
* switch from pycryptodome to pycryptodomex (#564) ([19dde42](https://github.com/Azure/aztk/commit/19dde42)), closes [#564](https://github.com/Azure/aztk/issues/564)
* allow cluster config to be printed when no username has been set (#597) ([1cc71c7](https://github.com/Azure/aztk/commit/1cc71c7)), closes [#597](https://github.com/Azure/aztk/issues/597)


##  0.7.1 (2018-05-11)

**Bug Fixes**
* Fix: create virtual environment even if container exists ([2db7b00](https://github.com/Azure/aztk/commit/2db7b00))
* Fix: gitattributes for jar files (#548) ([a18660b](https://github.com/Azure/aztk/commit/a18660b)), closes [#548](https://github.com/Azure/aztk/issues/548)
* Fix: pass docker repo command back to the cluster config (#538) ([a99bbe1](https://github.com/Azure/aztk/commit/a99bbe1)), closes [#538](https://github.com/Azure/aztk/issues/538)

##  0.7.0 (2018-05-01)

[AZTK is now published on pip!](https://pypi.org/project/aztk/) [Documentation has migrated to readthedocs](aztk.readthedocs.io)

This release includes a number of breaking changes. [Please follow the migration for upgrading from 0.6.0.](https://aztk.readthedocs.io/en/v0.7.0/80-migration.html).

**Breaking Changes**

- Moved `docker_repo` under a new `toolkit` key. `docker_repo` is now only used for custom Docker images. Use toolkit for supported images.
- Docker images have been refactored and moved to a different Dockerhub repository. The new supported images are not backwards compatible. See [the documentation on configuration files.](https://aztk.readthedocs.io/en/v0.7.0/13-configuration.html#cluster-yaml)

**Deprecated Features**
- Custom scripts have been removed in favor of Plugins, which are more robust. See, [the documentation on Plugins.](https://aztk.readthedocs.io/en/v0.7.0/15-plugins.html)

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
* Pypi auto deployment  (#428) ([c237501](https://github.com/Azure/aztk/commit/c237501)), closes [#428](https://github.com/Azure/aztk/issues/428)
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
- fix type error crash if no jars are specified in job submission
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
