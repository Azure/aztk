#!/bin/bash

if  [ "$IS_MASTER" = "1" ]; then
    echo "This is a custom script running on just the master!"
fi

if  [ "$IS_WORKER" = "1" ]; then
    echo "This is a custom script running on just the workers!"
fi

echo "This is a custom script running all workers and the master!"

