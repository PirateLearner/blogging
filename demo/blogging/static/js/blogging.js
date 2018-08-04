var blogging = blogging || {};
/* Blogging App related REST API endpoints */
$(document).ready(function(){
    if(!blogging.hasOwnProperty('utils')){
        blogging.utils = {};
    }
    if(!blogging.hasOwnProperty('admin')){
        blogging.admin = {};
    }
    if(!blogging.hasOwnProperty('open')){
        blogging.open = {};
    }
    
    /********************************************
     *  Generic and general methods             *
     *******************************************/
     blogging.utils = {
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
          console.log( "Error: " + thrownError );
          console.log( "Status: " + ErrorText );
          console.dir( xhRequest );
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
      get : function(url, onComplete, datatype="json"){
          requestParams = {
              url: url,
              // the data to send (will be converted to a query string)
              data: {format:'json'},
              // whether this is a POST or GET request
              type: "GET",
              // the type of data we expect back
              dataType : datatype,
              // code to run if the request succeeds;
              // the response is passed to the function
              success: onComplete,
              // code to run if the request fails; the raw request and
              // status codes are passed to the function
              error: blogging.utils.handleAjaxError,
              // code to run regardless of success or failure
              complete: blogging.utils.handleAjaxComplete
           };
           if(datatype=='html'){
               requestParams.accept = {text:'html'};
           }
           $.ajax(requestParams);
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
      
      getCurrentDateTime: function(){
          var date = new Date();
          return date.toISOString();
      },
  };/* Namespace utils end */
  
  blogging.admin = {
        /********************************************
         *  Per Article Methods: Management Side    *
         *******************************************/
         requestedTemplate: null,
        /*
         * @brief Fetch the initial form
         */
        fetchInitialForm : function(entry=0){
          url = '/rest/content/template/get_form.html/';
          if(entry!=0){
            url = url+'?entry=' + entry;
          }
          blogging.utils.get(url,
                             blogging.admin.renderForm,
                             'html')
        },
        /**
         * @brief Get form rendering information from the backend and render form
         * 
         */
        getForm :  function(){
          template = $('select[name="template"] option:selected').text();
          url = '/rest/content/template/get_form.html/';
          console.log($('select[name="template"] option:selected'));
          if(! ($('select[name="template"] option:selected').val() === '')){
            url = url+'?template=' + template;
            blogging.admin.requestedTemplate = template;
          }
          else{
              blogging.admin.requestedTemplate = null;
          }
          blogging.utils.get(url,
                             blogging.admin.renderForm,
                             'html')
        },
        
        /**
         * @brief Parse the content response from server
         * @param entry JSON Data returned by server for one entry.
         */
        renderForm : function(entry){
          form = $(entry);
          console.log(entry);

          /* Get any data previously filled in the previous form */
          prev_form = $('#content_form');
          prev_ordering = $('#fieldOrder').text().split(',');
          /* Remove cruft from received data */
          ordering = form.filter('span[id="fieldOrder"]').text().trim().split(',');
          form.find('fieldset').remove();
          form.find('select[name="author"]').parent().remove();
          
          if(!prev_form.length){
              /* Form doesn't exist. Render it now */
              overlay = $('<div class="overlay" id="overlay">'+
                           '<div><span>Close Btn</span></div>'+
                           '<div id="overlay_inner"></div>'+
                        '</div>');
              $('body').append(overlay);
              $('#overlay_inner').prepend(form.filter('span[id="fieldOrder"]'));
              $('#overlay_inner').append(blogging.admin.formatForm(form, ordering));
          }else{
              $('body').off('click', 'button[id="id_save_form"]', 'Save', blogging.admin.prepareSend);
              $('body').off('click', 'button[id="id_publish_form"]', 'Publish', blogging.admin.prepareSend);
              $('body').off('click', 'button[id="id_delete_form"]','Delete', blogging.admin.prepareSend);
              prev_form.remove();
              
              $('#overlay_inner').find('span[id="fieldOrder"]').remove();
              $('#overlay_inner').prepend(form.filter('span[id="fieldOrder"]'));
              $('#overlay_inner').append(blogging.admin.formatForm(form, ordering));
              /* Swap out the old form fields with the new one */
              blogging.admin.migrateData(prev_form, prev_ordering, $('#content_form'),form.filter('span[id="fieldOrder"]').text().trim().split(','));
          }

          
          /* If possible, place data in new fields by evaluating their type. */
          $('select[name="template"]').on('change', blogging.admin.getForm);
          console.log($('button[id="id_save_form"]'));
          $('body').on('click', 'button[id="id_save_form"]', 'Save', blogging.admin.prepareSend);
          $('body').on('click', 'button[id="id_publish_form"]', 'Publish', blogging.admin.prepareSend);
          $('body').on('click', 'button[id="id_delete_form"]','Delete', blogging.admin.prepareSend);
        },
        
        /**
         * @brief Prepare data to send request to server and dispatch request
         */
        prepareSend: function(event){
            event.preventDefault();
            publish = false;
            
            if(event.data === 'Delete'){
                console.log('Delete '+blogging.open.getPostId());
                //blogging.admin.deleteEntry(blogging.open.getPostId());
            }else {
                //Get all data
                form = $('#content_form');
                ordering = $('#fieldOrder').text().trim().split(',');
                data = {};
                if(blogging.open.getPostId() != 0){
                    data.id = blogging.open.getPostId();
                }
                
                for (var ii=0; ii< ordering.length; ii++){
                    console.log(ordering[ii]);
                    field = form.find('[name="'+ordering[ii]+'"]');
                    tag = field.prop('tagName').toLowerCase();
                    console.log(field);
                    console.log(tag);
                    switch(tag){
                        case 'input':
                            console.log('input');
                            data[ordering[ii]] = field.val();
                            break;
                        case 'textarea':
                            console.log('textarea');
                            data[ordering[ii]] = field.val();
                            break;
                        case 'select':
                            console.log('select');
                            data[ordering[ii]] = field.find('option:selected').val();
                            break;
                        default:
                            console.log('Unknown type');
                            return false;
                    }
                }
                if (event.data === 'Save'){
                    console.log('Save '+blogging.open.getPostId());
                }else if(event.data === 'Publish'){
                    console.log('Publish '+blogging.open.getPostId());
                    publish = true;
                    data['policy'] = [{
                                        'entry': blogging.open.getPostId(),
                                        'policy':"PUB",
                                        'start': blogging.utils.getCurrentDateTime()
                                       }];
                }else {
                console.log('Unknown option');
                }
                console.log(JSON.stringify(data));
                blogging.admin.saveEntry(data);
            }
            
            return false;
        },
        
        formatForm: function(form, ordering){
            /* 
             * Create a new form body
             */
            formBody = $('<form class="form" id="content_form"></form>');
            for (var ii=0; ii< ordering.length; ii++){
                formBody.append(form.find('[name='+ordering[ii]+']').parent());
            }
            /*
             * Add empty selection to template selection
             */
            if(blogging.open.getPostId()==0){
                /* New content. */
                if(blogging.admin.requestedTemplate != null){
                    formBody.find('select[name="template"] option').filter(function () { return $(this).html() == blogging.admin.requestedTemplate; }).prop('selected', true);
                    blogging.admin.requestedTemplate = null;
                }
            }else{
               /* 
                * Old Content Edit form
                */
               if(blogging.admin.requestedTemplate != null){
                   formBody.find('select[name="template"] option').filter(function () { return $(this).html() == blogging.admin.requestedTemplate; }).prop('selected', true);
                   blogging.admin.requestedTemplate = null;
               }
            }
            formBody.append($('<button type="button" id="id_save_form" name="Save">Save</button>\n'+
                              '<button type="button" id="id_publish_form" name="Publish">Publish</button>\n'+
                              '<button type="button" id="id_delete_form" name="Delete">Delete</button>'));
            return (formBody);
        },
        
        /**
         * @brief Try to migrate data from old form to new
         */
        migrateData: function(oldForm, oldOrdering, newForm, newOrdering){
            /* Copy in the common fields except the template field */
            unmigrated = [];
            migrated = [];
            for (var ii=0; ii< oldOrdering.length; ii++){
                if(oldOrdering[ii] != 'template'){
                    oldVal = oldForm.find('[name='+oldOrdering[ii]+']').val();
                    console.log(oldOrdering[ii]);
                    console.log(oldForm.find('[name='+oldOrdering[ii]+']'));
                    oldTag = oldForm.find('[name='+oldOrdering[ii]+']').prop('tagName').toLowerCase();
                    
                    console.log(newOrdering);
                    if(newOrdering.indexOf(oldOrdering[ii]) > -1){
                        /* Found */
                        console.log('Try to Migrate '+oldOrdering[ii]);
                        if(oldTag === newForm.find('[name='+ordering[ii]+']').prop('tagName').toLowerCase() ||
                           (oldTag === 'input' && newForm.find('[name='+oldOrdering[ii]+']').prop('tagName').toLowerCase() === 'textarea')){
                            newForm.find('[name='+oldOrdering[ii]+']').val(oldVal);
                            migrated.push(oldOrdering[ii]);
                        }
                        else{
                            unmigrated.push(oldOrdering[ii]);
                        }
                    }else{
                        unmigrated.push(oldOrdering[ii]);
                    }
                }
            }
            /* Foreach unmigrated type, if same tag element found, then copy, if general element found then append*/
            ported = false;
            for (var ii=0; ii< unmigrated.length; ii++){
                ported = false;
                for (var jj=0; jj< newOrdering.length; jj++){
                    if(migrated.indexOf(newOrdering[jj] <= -1)){
                        oldTag = oldForm.find('[name='+unmigrated[ii]+']').prop('tagName').toLowerCase();
                        newTag = newForm.find('[name='+newOrdering[jj]+']').prop('tagName').toLowerCase();
                        if(oldTag === newTag){
                            console.log('Migrate '+unmigrated[ii]+ ' to '+newOrdering[jj]);
                            newForm.find('[name='+newOrdering[jj]+']').val(oldForm.find('[name='+unmigrated[ii]+']').val());
                            migrated.push(newOrdering[jj]);
                            ported = true;
                            break;
                        }
                    }
                }
                if(ported == false){
                    for (var jj=0; jj< newOrdering.length; jj++){
                        oldTag = oldForm.find('[name='+unmigrated[ii]+']').prop('tagName').toLowerCase();
                        newTag = newForm.find('[name='+newOrdering[jj]+']').prop('tagName').toLowerCase();
                        if(oldTag === 'input' && newTag==='textarea'){
                            console.log('Migrate '+unmigrated[ii]+ ' to '+newOrdering[jj]);
                            newForm.find('[name='+newOrdering[jj]+']').val(newForm.find('[name='+newOrdering[jj]+']').val()+'\n'+oldForm.find('[name='+unmigrated[ii]+']').val());
                            migrated.push(newOrdering[jj]);
                            ported = true;
                            break;
                        }
                    }
                }
            }
            return(false);
        },
        
        /**
         * @brief Get contents of the object
         * TODO
         */
        getEntry : function(id){
            username = "dummy";
            filter_string = '?user='+username;
            blogging.utils.get('/rest/content/manage/'+id+'/', blogging.admin.parseEntry);
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
        saveEntry : function(data){
          console.log(data);
          
          $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!blogging.utils.csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", blogging.csrftoken);
                }
            }
          });
          
          url = "/rest/content/manage/";
          type = "POST";
          if ('id' in data)
          {
              url = url+data['id']+'/';
              type = "PUT";
          }
          //Save Form Data
          $.ajax({
            cache: false,
            url : url,
            type: type,
            dataType : "json",
            contentType: "application/json;",
            data : JSON.stringify(data),
            context : this,
            success : blogging.admin.parseEntry,
            error : blogging.utils.handleAjaxError
          }); 
        },
        
        deleteEntry : function(id){
            console.log("Delete "+id);
            $.ajaxSetup({
                beforeSend: function(xhr, settings) {
                    if (!blogging.utils.csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", blogging.csrftoken);
                    }
                }
            });
              
            url = "/rest/content/manage/"+id+'/';
            type = "DELETE";
            //Send delete request
            $.ajax({
              cache: false,
              url : url,
              type: type,
              dataType : "json",
              contentType: "application/json;",
              data : JSON.stringify(data),
              context : this,
              success : blogging.admin.parseResponse,
              error : blogging.utils.handleAjaxError
            });
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
           blogging.utils.get('/rest/content/manage/', blogging.admin.parseContent);
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
          
          /**
           * @brief Perform action on entr(y/ies)
           * 
           * This can be:
           * - Publish
           * - Unpublish
           * - Pin
           * - Unpin
           * - Delete
           */
           action : function(signal, entries){
             switch(signal){
               case 'PUB':
                 sig = 'PUBL';
                 break;
               case 'UNPUB':
                 sig = 'UNPB';
                 break;
               case 'PIN':
                 sig = 'PIN';
                 break;
               case 'UNPIN':
                 sig = 'UPIN';
                 break;
               case 'DEL':
                 sig = 'DEL';
                 break;
             }
             
             console.log(entries);
             
             $.ajaxSetup({
                 beforeSend: function(xhr, settings) {
                     if (!blogging.utils.csrfSafeMethod(settings.type) && !this.crossDomain) {
                         xhr.setRequestHeader("X-CSRFToken", blogging.csrftoken);
                     }
                 }
             });
              
             url = "/rest/content/manage/action/";
             type = "POST";
             data = {'objects': entries,
                     'action': sig};
    
             //Send delete request
             $.ajax({
               cache: false,
               url : url,
               type: type,
               dataType : "json",
               contentType: "application/json;",
               data : JSON.stringify(data),
               context : this,
               success : blogging.admin.parseResponse,
               error : blogging.utils.handleAjaxError
             });
           },
          /****************************************
           * General Helpers                      *
           ***************************************/
          /**
           * @brief Parse the response of request.
           */
          parseResponse : function(response){
            console.log(response);
          },
      };/* Admin namespace end */
   
      blogging.open = {
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
           blogging.utils.get('/rest/content/'+id+'/', blogging.open.parseEntry);
        },
      
        /**
         * @brief Parse the content response from server 
         */
        parseEntry : function(entry){
          console.log(entry);
        },
        
        /**
         * @brief Get Post ID from the URL if it exists, else 0
         */
        getPostId: function(){
            re = /.*\/blogging\/(\d+)\/edit\//;
            id = 0;
            if(re.test(window.location.href)){
                match = window.location.href.match(re);
                id = match[1];
            }
            return (id);
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
           blogging.utils.get('/rest/content/', blogging.open.parseContent);
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
      };/* Public namespace end*/
   
    /********************************************
     *  Usage                                   *
     ********************************************/
    blogging.csrftoken = null;
    blogging.guestUser = {
                  id: "0",
                  username: "Guest",
                  gravatar: "images/male.png",
                  url: "#",
              };
    blogging.currentUser = null;
    /* end blogging namespace object*/
    
    blogging.csrftoken = blogging.utils.getCookie('csrftoken');
    blogging.currentUser = blogging.guestUser;
    blogging.utils.getCurrentUser();
    
    /* These are for testing only */
    var post_list = [];
    
    /* Public API */
    //blogging.open.getContent();
    //blogging.open.getEntry("1");
    //blogging.open.getEntry("2"); /* Expect 404 */
    
    /* Admin side API */
    //blogging.admin.getContent();
    //blogging.admin.getEntry("1");
    //blogging.admin.getEntry("2");
    
    /* Saving Entires */
    var data = {
                'id': 9,
                //'title':"Test post via JS!",
                //'data' :"Test post content modified via JS request again using put",
                'policy': [{
                            'entry': 9,
                            'policy':"PUB",
                            'start': "2018-05-02T04:00:40Z",
                            'end'  : "2018-05-03T04:00:40Z",
                           }]
                };
    //blogging.admin.saveEntry(data);
    
    //blogging.admin.deleteEntry(10);
    //blogging.admin.action('PUB', [1,2]);
    
    //console.log(id);
    blogging.admin.fetchInitialForm(blogging.open.getPostId());
});