/*
* .replace('//', '/') serve per diverse configurazioni nel settings di force_script_name
* */
$('input[genetics=sequence_variant], input[genetics=sequence_variant_from_gene]').focusout(function () {
  if ($(this).val() && $(this).attr('genetics_mode')==='sequence_variant') {
    let notes = $(`p#${$(this).attr('id')}_notes`);
    let error = $(`div#${$(this).attr('id')}_error`);
    error.html('');
    notes.html('');
    $.ajax({
      url: `${force_script_name}/genetics/sequence_variant/`.replace('//', '/'),
      dataType: 'json',
      data: {
        sv: $(this).val(),
        id: $(this).attr('id')
      },
      success: function (data) {
        //AB026906.1:c.274del
        if (data.status==='Success') {
          let sequence_variant = $(`#${data.id}`);
          let protein_description = $(`${sequence_variant.attr('id_protein_description')}`);
          let type_effect = $(`${sequence_variant.attr('id_type_effect')}`);
          let chromosome_37 = $(`${sequence_variant.attr('id_chromosome_37')}`);
          let position_start_37 = $(`${sequence_variant.attr('id_position_start_37')}`);
          let position_end_37 = $(`${sequence_variant.attr('id_position_end_37')}`);
          let chromosome_38 = $(`${sequence_variant.attr('id_chromosome_38')}`);
          let position_start_38 = $(`${sequence_variant.attr('id_position_start_38')}`);
          let position_end_38 = $(`${sequence_variant.attr('id_position_end_38')}`);
          let chromosome = $(`${sequence_variant.attr('id_chromosome')}`);
          let position = $(`${sequence_variant.attr('id_position')}`);
          let ref = $(`${sequence_variant.attr('id_ref')}`);
          let ale = $(`${sequence_variant.attr('id_ale')}`);
          let notes = $(`p#${data.id}_notes`);
          let error = $(`div#${data.id}_error`);
          error.html('');
          notes.html('');
          let geneText = '';
          if (data.gene !== undefined) {
            geneText = ` <a href="https://omim.org/entry/${data.gene.mim_number}" target="_blank">More info on <strong>${data.gene.approved_symbol}</strong> Omim.org's page.</a>`;
          }
          let hgvsMutalyzer = '<a href="https://varnomen.hgvs.org/" target="_blank">HGVS</a>/<a href="https://mutalyzer.nl/" target="_blank">mutalyzer.nl</a>';
          if (data.notes || geneText) {
            let proteinDescription = '';
            let htmlProteinDescription = '';
            if (data.proteinDescriptions!==undefined && data.proteinDescriptions.length>0) {
              htmlProteinDescription = `<br><strong>Protein description</strong>${data.proteinDescriptions.length>1 ? 's: ' : ': '}`;
              let dash = '';
              data.proteinDescriptions.forEach(function (value, index, array) {
                proteinDescription += dash + value;
                dash = ' - ';
              });
              htmlProteinDescription += proteinDescription;
            }
            if (protein_description.length > 0) {
              protein_description.val(proteinDescription);
              htmlProteinDescription = '';
            }
            type_effect.val(data.type_effect)
            chromosome_37.val(data.chromosome_37)
            position_start_37.val(data.position_start_37)
            position_end_37.val(data.position_end_37)
            chromosome_38.val(data.chromosome_38)
            position_start_38.val(data.position_start_38)
            position_end_38.val(data.position_end_38)
            chromosome.val(data.chromosome)
            position.val(data.position)
            ref.val(data.ref)
            ale.val(data.ale)
            notes.html(`<span class="help-block"><strong>${hgvsMutalyzer}</strong>: ${data.notes} ${geneText} ${htmlProteinDescription}</span>`)
          }
          if (data.error) {
            error.html(`<span class="help-block"><strong>${hgvsMutalyzer}</strong>: ${data.error}</span>`)
          }
        } else {
            error.html(`<span class="help-block"><strong>HGVS/mutalyzer.nl: ${data.message}</strong></span>`);
        }
      }
    });
  }
});

$('input[genetics=sequence_variant_from_gene]').each(function( index ) {
  if ($(this).val() !== '') {
    $(this).attr('genetics_mode', 'sequence_variant');
  }
});


