# -*- coding: utf-8 -*-
from django.db import models


class HgncGene(models.Model):
    """
    Importo solo gli approved
    """
    hgnc_id = models.CharField(max_length=50, db_index=True)
    approved_symbol = models.CharField(max_length=100, db_index=True)
    alias_symbols = models.CharField(max_length=255, db_index=True, null=True, blank=True)
    approved_name = models.CharField(max_length=250)
    alias_names = models.CharField(max_length=250, null=True, blank=True)
    chromosome_location = models.CharField(max_length=50, db_index=True, null=True, blank=True)
    orphanet_id = models.CharField(max_length=50, db_index=True, null=True, blank=True)  # non viene più esportato ?
    mim_number = models.CharField(max_length=50, db_index=True, null=True, blank=True)  # omim_id

    def __str__(self):
        return "%s - %s" % (self.approved_symbol, self.approved_name)

    @property
    def omim_phenotypes(self):
        phenotypes = []
        for op in OmimPhenotype.objects.filter(omim_gene__mim_number=self.mim_number).distinct():
            phenotypes.append(op.phenotype)
        return phenotypes

    @property
    def omim_titles(self):
        titles = OmimTitle.objects.filter(omim_gene__mim_number=self.mim_number)
        if titles.exists():
            # there can be only one
            return str(titles[0])
        return ""

    @property
    def html_omim_titles(self):
        titles = OmimTitle.objects.filter(omim_gene__mim_number=self.mim_number)
        if titles.exists():
            # there can be only one
            return titles[0].html()
        return ""

    def str_html(self):
        return '<a href="https://omim.org/entry/%s" target="_blank">%s</a>' % (self.mim_number, self)

    class Meta:
        app_label = 'genetics'


class OmimGene(models.Model):
    mim_number = models.CharField(max_length=50, db_index=True)  # MIM Number
    gene_symbols = models.CharField(max_length=100, db_index=True)
    chromosome_location = models.CharField(max_length=50, db_index=True, null=True, blank=True)

    class Meta:
        app_label = 'genetics'


class OmimPhenotype(models.Model):
    omim_gene = models.ForeignKey(OmimGene, on_delete=models.CASCADE, related_name='phenotypes')
    phenotype = models.CharField(max_length=250)

    class Meta:
        app_label = 'genetics'


class OmimTitle(models.Model):
    prefix_map = {
        "NULL": '',
        "Number Sign": '# ',
        "Plus": '+ ',
        "Caret": '^ ',
        "Asterisk": '* ',
        "Percent": '% '
    }
    prefix = models.CharField(max_length=50, db_index=True, null=True, blank=True)
    omim_gene = models.ForeignKey(OmimGene, on_delete=models.CASCADE)
    preferred = models.TextField()
    alternative = models.TextField()

    @property
    def one_char_prefix(self):
        try:
            return OmimTitle.prefix_map[self.prefix]
        except:
            return ''

    def __str__(self):
        if self.alternative:
            return "%sPREF: %s ALT: %s" % (self.one_char_prefix, self.preferred, self.alternative)
        else:
            return "%s%s" % (self.one_char_prefix, self.preferred)

    def html(self):
        if self.alternative:
            return "<strong>%sPREF</strong>: %s <strong>ALT</strong>: %s" % (
                self.one_char_prefix, self.preferred, self.alternative)
        else:
            return "<strong>%s</strong>%s" % (self.one_char_prefix, self.preferred)

    class Meta:
        app_label = 'genetics'
