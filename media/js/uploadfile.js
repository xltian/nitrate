valueUploadNum = 1;

Event.observe(window, 'load', function() {
    if($('id_upload_files')) {
        createUploadZone();
    }
})

function getUploadParam()
{
    args = $A(arguments);
    id = args[0];

    var param = new Object();
    param.id = id;
    param.upload_zone = 'id_upload_zone_' + id;
    param.new_upload_iframe = 'id_upload_iframe_' + id;
    param.upload_form = 'id_upload_form_' + id;
    param.upload_field = 'id_upload_file_' + id;
    param.upload_file_name = "upload_file_" + id;
    param.upload_link = 'id_upload_link_' + id;
    param.remove_link = 'id_remove_file_link' + id;
    param.progress_bar = 'id_upload_progressbar_' + id;
    param.display_file = 'id_display_file_' + id;
    param.display_file_input = 'id_input_file_' + id;
    return param;
}

function createUploadZone()
{
    var p = getUploadParam(valueUploadNum);
    
    /*
    var new_upload_zone = new Element('div', { 'id': p.upload_zone });
    var new_upload_iframe = new Element('iframe',
                                    { 'id': p.upload_iframe,
                                      'border': '0',
                                      'height': '20',
                                      'width': '300'
                                    });
    var new_upload_form = new Element('form', { 'id': p.upload_form, 'enctype': 'multipart/form-data' });
    
    var new_upload_field = new Element('input', 
                                    { 'id': p.upload_field,
                                        'type': 'file',
                                        'name': 'upload_file',
                                        'size': '15'
                                    });
                                    
    var new_upload_link = new Element('a', 
                                    { 'id': p.upload_link,
                                        'href': 'javascript:uploadFile(' + p.id + ')',
                                    }).update('  Upload');


    new_upload_form.insert(new_upload_field);
    new_upload_form.insert(new_upload_link);
    new_upload_iframe.contentWindow.document.insert(new_upload_form)
    new_upload_zone.insert(new_upload_iframe);

    $('id_upload_files').insert(new_upload_zone);
    */
    var new_upload_zone = new Element('div', { 'id': p.upload_zone });
	/*
    var new_upload_field = new Element('input', 
                                    { 'id': p.upload_field,
                                        'type': 'text',
                                        'name': 'upload_file',
                                        'size': '12',
    });
	*/
    var new_upload_link = new Element('input', 
                                    { 'id': p.upload_link,
                                        'type': 'button',
                                        'name': 'upload_file',
                                        'value': 'Upload...',
    });
    
    
    // new_upload_zone.insert(new_upload_field);
    new_upload_zone.insert(new_upload_link);

    $('id_upload_files').insert(new_upload_zone);
    
    
    new Ajax_upload(new_upload_link, {
        // Location of the server-side upload script
        action: '/management/uploadfile/',
        // File upload name
        name: 'upload_file',

        // Fired when user selects file
        // You can return false to cancel upload
        // @param file basename of uploaded file
        // @param extension of that file
        onSubmit: function(file, extension) {
            /*
            if (! (extension && /^(jpg|png|jpeg|gif)$/.test(extension))) {
                    // extension is not allowed
                    alert('Error: invalid file extension');
                    // cancel upload
                    return false;
            }
            */
            
            new_upload_link.disable();
            // new_upload_field.value = file + " is uploading...";
            valueUploadNum = valueUploadNum + 1;
            createUploadZone();
            // new_upload_field.hide();
            new_upload_link.hide();
            createUploadProgressBar(id-1, file);
        },
        // Fired when file upload is completed
        // @param file basename of uploaded file
        // @param response server response
        onComplete: function(file, response) {
            returnobj = response.evalJSON(true);
            if(returnobj.response == 'ok') {
                removeUploadProgressBar(id);
                createFileDisplayZone(id, returnobj.file_id, returnobj.file_name);
                // $(p.upload_form).remove();
                // alert("Upload file OK");
            } else {
				removeUploadProgressBar(id);
                // $(p.upload_form).show();
                // alert("Upload file failed");
            }
        }
    }); 
}

function createUploadProgressBar(id, filename)
{
    var p = getUploadParam(id);
    var new_upload_progressbar = new Element('div', { 'id': p.progress_bar }).update(filename + ' is uploading...');
    $(p.upload_zone).insert(new_upload_progressbar);
}

function removeUploadProgressBar(id)
{
    var p = getUploadParam(id);
    $(p.progress_bar).remove();
}

function createFileDisplayZone(id, file_id, file_name)
{
    var p = getUploadParam(id);    
    var new_upload_hidden_file = new Element('input', 
                                            { 'id': p.display_file_input, 
                                            'type': 'hidden', 
                                            'name': 'upload_file_' + id,
                                            'value': file_id,
    });
    var new_upload_display_file = new Element('span',{
                                            'id': p.display_file,
    }).update(file_name);
    var new_remove_uploaded_link = new Element('a', 
                                            { 'id': p.remove_link,
                                              'href': 'javascript:removeUploadedFile(' + id + ');'
    }).update('Remove');
    
    $(p.upload_zone).insert(new_upload_display_file);
    $(p.upload_zone).insert(new_upload_hidden_file);
    $(p.upload_zone).insert(new_remove_uploaded_link);
}

function uploadFile(id)
{   
    var p = getUploadParam(id);
    
    if($F(p.upload_field) == "") {
        alert("You should select a file before upload");
        return false;
    }
    
    valueUploadNum = valueUploadNum + 1;
    // createUploadZone();
    // $(p.upload_form).hide();
    // createUploadProgressBar(id);
    
    /*
    var success = function(t) {
        returnobj = t.responseText.evalJSON(true);
        if(returnobj.response == 'ok') {
            removeUploadProgressBar(id);
            createFileDisplayZone(id);
            $(p.upload_form).remove();
            alert("Upload file OK");
        } else {
            $(p.upload_form).show();
            alert("Upload file failed");
        }
    }
    
    var failure = function(t) {
        alert("Upload file failed, something wrong when connect to server, please contact to admin.");
        $(p.upload_form).show();
    }
    
    var url  = getURLParam().url_upload_file;
    var params = $(p.upload_form).serialize(true);
    console.log(params);
    console.log(url);
    var add_new_comment_ajax = new Ajax.Request(url, {method:'post', parameters:params, onSuccess:success, onFailure:failure});
    */
}

function removeUploadedFile(id)
{
    var p = getUploadParam(id);
    $(p.upload_zone).remove();
}