$('input[genetics=sequence_variant], input[genetics=sequence_variant_from_gene]').focusout();
$('input[genetics=gene]').keypress(function() {
  $('p#'+$(this).attr("id")+'_notes').html('');
});

$('input[genetics=gene]').autocomplete({
  source: `${force_script_name  }/genetics/gene/`.replace('//', '/'),
  select: function (event, ui) { //item selected
    AutoCompleteSelectHandlerGene(event, ui);
  },
  minLength: 3,
  sdelay: 300
});

$('input[genetics=sequence_variant_from_gene]').autocomplete({
  source: `${force_script_name}/genetics/gene/`.replace('//', '/'),
  focus: function (event, ui) {
    AutoCompleteFocusHandlerSQFromGene(event, ui);
    return false;
  },
  select: function (event, ui) { //item selected
    AutoCompleteSelectHandlerSQFromGene(event, ui);
    return false;
  },
  minLength: 3,
  sdelay: 300
});
/*
* https://stackoverflow.com/a/11416733/1029569 mi ha portato ad aggiungere _renderItem tramite un .each
* altrimenti (con la sintassi dell'esempio standard) funzionava solo sul primo
* */
$('input[genetics=gene]').each(function( index ) {
  $(this).autocomplete("instance")._renderItem = function (ul, item) {
    return $("<li>")
      .append("<div>" + item.label + (item.phenotypes !== undefined ? '<br>' + item.phenotypes : '') + (item.titles !== undefined ? '<br>' + item.titles : '') + "</div>")
      .appendTo(ul);
  };
});

$('input[genetics=sequence_variant_from_gene]').keyup(function() {
  if ($(this).val() === '') {
    $(this).autocomplete('enable');
    target.attr('genetics_mode', 'autocomplete');
  }
});

$('input[genetics=sequence_variant_from_gene]').each(function( index ) {
  $(this).autocomplete("instance")._renderItem = function (ul, item) {
    return $("<li>")
      .append("<div>" + item.label + (item.phenotypes !== undefined ? '<br>' + item.phenotypes : '') +
        (item.titles !== undefined ? '<br>' + item.titles : '')
        + "</div><ul genetics='transcripts' gene='" + item.approved_symbol + "'></ul>")
      .appendTo(ul);
  };
});


function AutoCompleteSelectHandlerGene(event, ui) {
  $(`#${ event.target.attributes['id'].value.slice(0, -13) }_id`).val(ui.item.id);
  let notes = $(`p#${event.target.attributes["id"].value.slice(0, -13)}_notes`);
  notes.html(`<span class="help-block"><a target="_blank" href="https://omim.org/entry/${ui.item.mim_number}">More info on Omim.org's page.</a></span>`);
}

function AutoCompleteSelectHandlerSQFromGene(event, ui) {
  return false;
}



function AutoCompleteFocusHandlerSQFromGene(event, ui) {
  let notes = $(`p#${event.target.attributes['id'].value}_notes`);
  let error = $(`div#${event.target.attributes['id'].value}_error`);
  notes.html(`<span class="help-block"><a target="_blank" href="https://omim.org/entry/${ui.item.mim_number}">${ui.item.approved_symbol} More info on Omim.org's page.</a></span>`);
  error.html('');
  let targetId = event.target.attributes['id'].value;
  let ul = $(`ul[genetics=transcripts][gene=${ui.item.approved_symbol}]`);
  if (ul.html() === '') {
    $.ajax({
      url: `${force_script_name}/genetics/transcripts/`.replace('//', '/'),
      dataType: 'json',
      data: {
        name: ui.item.approved_symbol
      },
      success: function (data) {
        if (data.status === 'Success') {
          let ul = $(`ul[genetics=transcripts][gene=${data.name}]`);
          transcripts = '';
          data.transcripts.forEach(function (value, index, array) {
            transcripts += `<li class="transcript" targetid="${ targetId }">${ value }</li>`;
          });
          ul.html(transcripts);
          $('li.transcript').click(function() {
            let self = $(this);
            let targetId = self.attr('targetid');
            let target = $(`input#${targetId}`);
            target.val(self.html());
            target.autocomplete('disable');
            target.attr('genetics_mode', 'sequence_variant');
            target.autocomplete('close');
          });
        } else {
          ul.html('<li>Error searching for transcripts.</li>');
        }
      }
    });
  }
}
