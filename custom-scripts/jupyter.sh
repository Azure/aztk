#!/bin/bash

# This custom script only works on images where jupyter is pre-installed on the Docker image
# 
# This custom script has been tested to work on the following docker images:
#  - jiata/aztk-python:0.1.0-spark2.2.0-anaconda3-5.0.0 (python3.6.2)
#  - jiata/aztk-python:0.1.0-spark2.1.0-anaconda3-5.0.0 (python3.6.2)
#  - jiata/aztk-python:0.1.0-spark1.6.3-anaconda3-5.0.0 (python3.6.2)

if  [ "$IS_MASTER" = "1" ]; then

    PYSPARK_DRIVER_PYTHON="/.pyenv/versions/${USER_PYTHON_VERSION}/bin/jupyter"
    JUPYTER_KERNELS="/.pyenv/versions/${USER_PYTHON_VERSION}/share/jupyter/kernels"

    # disable password/token on jupyter notebook
    jupyter notebook --generate-config --allow-root
    JUPYTER_CONFIG='/.jupyter/jupyter_notebook_config.py'
    echo >> $JUPYTER_CONFIG
    echo -e 'c.NotebookApp.token=""' >> $JUPYTER_CONFIG
    echo -e 'c.NotebookApp.password=""' >> $JUPYTER_CONFIG

    # get master ip
    MASTER_IP=$(hostname -i)

    # remove existing kernels
    rm -rf $JUPYTER_KERNELS/*

    # set up jupyter to use pyspark 
    mkdir $JUPYTER_KERNELS/pyspark
    touch $JUPYTER_KERNELS/pyspark/kernel.json
    cat << EOF > $JUPYTER_KERNELS/pyspark/kernel.json
{
    "display_name": "PySpark",
    "language": "python",
    "argv": [
        "python",
        "-m",
        "ipykernel",
        "-f",
        "{connection_file}"
    ],
    "env": {
        "SPARK_HOME": "$SPARK_HOME",
        "PYSPARK_PYTHON": "python",
        "PYSPARK_SUBMIT_ARGS": "--master spark://$MASTER_IP:7077 pyspark-shell"
    }
}
EOF

    # start jupyter notebook from /jupyter
    cd /jupyter
    (PYSPARK_DRIVER_PYTHON=$PYSPARK_DRIVER_PYTHON PYSPARK_DRIVER_PYTHON_OPTS="notebook --no-browser --port=8888 --allow-root" pyspark &)
fi


