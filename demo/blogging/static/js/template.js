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
                 '<select name="type" id="type_title">'+
                    '<option value="TextField">Multiline Text</option>'+
                    '<option value="CharField" selected>Short Text</option>'+
                    '<option value="ImageField">Image</option>'+
                 '</select></div>');
          $('#save_btn').before(text);
          $('#save_btn').prev('div').find('input').focus();
          return false;
        },
    };
    
    $('#save_btn').on("click", blogging.admin.template.saveTemplate);
    blogging.admin.template.render();
    
});