/* Blogging App related REST API endpoints */
$(document).ready(function(){
    var blogging = {
      /********************************************
       *  Generic and general methods             *
       *******************************************/
       utils : {
	      /**
	       * @brief Get Cookie of \<name\> from the DOM Cookie Object
	       */
	      getCookie : function(name){
	          var cookieValue = null;
	          if (document.cookie && document.cookie != ''){
	              var cookies = document.cookie.split(';');
	              for(var i=0; i < cookies.length; i++){
	                  var cookie = jQuery.trim(cookies[i]);
	                  if(cookie.substring(0, name.length+1) == (name + '=')){
	                      cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
	                      break;
	                  }
	              }
	          }
	          return cookieValue;
	      },/* end getCookie */
	      
	      /**
	       * @brief Test currently requested method if it is CSRF safe or not.
	       */
	      csrfSafeMethod : function(method){
	          return(/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
	      },/* end csrfSafeMethod */
	      
	      
	      handleAjaxError : function(xhRequest, ErrorText, thrownError){
	          //alert( "Sorry, there was a problem!" );
	          console.log( "Error: " + errorThrown );
	          console.log( "Status: " + status );
	          console.dir( xhr );
	      },
	      
	      handleAjaxComplete : function(xhr, status){
	        console.log("Request Completed with status: "+status);
	        
	      },
	      
	      /**
	       * @brief Perform AJAX Get request
	       * 
	       * Since most error handling and other operations are the same, just
	       * passing in the GET url and the method to invoke on success are passed.
	       * 
	       * @param url URL     to which GET request must be sent.
	       * @param onComplete  Method to be invoked on successful response.
	       * 
	       */
	      get : function(url, onComplete){
	           $.ajax({
	              url: url,
	              // the data to send (will be converted to a query string)
	              data: {format:'json'},
	              // whether this is a POST or GET request
	              type: "GET",
	              // the type of data we expect back
	              dataType : "json",
	              // code to run if the request succeeds;
	              // the response is passed to the function
	              success: onComplete,
	              // code to run if the request fails; the raw request and
	              // status codes are passed to the function
	              error: blogging.utils.handleAjaxError,
	              // code to run regardless of success or failure
	              complete: blogging.utils.handleAjaxComplete
	           });
	      },
	      
	      setupUser : function(data){
	        console.log(data);
	        if(!('id' in data)){
	            blogging.currentUser = blogging.guestUser;
	        }
	        else{
	            blogging.currentUser = {
	                            id:       data['id'],
	                            username: data['username'],
	                            gravatar: data['gravatar'],
	                            url:      "#",
	                          };
	        }
	      },
	      /**
	       * Get information about current user, if logged in. 
	       * Else, use Guest User credentials.
	       */
	      getCurrentUser : function(){
	          $.ajaxSetup({
	              beforeSend: function(xhr, settings) {
	                  if (!blogging.utils.csrfSafeMethod(settings.type) && !this.crossDomain) {
	                      xhr.setRequestHeader("X-CSRFToken", csrftoken);
	                  }
	              }
	          });
	          
	          blogging.utils.get("/rest/users/current/", blogging.utils.setupUser);
	      },/* function getCurrentUser ends */
	  },/* Namespace utils end */
      
      admin : {
        /********************************************
         *  Per Article Methods: Management Side    *
         *******************************************/
        /**
         * @brief Get form rendering information from the backend and render form
         * 
         * TODO
         */
        getForm :  function(entry_id){
        
        },
        
        /**
         * @brief Get contents of the object
         * TODO
         */
        getEntry : function(id){
            username = "dummy";
            filter_string = '?user='+username;
            get('/rest/content/manage/'+id+'/', blogging.admin.parseEntry);
        },
      
        /**
         * @brief Parse the content response from server
         * @param entry JSON Data returned by server for one entry.
         */
        parseEntry : function(entry){
          console.log(entry);
        },
      
        /**
         * @brief Save the form contents
         */
        saveEntry : function(){
          $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!blogging.utils.csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", blogging.csrftoken);
                }
            }
          });
          
          //Save Form Data
          $.ajax({
            cache: false,
            url : "/rest/content/manage/",
            type: "POST",
            dataType : "json",
            contentType: "application/json;",
            data : JSON.stringify(data),
            context : this,
            success : blogging.admin.parseEntry,
            error : utils.handleAjaxError
          }); 
        },
        /**
         * @brief Perform action on entry
         * 
         * This can be:
         * - Publish
         * - Unpublish
         * - Pin
         * - Unpin
         * - Delete
         * - Save
         */
         action : function(signal, multiple){
       
         },
         
        /********************************************
         *  Bulk Operations: Management Side        *
         *******************************************/
         getContent : function(){
           /* Has the user set the 'filter by User', 
            * 'filter drafts', 
            * 'filter published'? 
            */
           /* TODO */
           username='user'
           filter_string = '?user='+username;
           get('/rest/content/manage/', blogging.admin.parseContent);
         },
       
         /**
          * @brief Parse the content obtained from the server
          */
          parseContent : function(contentList){
            console.log(contentList);
            for(i=0; i< contentList.length; i++){
              console.log(contentList[i]);
            }
          },
       
      },/* Admin namespace end */
       
      open : {
        /********************************************
         *  Per Article Methods: Public Side        *
         *  Can't use 'public'                      *
         *******************************************/
        /**
         * @brief Get contents of the object
         * TODO
         */
        getEntry : function(id){
           filter_string = '?user='+username;
           utils.get('/rest/content/'+id+'/', blogging.open.parseEntry);
        },
      
        /**
         * @brief Parse the content response from server 
         */
        parseEntry : function(entry){
          console.log(entry);
        },
        
        /********************************************
         *  Bulk Operations: Public                  *
         ********************************************/
        /**
         * @brief Get published content in JSON format
         */
         getContent : function(){
           /* Has the user set the 'filter by User' ? */
           /* TODO */
           username='user'
           filter_string = '?user='+username;
           utils.get('/rest/content/', blogging.open.parseContent);
         },
       
         /**
          * @brief Parse the content obtained from the server
          */
          parseContent : function(contentList){
            console.log(contentList);
            for(i=0; i< contentList.length; i++){
              console.log(contentList[i]);
            }
          }
      },/* Public namespace end*/
       
      /********************************************
       *  Usage                                   *
       ********************************************/
       csrftoken : null,
       guestUser : {
                      id: "0",
                      username: "Guest",
                      gravatar: "images/male.png",
                      url: "#",
                  },
       currentUser : null,
    };/* end blogging namespace object*/
    
    blogging.csrftoken = blogging.utils.getCookie('csrftoken');
    blogging.currentUser = blogging.guestUser;
    blogging.utils.getCurrentUser();
});