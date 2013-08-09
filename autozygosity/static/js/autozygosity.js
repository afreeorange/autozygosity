// Keep users from fiddling with tabs or buttons on form submit
function disable_interaction() {
	$('button').each(function() {
		$(this).hide();
	});
	$('#navigation > li > a').each(function() {
		$(this).removeAttr('data-toggle');
	});
}

$(function () {

	// Because location.origin seems to be Webkit-only
	if (!window.location.origin) {
		window.location.origin = window.location.protocol+"//"+window.location.host;
	};

	// Show any older tokens if possible and available
	if ($.jStorage.storageAvailable()) {

		older_tokens = $.jStorage.get('older_tokens', []);

		if (older_tokens.length >= 2) {
			$('#older-tokens').show();
			$('#older-tokens').text('A few older tokens: ');
			for (var i = 0; i < older_tokens.length - 1; i++) {
				$('#older-tokens').append(' <a href="' + autozygosity.app_root + "/token/" + older_tokens[i] + '">' + older_tokens[i] + '</a>');
			};
		};
	};

	// Turns the token submission explanation message off.
	// Again, probably overkill. Used jQuery forms for upload
	// progress. I wanted it to go to the submission target
	// (/token/{token}), but couldn't make this work. Hence
	// added window.location.href. Downside is that this is
	// a POST and GET in sequence, so using a session helper
	// wouldn't work.
	$('#no-token-explanation').click(function(){
		$.get(autozygosity.app_root + '/misc/no_explanation');
		$('#token-explanation').slideUp();
	});

	// Custom token validator
	$.validator.addMethod("validtoken", function( value, element ) {
		var result = this.optional(element) || /^[a-z]{5,15}$/.test(value);
		return result;
	}, "Your token's between 5 and 15 characters.<br />It doesn't have any numbers or strange characters.");

	// Check file extension (doesn't mean it's a _valid_ VCF however...)
	$.validator.addMethod("validextensions", function( value, element ) {
		var re = new RegExp("^.*.\.(" + autozygosity.allowed_extensions + ")$","i");
		var result = this.optional(element) || re.test(value);
		return result;
	}, "You need to upload a raw VCF file or any one of the supported compression formats. File extension is important.");

	// Validate token-check form
	$("#tokencheck").validate({
		rules: {
			token: {
				required: true,
				validtoken: true
			}
		},
		messages: {
			token: {
				required: "You need to give me a token"
			}
		},
		errorContainer: '#tokencheck-messages',
		errorLabelContainer: '#tokencheck-messages',
		errorElement: "span",
		wrapper: ""
	});

	var valid_uri = false;

	// Validate VCF upload form
	$("#vcfupload").validate({
		rules: {
			vcf: {
				required: function() {
					return $('#uri').val() == '';
				},
				validextensions: true
			},
			uri: {
				required: function() {
					return $('#vcf').val() == '';
				},
				url: true
			},
			min_variant_quality: {
				required: true,
				min: 0,
				digits: true
			},
			min_quality_depth: {
				required: true,
				min: 0,
				digits: true
			},
			homozyg_window_size: {
				required: true,
				min: 0,
				digits: true
			},
			heterozyg_calls: {
				required: true,
				min: 0,
				digits: true
			}
		},
		messages: {
			vcf: {
				validextensions: "You need to specify a VCF or compressed file for upload"
			},
			uri: {
				url: "You need to specify a valid URI"
			},
			min_variant_quality: {
				required: "You need to specify minimum variant quality",
				digits: "All values need to be integers"
			},
			min_quality_depth: {
				required: "You need to specify proper quality depth",
				digits: "All values need to be integers"
			},
			homozyg_window_size: {
				required: "You need to specify proper homozygosity window size",
				digits: "All values need to be integers"
			},
			heterozyg_calls: {
				required: "You need to specify proper number of heterozygous calls allowed in window",
				digits: "All values need to be integers"
			}
		},
		errorPlacement: function($error, $element) {
			var name = $element.attr("name");
			$("#" + name + "-error-messages").append($error);
		},
		errorElement: "span",
		wrapper: "",
		success: function() {
			$('.label-error').hide();
			valid_uri = true;
		}
	});

	// Show the download message only when (a) URI is valid, (b) submission happens
	$('#uri-submit').click(function() {
		if (valid_uri) {
			disable_interaction();
			$('#uri-example > span').show();
		};
	});


	// Upload progress bar
	var bar = $('.bar');
	var percent = $('.percent');
	var visual = $('#visual-progress');

	percent.html('0%');

	// Trigger an Ajax submit only when the upload portion is submitted.
	$('#submit').click(function(){
		$('#vcfupload').ajaxForm({
			beforeSend: function() {
				var percentVal = '0%';
				bar.width(percentVal)
				percent.html(percentVal);

				visual.slideDown();
				$('.hide-after-submit').hide();
				// Keep users from fiddling with tabs or buttons on form submit
				disable_interaction();
			},
			uploadProgress: function(event, position, total, percentComplete) {
				var percentVal = percentComplete + '%';
				bar.width(percentVal);
				percent.html(percentVal);
			},
			complete: function(xhr) {
				$('.hide-after-submit ').fadeOut();

				// Anything other than 200 (including a 404) and barf...
				if (xhr.status != 200) {
					window.location.href = autozygosity.app_root + "/misc/oops";
					return true;
				};

				// Here, I make Flask return a header with the submission token. This is
				// because I couldn't figure out how to get the response URI (_not_ responseText)
				// from the XHR object. Nothing (not even getAllResponseHeaders()) worked.
				// Could be missing something. This will have to do for now.
				window.location.href = autozygosity.app_root + "/token/" + xhr.getResponseHeader('token');
			}
		});
	});

	// Analysis tuning
	$('#min_variant_quality').slider({
		min: 0,
		max: 99,
		step: 1,
		value: 30,
		tooltip: "hide"
	}).on('slide', function(ev) {
		$('#min_variant_quality-value').html(ev.value);
	});


	// Sample URI for URI form
	$('#uri-sample-data').click(function() {
		$('#uri').val(window.location.origin + autozygosity.app_root + '/static/sample.vcf');
	});

	/*
	 * Natural Sort algorithm for Javascript - Version 0.7 - Released under MIT license
	 * Author: Jim Palmer (based on chunking idea from Dave Koelle)
	 * Contributors: Mike Grier (mgrier.com), Clint Priest, Kyle Adams, guillermo
	 * See: http://js-naturalsort.googlecode.com/svn/trunk/naturalSort.js
	 */
	function naturalSort (a, b) {
		var re = /(^-?[0-9]+(\.?[0-9]*)[df]?e?[0-9]?$|^0x[0-9a-f]+$|[0-9]+)/gi,
			sre = /(^[ ]*|[ ]*$)/g,
			dre = /(^([\w ]+,?[\w ]+)?[\w ]+,?[\w ]+\d+:\d+(:\d+)?[\w ]?|^\d{1,4}[\/\-]\d{1,4}[\/\-]\d{1,4}|^\w+, \w+ \d+, \d{4})/,
			hre = /^0x[0-9a-f]+$/i,
			ore = /^0/,
			// convert all to strings and trim()
			x = a.toString().replace(sre, '') || '',
			y = b.toString().replace(sre, '') || '',
			// chunk/tokenize
			xN = x.replace(re, '\0$1\0').replace(/\0$/,'').replace(/^\0/,'').split('\0'),
			yN = y.replace(re, '\0$1\0').replace(/\0$/,'').replace(/^\0/,'').split('\0'),
			// numeric, hex or date detection
			xD = parseInt(x.match(hre)) || (xN.length != 1 && x.match(dre) && Date.parse(x)),
			yD = parseInt(y.match(hre)) || xD && y.match(dre) && Date.parse(y) || null;
		// first try and sort Hex codes or Dates
		if (yD)
			if ( xD < yD ) return -1;
			else if ( xD > yD )  return 1;
		// natural sorting through split numeric strings and default strings
		for(var cLoc=0, numS=Math.max(xN.length, yN.length); cLoc < numS; cLoc++) {
			// find floats not starting with '0', string or 0 if not defined (Clint Priest)
			var oFxNcL = !(xN[cLoc] || '').match(ore) && parseFloat(xN[cLoc]) || xN[cLoc] || 0;
			var oFyNcL = !(yN[cLoc] || '').match(ore) && parseFloat(yN[cLoc]) || yN[cLoc] || 0;
			// handle numeric vs string comparison - number < string - (Kyle Adams)
			if (isNaN(oFxNcL) !== isNaN(oFyNcL)) return (isNaN(oFxNcL)) ? 1 : -1;
			// rely on string comparison if different types - i.e. '02' < 2 != '02' < '2'
			else if (typeof oFxNcL !== typeof oFyNcL) {
				oFxNcL += '';
				oFyNcL += '';
			}
			if (oFxNcL < oFyNcL) return -1;
			if (oFxNcL > oFyNcL) return 1;
		}
		return 0;
	}
	 
	// JQuery Datatables plugin for natual sorting
	jQuery.extend( jQuery.fn.dataTableExt.oSort, {
		"natural-asc": function ( a, b ) {
			return naturalSort(a,b);
		},
		"natural-desc": function ( a, b ) {
			return naturalSort(a,b) * -1;
		}
	} );

	// JQuery Datatables plugin to sort formatted numbers
	jQuery.extend( jQuery.fn.dataTableExt.oSort, {
		"formatted-num-pre": function ( a ) {
			a = (a === "-" || a === "") ? 0 : a.replace( /[^\d\-\.]/g, "" );
			return parseFloat( a );
		},
		"formatted-num-asc": function ( a, b ) {
			return a - b;
		},
		"formatted-num-desc": function ( a, b ) {
			return b - a;
		}
	} );

	// Apply JQuery.Datatables magic to BED file results
	$('#bed-table').dataTable({
		"aoColumns": [{"sType": "natural"}, {"sType": "formatted-num"}, {"sType": "formatted-num"}, {"sType": "formatted-num"}, {"sType": "formatted-num"}],
		"bFilter": false,
		"bPaginate": false,
		"bInfo": false,
	});

});