/* autocomplete.js
**
** This provides some custom on autocompletes.
** It excludes items already added to the autocomplete
** from being included in the autocomplete results.
** Right now, this is only applied to the request picker
** on the project page editor.
*/

import $ from 'jquery';

let projectRequestAutocomplete = $('.project.form #id_requests-autocomplete');

function getDeckElements(autocompleteInput) {
    var elementIds = [];
    $(autocompleteInput).siblings('.deck').children().map((i, item) => {
        elementIds.push($(item).data('value'));
    });
    return elementIds;
}

$(projectRequestAutocomplete).change(function() {
    $(this).yourlabsAutocomplete().data = {
        exclude: getDeckElements(this)
    };
});

$('.select2').on('select2:unselect', function() {
  console.log("here");
	var $el = $(this);
  console.log($el);
	setTimeout(function() {
		$('.select2-search__field', $el.closest('.form-group'))
			.val('');
	}, 0);
});
