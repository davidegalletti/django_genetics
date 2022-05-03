import json

from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from genetics.utils import ApiInvoker
from genetics.models import OmimGene
from genetics.models import HgncGene


def gene(request):
    data = 'fail'
    try:
        if request.is_ajax():
            q = request.GET.get('term', '')
            # limito a 25 il n. di record per evitare eccessivi rallentamenti per ricerca
            genes = list(HgncGene.objects.filter(Q(approved_symbol__icontains=q) | Q(alias_symbols__icontains=q) |
                                                 Q(approved_name__icontains=q) | Q(alias_names__icontains=q) )[:25])
            # per lo stesso motivo effettuo la ricerca solo se ci sono almeno 4 caratteri
            mims = []
            if len(q) >= 4:
                mims = [og.mim_number for og in OmimGene.objects.filter(phenotypes__phenotype__icontains=q)[:25]]
            other_genes = []
            if len(mims) > 0:
                other_genes = list(HgncGene.objects.filter(mim_number__in=mims))
            all_genes = list(set(genes + other_genes))
            results = []
            for g in all_genes:
                phenotypes = " || ".join(g.omim_phenotypes)
                symbol = g.approved_symbol
                if g.alias_symbols:
                    symbol += " (%s)" % g.alias_symbols
                genes_json = {
                    'id': g.id,
                    'label': "%s - %s" % (symbol, g.approved_name),
                    'approved_symbol': g.approved_symbol,
                    'chromosome_location': g.chromosome_location,
                    'phenotypes': phenotypes,
                    'titles': g.html_omim_titles,
                    'value': "%s - %s" % (g.approved_symbol, g.approved_name),
                    'mim_number': g.mim_number
                }
                if g.mim_number:
                    pass
                    # I seek extra info on OMIM
                results.append(genes_json)
            data = json.dumps(results)
    except:
        pass
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


def transcripts(request):
    data = {
        'transcripts': [],
        'error': "",
        'status': ApiInvoker.FAILURE
    }
    try:
        if request.is_ajax():
            mutalyzer_cs_endpoint = "https://mutalyzer.nl/json/getTranscriptsByGeneName"
            url = mutalyzer_cs_endpoint + ("?build=hg38&name=%s" % request.GET['name'])
            aics = ApiInvoker(url=url)
            # https://mutalyzer.nl/json/getTranscriptsByGeneName?build=hg19&name=MAP7D2
            """
                [
                    "NM_001168465.1",
                    "NM_001168466.1",
                    "NM_001168467.1",
                    "NM_152780.2",
                    "NM_152780.3",
                    "XM_005274478.1",
                    "XM_005274479.1",
                    "XM_005274480.1",
                    "XM_005274481.1"
                ]
            """
            data['transcripts'] = aics.decoded
            if aics.exception:
                data['exception'] = aics.exception
            data['status'] = ApiInvoker.SUCCESS
        else:
            data['error'] = "Generic error."
    except:
        pass
    data['name'] = request.GET['name']
    return JsonResponse(data)


