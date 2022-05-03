===============
DJANGO GENETICS
===============

Alpha: DO NOT USE IN PRODUCTION
Django Genetics is a Django app that integrate data from  HGNC, OMIM and
web services from mutalyzer.nl and ensembl.org to provide an information
rich data entry for genes an mutation variants


Quick start
-----------

1. Add "genetics" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'genetics',
    ]

2. Run ``python manage.py migrate`` to create the models.

3. Run ``import_gene`` management command to import HGNC and OMIM data.

4. Use in forms ....
