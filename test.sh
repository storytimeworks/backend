#!/bin/bash

mysql -uroot < init_db.sql
python setup.py test