def sequence_variant(request):
    data = {
        'notes': "",
        'error': "",
        'status': ApiInvoker.FAILURE
    }
    try:
        if request.is_ajax():
            mutalyzer_cs_endpoint = "https://mutalyzer.nl/json/checkSyntax"
            url = mutalyzer_cs_endpoint + ("?variant=%s" % request.GET['sv'])
            aics = ApiInvoker(url=url)
            # https://mutalyzer.nl/json/checkSyntax?variant=AB026906.1:c.274de
            """
                {
                  "valid": false,
                  "messages": [
                    {
                      "errorcode": "EPARSE",
                      "message": "Expected \">\" (at char 17), (line:1, col:18)"
                    }
                  ]
                }
            """
            if aics.decoded["valid"]:
                data['notes'] = 'Valid syntax. '
                # se è valido sintatticamente faccio una verifica semantica
                mutalyzer_ml_endpoint = "https://mutalyzer.nl/json/runMutalyzerLight"
                url = mutalyzer_ml_endpoint + ("?variant=%s" % request.GET['sv'])
                aiml = ApiInvoker(url=url)
                if aiml.decoded['errors'] == 0:
                    try:
                        data['proteinDescriptions'] = [pd[1+pd.find(':'):] for pd in aiml.decoded['proteinDescriptions']]
                    except:
                        data['proteinDescriptions'] = []
                    if aiml.decoded['warnings'] == 0:
                        # data['notes'] += aiml.decoded['summary']
                        pass # il summary è poco informativo
                    else:
                        data['error'] += "Warnings(s): " + " -- ".join([m['message'] for m in aiml.decoded['messages']])
                    mutalyzer_gn_endpoint = "https://mutalyzer.nl/json/getGeneName" #NM_001168465.1
                    '''
                        https://mutalyzer.nl/json/getGeneName?build=hg19&accno=NM_000052.6  ==> {"faultcode": "ENOTFOUND", "faultstring": "Transcript NM_000052.6 not found for build hg19."}
                        https://mutalyzer.nl/json/getGeneName?build=hg19&accno=NM_000052.5  ==> "ATP7A"
                        https://mutalyzer.nl/json/getGeneName?build=hg38&accno=NM_000052.6  ==> "ATP7A"
                        USIAMO LA 38 CHIEDERE CONFERMA A DAVIDE MEI
                    '''
                    url = mutalyzer_gn_endpoint + ("?build=hg38&accno=%s" % aiml.decoded['referenceId'])
                    aign = ApiInvoker(url=url)
                    if aign.decoded:
                        try:
                            gene = HgncGene.objects.get(approved_symbol=aign.decoded)
                            data['gene'] = {
                                'approved_symbol': gene.approved_symbol,
                                'mim_number': gene.mim_number
                            }
                        except:
                            pass
                    # API VEP
                    vep_37_endpoint = "https://grch37.rest.ensembl.org/vep/human/hgvs/"  # NM_001168465.1
                    vep_38_endpoint = "https://rest.ensembl.org/vep/human/hgvs/"  # NM_001168465.1
                    url_37 = vep_37_endpoint + ("%s?content-type=application/json" % request.GET['sv'])
                    url_38 = vep_38_endpoint + ("%s?content-type=application/json" % request.GET['sv'])
                    aivep37 = ApiInvoker(url=url_37)
                    aivep38 = ApiInvoker(url=url_38)
                    type_effect = ''
                    ref = ''
                    ale = ''
                    chromosome_38 = ''
                    position_start_38 = ''
                    position_end_38 = ''
                    chromosome_37 = ''
                    position_start_37 = ''
                    position_end_37 = ''
                    if aivep38.decoded:
                        try:
                            try:
                                type_effect = aivep38.decoded[0]['most_severe_consequence']
                            except:
                                pass
                            try:
                                # "allele_string" quello che è a sinistra dello "/" è ref
                                # "allele_string" quello che è a destra dello "/" è ale
                                allele_string = aivep38.decoded[0]['allele_string']
                                allele_split = allele_string.split('/')
                                ref = allele_split[0]
                                ale = allele_split[1]
                            except:
                                pass
                            try:
                                chromosome_38 = aivep38.decoded[0]['seq_region_name']
                                position_start_38 = aivep38.decoded[0]['start']
                                position_end_38 = aivep38.decoded[0]['end']
                            except:
                                pass
                        except:
                            pass
                    if aivep37.decoded:
                        try:
                            try:
                                chromosome_37 = aivep37.decoded[0]['seq_region_name']
                                position_start_37 = aivep37.decoded[0]['start']
                                position_end_37 = aivep37.decoded[0]['end']
                            except:
                                pass
                        except:
                            pass
                    data['type_effect'] = type_effect
                    data['ref'] = ref
                    data['ale'] = ale
                    data['chromosome_38'] = chromosome_38
                    data['position_start_38'] = position_start_38
                    data['position_end_38'] = position_end_38
                    data['chromosome_37'] = chromosome_37
                    data['position_start_37'] = position_start_37
                    data['position_end_37'] = position_end_37
                else:
                    data['error'] += "Error(s): " + " -- ".join([m['message'] for m in aiml.decoded['messages']])
            else:
                if aics.decoded["messages"][0]['errorcode'] == 'EPARSE':
                    data = aics.decoded
                    data['error'] = " -- ".join([m['message'] for m in aics.decoded['messages']])
                    data['notes'] = ''
                else:
                    try:
                        data['notes'] = " -- ".join([m['message'] for m in aics.decoded['messages']])
                    except:
                        pass
            data['status'] = ApiInvoker.SUCCESS
        else:
            data['error'] = "Generic error."
    except:
        pass
    data['id'] = request.GET['id']
    return JsonResponse(data)
