/**
 * To Manage articles and Bookamrks
 */
$(document).ready(function(){

	var data_attributes = {};

	/**
	 * Iska hum kuchh nahi kar sakte !!
	 */ 	
	var getCookie = function(name){
	    var cookieValue = null;
	    if (document.cookie && document.cookie != '') {
	        var cookies = document.cookie.split(';');
	        for (var i = 0; i < cookies.length; i++) {
	            var cookie = jQuery.trim(cookies[i]);
	            // Does this cookie string begin with the name we want?
	            if (cookie.substring(0, name.length + 1) == (name + '=')) {
	                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
	                break;
	            }
	        }
	    }
	    return cookieValue;
	};
	
	var csrfSafeMethod = function(method) {
	    // these HTTP methods do not require CSRF protection
	    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
	};


	/**
	 * Parse the response
	 */
	var renderResponse = function(data){
		console.log("renderResponses: In, "+data.result);
		var text = data.return_text.split('\n');
		var arrayLength = text.length;
		var status_text = "";
		for (var i = 0; i < arrayLength; i++) {
			console.log(text[i]);
			status_text += "<sapn>" + text[i] + "</span><br />";
		}

		if (data.result == 'success') {
			$('#id-status-text').html(status_text);
			$('#id-status-icon').text('done_all');
			$('#id-div-status').removeClass('status-failure');
			$('#id-div-status').addClass('status-success');
			$('#id-div-status').removeClass('hidden');
			$('#id-div-loading').addClass('hidden');

			if (data.action == 'Delete')			
			{
				 location.reload();
			}
			else if (data.action == 'Publish') {
				/* Change the icons of published icons */
				console.log(data.published_id)
				for (var i = 0; i < data.published_id.length; i++) {
					console.log(data.published_id[i]);
					console.log($(".post-status").find('[data-id="' + data.published_id[i] + '"]').text());
					$(".post-status").find('[data-id="' + data.published_id[i] + '"]').text('check');
				}
			}
			else if (data.action == 'Unpublish') {
				/* Change the icons of published icons */
				console.log(data.published_id)
				for (var i = 0; i < data.published_id.length; i++) {
					console.log(data.published_id[i]);
					console.log($(".post-status").find('[data-id="' + data.published_id[i] + '"]').text());
					$(".post-status").find('[data-id="' + data.published_id[i] + '"]').children("i").text('close');
				}
			}

						
		} else if (data.result == 'failure') {
			console.log("failed");
			$('#id-status-text').html(status_text);
			$('#id-status-icon').text('error_outline');
			$('#id-div-status').addClass('status-failure');
			$('#id-div-status').removeClass('status-success');
			$('#id-div-status').removeClass('hidden');
			$('#id-div-loading').addClass('hidden');

		} else {
			console.log("unexpected error!");
			$('#id-status-text').text('Unexpected error occurred!');
			$('#id-status-icon').text('error_outline');
			$('#id-div-status').addClass('status-failure');
			$('#id-div-status').removeClass('status-success');
			$('#id-div-status').removeClass('hidden');
			$('#id-div-loading').addClass('hidden');
		}
	}

	/**
	 * Send request
	 */
	var sendRequest = function(){
		console.log("sendRequest: In");	
		
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        }
    });		
    
		$.ajax({
				    
		    url: data_attributes.url,
		    data: {
		        format:'json'
		    },
		    type: "POST",		 
		    // the type of data we expect back
		    dataType: "json",
		 
		    // code to run if the request succeeds;
		    // the response is passed to the function
		    success: renderResponse,
		 
		    // code to run if the request fails; the raw request and
		    // status codes are passed to the function
		    error: function( xhr, status, errorThrown ) {
		        //alert( "Sorry, there was a problem!" );
		        console.log( "Error: " + errorThrown );
		        console.log( "Status: " + status );
		        console.dir( xhr );
		    },
		 
		    // code to run regardless of success or failure
		    complete: function( xhr, status ) {
		        //alert( "The request is complete!" );
		    }
		});
	};

	/**
	 * Page Click Actions
	 */
	var pageClickAct = function(){				
		console.log("pageClickAct: In");	
					
		data_attributes.url = window.location.origin + $('#id-action-btn').data('url');
		var arg1 = 'ids='
		var count = 0;
		$('#id-tbody').find('tr.is-selected').each(function() {
  		arg1 += $(this).data('id') + ','
  		count++;
		});				
		if (count == 0) {
			$('#id-status-text').text('Select at least one entry.');
			$('#id-div-status').addClass('status-failure');
			$('#id-div-status').removeClass('status-success');
			$('#id-div-status').removeClass('hidden');
			return false;			
		}
		var arg2 = 'action=';
		var selected = $('#id_action').val();
		if (selected == null) {
			$('#id-status-text').text('select one action for selected entries.');
			$('#id-div-status').addClass('status-failure');
			$('#id-div-status').removeClass('status-success');
			$('#id-div-status').removeClass('hidden');
			return false;				
		}
		arg2 += selected;
		data_attributes.url += '?' + arg1 + '&' + arg2				
		
		$('#id-div-action').addClass('hidden');
		$('#id-status-text').text('Waiting for the server response. Please wait...');
		$('#id-div-status').removeClass('hidden');
		$('#id-div-loading').removeClass('hidden');

		sendRequest();
	};	
	
	$('#id-action-btn').unbind().on('click', pageClickAct);

});
