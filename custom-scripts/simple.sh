#!/bin/bash

# Demo plugin. Not actually meant to be used.

if  [ "$AZTK_IS_MASTER" = "true" ]; then
    echo "This is a custom script running on just the master!"
fi

if  [ "$AZTK_IS_WORKER" = "true" ]; then
    echo "This is a custom script running on just the workers!"
fi

echo "This is a custom script running all workers and the master!"

