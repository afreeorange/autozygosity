$(function () {

	/* Can consolidate a lot but readability is paramount, and space (and bandwidth) are cheap. */

	// Custom token validator
	$.validator.addMethod("validtoken", function( value, element ) {
		var result = this.optional(element) || /^[a-z]{5,15}$/.test(value);
		return result;
	}, "Your token's between 5 and 15 characters.<br />It doesn't have any numbers or strange characters.");

	// Check file extension (doesn't mean it's a _valid_ VCF however...)
	$.validator.addMethod("vcfextension", function( value, element ) {
		var result = this.optional(element) || /^.*.\.vcf$/i.test(value);
		return result;
	}, "You need to upload a VCF file. It should end in '.vcf'");

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
			}
		},
		messages: {
			vcf: {
				required: "You need to specify an input file"
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

});