#!/bin/bash
activate="envosdr/bin/activate"
if [ ! -f "$activate" ]
then
    echo "ERROR: activate not found at $activate"
    return 1
fi
. "$activate"
flask run
deactivate
