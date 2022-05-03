# -*- coding: utf-8 -*-
import csv
import logging
from django.db import transaction
from django.core.management.base import BaseCommand
from django.conf import settings

from genetics.models import HgncGene, OmimGene, OmimTitle, OmimPhenotype

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '''Imports Gene data from HGNC and OMIM'''

    def handle(self, *args, **options):
        ############# HGNC GENE
        # HGNC ID	Status	Approved symbol	Approved name	Chromosome location	Orphanet ID	OMIM ID
        # 0 HGNC ID   1 Approved symbol     2 Approved name      3 Status      4 Alias symbols     5 Chromosome       6 RefSeq IDs    7 Alias names     8 OMIM ID(supplied by OMIM)
        # ==> genetics.models.HgncGene
        # hgnc_id	Status	approved_symbol	approved_name	chromosome_location	orphanet_id	omim_id
        hgnc_gene_columns = {
            'hgnc_id': 0,
            'approved_symbol': 1,
            'approved_name': 2,
            'alias_symbols': 4,
            'alias_names': 2,
            'chromosome_location': 5,
            'omim_id': 8
        }
        ############# OMIM MORBID MAP
        # Phenotype	Gene Symbols	MIM Number	Cyto Location
        # ==> genetics.models.OmimGene
        # ---------	gene_symbols	omim_id 	chromosome_location
        # ==> genetics.models.OmimPhenotype
        # phenotype
        morbid_map_columns = {
            'phenotype': 0,
            'gene_symbols': 1,
            'mim_number': 2,
            'chromosome_location': 3,
        }
        ############# OMIM MIMTITLES
        # Prefix	MIM Number	Preferred Title; symbol	Alternative Title(s); symbol(s)
        # ==> genetics.models.OmimTitle
        # prefix	omim_gene	preferred               alternative
        mim_titles_columns = {
            'prefix': 0,
            'mim_number': 1,
            'preferred': 2,
            'alternative': 3,
        }

        try:
            with transaction.atomic():
                ############# HGNC GENE
                if True:
                    file_path = ("%s/../genetics/data/hgnc/HGNC Gene w alias.csv" % settings.BASE_DIR)
                    logger.info("Importing HGNC GENE w alias.csv")
                    with open(file_path, 'r', errors='ignore') as file_hgnc_gene:
                        csv_reader = csv.reader(file_hgnc_gene, delimiter=',', quotechar='"')
                        for row in csv_reader:
                            if row[0] != "HGNC ID": #salto la prima riga
                                try:
                                    # se non esiste già (ho verificato: hgnc_id è univoco)
                                    if not HgncGene.objects.filter(hgnc_id=row[hgnc_gene_columns['hgnc_id']]).exists():
                                        HgncGene.objects.create(
                                            hgnc_id=row[hgnc_gene_columns['hgnc_id']],
                                            approved_symbol=row[hgnc_gene_columns['approved_symbol']],
                                            approved_name=row[hgnc_gene_columns['approved_name']],
                                            alias_symbols=row[hgnc_gene_columns['alias_symbols']],
                                            alias_names=row[hgnc_gene_columns['alias_names']],
                                            chromosome_location=row[hgnc_gene_columns['chromosome_location']],
                                            mim_number=row[hgnc_gene_columns['omim_id']],
                                        )

                                except Exception as ex:
                                    logger.error("Non blocking error importing HGNC Gene: %s" % (str(ex)))
                ############# OMIM MORBID MAP
                if True:
                    file_path = ("%s/../genetics/data/omim/morbidmap.csv" % settings.BASE_DIR)
                    logger.info("Importing OMIM morbidmap.csv")
                    with open(file_path, 'r', errors='ignore') as file_omim_morbidmap:
                        csv_reader = csv.reader(file_omim_morbidmap, delimiter=',', quotechar='"')
                        for row in csv_reader:
                            if row[0] != '# Phenotype': #salto la prima riga
                                try:
                                    # se non esiste già (ho verificato: hgnc_id è univoco)
                                    if not OmimGene.objects.filter(mim_number=row[morbid_map_columns['mim_number']]).exists():
                                        og = OmimGene.objects.create(
                                            mim_number=row[morbid_map_columns['mim_number']],
                                            gene_symbols=row[morbid_map_columns['gene_symbols']],
                                            chromosome_location=row[morbid_map_columns['chromosome_location']]
                                        )
                                    else:
                                        og = OmimGene.objects.get(mim_number=row[morbid_map_columns['mim_number']])
                                        # per ora non verifico gli altri campi ....
                                    if not og.phenotypes.filter(phenotype=row[morbid_map_columns['phenotype']]).exists():
                                        OmimPhenotype.objects.create(omim_gene=og,
                                                                     phenotype=row[morbid_map_columns['phenotype']])
                                except Exception as ex:
                                    logger.error("Non blocking error importing OMIM morbidmap: %s" % (str(ex)))
                ############# OMIM MIMTITLES
                if True:
                    file_path = ("%s/../genetics/data/omim/mimTitles.csv" % settings.BASE_DIR)
                    logger.info("Importing OMIM mimTitles.csv")
                    with open(file_path, 'r', errors='ignore') as file_omim_titles:
                        csv_reader = csv.reader(file_omim_titles, delimiter=',', quotechar='"')
                        for row in csv_reader:
                            if row[0] != 'Prefix': #salto la prima riga
                                try:
                                    # se non esiste già [ho controllato solo una riga per ciascun mim_numer]
                                    if not OmimTitle.objects.filter(omim_gene__mim_number=row[mim_titles_columns['mim_number']]).exists():
                                        og = OmimTitle.objects.create(
                                            omim_gene=OmimGene.objects.get(mim_number=row[mim_titles_columns['mim_number']]),
                                            prefix=row[mim_titles_columns['prefix']],
                                            preferred=row[mim_titles_columns['preferred']],
                                            alternative=row[mim_titles_columns['alternative']],
                                        )
                                    else:
                                        og = OmimTitle.objects.get(omim_gene__mim_number=row[mim_titles_columns['mim_number']])
                                        # per ora non verifico gli altri campi ....
                                        og.prefix = row[mim_titles_columns['prefix']]
                                        og.preferred = row[mim_titles_columns['preferred']]
                                        og.alternative = row[mim_titles_columns['alternative']]
                                        og.save()
                                except Exception as ex:
                                    # se OmimGene non esiste è perché non è presente in morbidmap
                                    logger.error("Non blocking error importing OMIM morbidmap: %s" % (str(ex)))
                                    logger.error("Row: %s" % row)
        except Exception as ex:
            logger.error("Blocking error importing HGNC / OMIM data: %s" % str(ex))
        print("END!")
        logger.info("END END END importing OMIM morbidmap END END END")
