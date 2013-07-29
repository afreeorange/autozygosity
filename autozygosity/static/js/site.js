$(function () {

	// Gets a regex-compatible list of allowed extensions
	// Probably overkill
	allowed_extensions = ""
	$.get('/misc/allowed_upload_extensions', function(data) {
		allowed_extensions = data;
	});

	// Turns the token submission explanation message off
	// Again, probably overkill. Used jQuery forms for upload
	// progress. I wanted it to go to the submission target
	// (/token/{token}), but couldn't make this work. Hence
	// added window.location.href. Downside is that this is
	// a POST and GET in sequence, so using a session helper
	// wouldn't work.
	$('#no-token-explanation').click(function(){
		$.get('/misc/no_explanation');
		$('#token-explanation').slideUp();
	});

	// $.get('/misc/allowed_upload_extensions', function(data) {
	// 	allowed_extensions = data;
	// });

	// Custom token validator
	$.validator.addMethod("validtoken", function( value, element ) {
		var result = this.optional(element) || /^[a-z]{5,15}$/.test(value);
		return result;
	}, "Your token's between 5 and 15 characters.<br />It doesn't have any numbers or strange characters.");

	// Check file extension (doesn't mean it's a _valid_ VCF however...)
	$.validator.addMethod("vcfextension", function( value, element ) {
		var re = new RegExp("^.*.\.(" + allowed_extensions + ")$","i");
		var result = this.optional(element) || re.test(value);
		return result;
	}, "You need to upload a raw VCF file or any one of the supported compression formats. File extension is important.");

	// Validate token-check form before submission
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

	$("#vcfupload").validate({
		rules: {
			vcf: {
				required: true,
				vcfextension: true
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
				required: "You need to specify an input file"
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
		errorContainer: '#vcfupload-messages',
		errorLabelContainer: '#vcfupload-messages',
		errorElement: "span",
		wrapper: ""
	});

	// Upload progress bar
	var bar = $('.bar');
	var percent = $('.percent');
	var visual = $('#visual-progress');

	percent.html('0%');

	$('#vcfupload').ajaxForm({
		beforeSend: function() {
			var percentVal = '0%';
			bar.width(percentVal)
			percent.html(percentVal);

			visual.slideDown();
			$('.hide-after-submit').hide();
			$('#submit').attr('disabled', 'disabled');
			$('#token-submit').attr('disabled', 'disabled');
		},
		uploadProgress: function(event, position, total, percentComplete) {
			var percentVal = percentComplete + '%';
			bar.width(percentVal);
			percent.html(percentVal);
		},
		complete: function(xhr) {
			$('.hide-after-submit ').fadeOut();

			// Here, I make Flask return a header with the submission token. This is
			// because I couldn't figure out how to get the response URI (_not_ responseText)
			// from the XHR object. Nothing (not even getAllResponseHeaders()) worked.
			// Could be missing something. This will have to do for now.
			window.location.href = "/token/" + xhr.getResponseHeader('token');
		}
	});

	// Analysis tuning
	$('#tune-analysis').click(function(){
		$('#token-analysis-params').fadeToggle();
	});
	$('#min_variant_quality').slider({
		min: 0,
		max: 99,
		step: 1,
		value: 30,
		tooltip: "hide"
	}).on('slide', function(ev) {
		$('#min_variant_quality-value').html(ev.value);
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
		"aoColumns": [{"sType": "natural"}, {"sType": "formatted-num"}, {"sType": "formatted-num"}, null, null],
		"bFilter": false,
		"bPaginate": false,
		"bInfo": false,
	});

});