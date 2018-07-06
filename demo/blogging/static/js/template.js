var blogging = blogging || {};
$(document).ready(function(){
    /* 
     * Fixup blogging global object and place of insertion of properties
     */
    if(!blogging.hasOwnProperty('admin')){
        blogging.admin = {};
    }
    blogging.admin.template = {
          /**
           * @brief Create a new form row to accept a new Form Field in template
           */
          createNewOption: function(target){
          /* Insert New Row */
          
        },
        /**
         * @brief Parse the form and convert its into JSON format for saving. 
         * Then, save it. 
         */
        saveTemplate: function(event){
          data = [];
          //data.name = $('#id_name').val();
          //data.fields = [];
          /* Parse Form Data */
          event.preventDefault();
          end_of_form = false;
          elem = $('#div_title');
          count = 1;
          while(!end_of_form && count < 10){
            console.log(elem);
            if(elem.is('input#save_btn')){
              end_of_form=true;
            }
            else if(elem.is('div')){
                field = elem.find("input").val();
                type = elem.find("select").val();
                
                data.push({ [field]: {'type': type,
                                           'extra': (
                                        type==='CharField' ? {'max_length': 100}: null)}
                                });
                pr = 'Field: '+field+' Type: '+type;
                
                console.log(pr);
                
                elem = elem.next();
            }
            else{
              console.log('Exception');
            }
            count++;
          }
          console.log(data);
          $('#id_fields').val(JSON.stringify(data));
          if(count!=10){
            $('#template_form').submit();
          }
          else{
              return false;
          }
          /* POST data */
          /*
          $.ajaxSetup({
              beforeSend: function(xhr, settings) {
                  if (!blogging.utils.csrfSafeMethod(settings.type) && !this.crossDomain) {
                      xhr.setRequestHeader("X-CSRFToken", blogging.csrftoken);
                  }
              }
          });
          
          url = "/blogging/template/edit/";
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
            dataType : "text",
            //contentType: "application/json;",
            data : JSON.stringify(data),
            context : this,
            success : blogging.admin.parseEntry,
            error : blogging.utils.handleAjaxError
          });
           
          return false;
          */
        },
        
        /**
         * @brief Hide the `fields` form field and replace by an option to add 
         * fields. Add the defaults already.
         */
        render: function(){
           $('#div_fields').hide();
           
           
           add_btn = $('<button type="button" id="add_row_btn">Add Field</button>');
           
           /* If div_fields is non-empty, populate those fields */
           data = $('#id_fields').val();
           if (data != ''){
               data = JSON.parse(data);
               for (index in data){
                   item = data[index];
                   blogging.admin.template.addRow();
                   //console.log(Object.keys(item));
                   //console.log(item[Object.keys(item)[0]]['type']);
                   $('#save_btn').prev('div').find('input').val(Object.keys(item)[0]);
                   $('#save_btn').prev('div').find('select').val(item[Object.keys(item)[0]]['type']);
                   if(Object.keys(item)[0].toLowerCase().trim() === 'title'){
                       $('#save_btn').prev('div').attr('id', 'div_title');
                       $('#save_btn').prev('div').find('input').attr('id','id_title');
                       $('#save_btn').prev('div').find('input').prop("readonly", true);
                       $('#save_btn').prev('div').find('select').attr('id','type_title');
                       $('#save_btn').prev('div').find('select').prop("disabled", true);
                   }
               }
           }
           else{
               title = $('<div id="div_title">'+
                       '<input type="text" name="title" id="id_title" '+
                                            'value="Title" readonly>'+
                       '<select name="type" id="type_title" disabled>'+
                       '<option value="TextField">Multiline Text</option>'+
                       '<option value="CharField" selected>Short Text</option>'+
                       '<option value="ImageField">Image</option>'+
                       '</select></div>');
               $('#save_btn').before(title);
           }
           
           $('#template_form').before(add_btn);
           $('#add_row_btn').on("click", blogging.admin.template.addRow);
           return false;
        },
        
        /**
         * @brief Add a blank row to add another template field.
         */
        addRow: function(){
          text = $('<div>'+
                 '<input type="text" placeholder="Enter field name. e.g. Body">'+
                 '<select name="type">'+
                    '<option value="TextField">Multiline Text</option>'+
                    '<option value="CharField" selected>Short Text</option>'+
                    '<option value="ImageField">Image</option>'+
                 '</select></div>');
          $('#save_btn').before(text);
          $('#save_btn').prev('div').find('input').focus();
          return false;
        },
    };

    blogging.admin.template.api = {
        url: '/rest/content/template/',
        
        resetUrl: function()
        {
            blogging.admin.template.api.url = '/rest/content/template/';
        },
        
        renderForm: function(id=0){
            blogging.admin.template.api.resetUrl();
            /**
             * @fixme Remove this code later
             * Detach the original form from the page.
             */
            form = $('form').remove();
            overlay = $('<div class="overlay" id="overlay">'+
                           '<div><span>Close Btn</span></div>'+
                           '<div id="overlay_inner"></div>'+
                        '</div>');
            text = $('<h3>Create Template</h3><div>\n'+
                     '<button type="button" id="add_row_btn">Add Field</button>'+
                     '<form action="'+ blogging.admin.template.api.url+
                     (id==0?'':id+'/')+
                     '" method="post" id="template_form">\n'+
                     '<div id="div_name">\n'+
                     '<label for="id_name">Name:</label>'+
       '<input type="text" name="name" maxlength="15" required id="id_name" />'+
      '</div>\n<div id="div_title">'+
        '<input type="text" name="title" id="id_title" value="Title" readonly>'+
        '<select name="type" id="type_title" disabled>'+
          '<option value="TextField">Multiline Text</option>'+
          '<option value="CharField" selected>Short Text</option>'+
          '<option value="ImageField">Image</option>'+
        '</select></div>\n'+
            '<input type="submit" value="Save" name="Save" id="save_btn"/>\n'+
         '<input type="submit" value="Delete" name="Delete" id="del_btn"/>\n'+
                     '</form></div>');
           
           $('body').append(overlay);
           $('#overlay_inner').append(text);
           $('#add_row_btn').on("click", blogging.admin.template.addRow);
           $('#save_btn').on("click", blogging.admin.template.api.saveTemplate);
           
           if (id != 0){
               blogging.utils.get('/rest/content/template/'+id+'/', 
                                  blogging.admin.template.api.fillForm);
               blogging.admin.template.api.url += id+'/';
           }
        },
        
        /**
         * @brief Fill out form data from values already present
         */
        fillForm: function(entry){
          console.log(entry);
          $('#id_name').val(entry['name']);
          data = JSON.parse(entry['fields']);
          for (index in data){
              item = data[index];
              console.log($('#template_form input[value='+
                              Object.keys(item)[0].toLowerCase().trim()+']'));
              if(Object.keys(item)[0].toLowerCase().trim() === 'title'){
                  continue;
              }
              blogging.admin.template.addRow();
              //console.log(Object.keys(item));
              //console.log(item[Object.keys(item)[0]]['type']);
              $('#save_btn').prev('div').find('input').val(Object.keys(item)[0]);
              $('#save_btn').prev('div').find('select').val(item[Object.keys(item)[0]]['type']);
          }
        },
        
        saveTemplate: function(event){
            data = [];
            //data.name = $('#id_name').val();
            //data.fields = [];
            /* Parse Form Data */
            event.preventDefault();
            end_of_form = false;
            elem = $('#div_title');
            count = 1;
            while(!end_of_form && count < 10){
              console.log(elem);
              if(elem.is('input#save_btn')){
                end_of_form=true;
              }
              else if(elem.is('div')){
                  field = elem.find("input").val();
                  type = elem.find("select").val();
                  
                  data.push({ [field]: {'type': type,
                                             'extra': (
                                          type==='CharField' ? {'max_length': 100}: null)}
                                  });
                  pr = 'Field: '+field+' Type: '+type;
                  
                  console.log(pr);
                  
                  elem = elem.next();
              }
              else{
                console.log('Exception');
              }
              count++;
            }
            $('#id_fields').val(JSON.stringify(data));
            
            form_data = {
                'name': $('#id_name').val(),
                'fields': JSON.stringify(data)
            }
            console.log(form_data);
            console.log(blogging.admin.template.api.url);
            if(count!=10){
              /* POST data */
              
              $.ajaxSetup({
                  beforeSend: function(xhr, settings) {
                      if (!blogging.utils.csrfSafeMethod(settings.type) && !this.crossDomain) {
                          xhr.setRequestHeader("X-CSRFToken", blogging.csrftoken);
                      }
                  }
              });
              
              type = "PUT";
              //Save Form Data
              $.ajax({
                cache: false,
                url : blogging.admin.template.api.url,
                type: type,
                dataType : "json",
                contentType: "application/json;",
                data : JSON.stringify(form_data),
                context : this,
                success : blogging.admin.template.api.fillForm,
                error : blogging.utils.handleAjaxError
              });
            }
            return false;
        }
    };
    
    //$('#save_btn').on("click", blogging.admin.template.saveTemplate);
    //blogging.admin.template.render();
    re = /.*\/template\/(\d+)\//;
    id = 0;
    if(re.test(window.location.href)){
        match = window.location.href.match(re);
        id = match[1];
    }
    //console.log(id);
    blogging.admin.template.api.renderForm(id);
});
