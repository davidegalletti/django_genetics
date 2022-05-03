#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django import forms


class SequenceVariantInput(forms.Widget):
    template_name = 'genetics/widgets/sequence_variant.html'

    def __init__(self, attrs=None):
        super(SequenceVariantInput, self).__init__(attrs)


class SequenceVariantFromGeneInput(forms.Widget):
    template_name = 'genetics/widgets/sequence_variant_from_gene.html'

    def __init__(self, attrs=None):
        super(SequenceVariantFromGeneInput, self).__init__(attrs)


class GeneInput(forms.Widget):
    template_name = 'genetics/widgets/gene.html'

    def __init__(self, attrs=None):
        super(GeneInput, self).__init__(attrs)

    def render(self, name, value, attrs=None, renderer=None):
        """
        Returns this Widget rendered as HTML, as a Unicode string.
        """
        context = self.get_context(name, value, attrs)
        if value is not None:
            from genetics.models import HgncGene
            try:
                context['gene'] = HgncGene.objects.get(pk=value)
            except:
                pass
        return self._render(self.template_name, context, renderer)

