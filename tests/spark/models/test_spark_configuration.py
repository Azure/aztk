from aztk.spark.models import SparkConfiguration
from aztk.error import InvalidModelError


def test_spark_configuration_defaults():
    spark_configuration = SparkConfiguration()
    spark_configuration.validate()

    assert spark_configuration.spark_defaults_conf is None
    assert spark_configuration.spark_defaults_conf is None
    assert spark_configuration.spark_defaults_conf is None


def test_spark_configuration_fields():
    spark_configuration = SparkConfiguration(
        spark_defaults_conf="spark-defaults.conf",
        spark_env_sh="spark-env.sh",
        core_site_xml="core-site.xml",
    )
    spark_configuration.validate()

    assert spark_configuration.spark_defaults_conf == "spark-defaults.conf"
    assert spark_configuration.spark_env_sh == "spark-env.sh"
    assert spark_configuration.core_site_xml == "core-site.xml"
