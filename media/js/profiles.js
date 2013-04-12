Nitrate.Profiles = {
    Infos: {},
    Bookmarks: {},
};

Nitrate.Profiles.Bookmarks.on_load = function()
{
    if($('id_table_bookmark')) {
        TableKit.Sortable.init('id_table_bookmark',
        {
            rowEvenClass : 'roweven',
            rowOddClass : 'rowodd',
            nosortClass : 'nosort'  
        });
    }
    
    if($('id_check_all_bookmark')) {
        $('id_check_all_bookmark').observe('click', function(e) {
            clickedSelectAll(this, $('id_table_bookmark'), 'pk');
        })
    }
    
    $('id_form_bookmark').observe('submit', function(e) {
        e.stop();
        
        if(!confirm(default_messages.confirm.remove_bookmark))
            return false;
        
        var callback = function(t) {
            var returnobj = t.responseText.evalJSON();
            
            if (returnobj.rc != 0) {
                alert(returnobj.response);
                return returnobj;
            }
            // using location.reload will cause firefox(tested) remember the checking status
            window.location = window.location;
        }
        var parameters = this.serialize(true);
        if(!parameters['pk']){
            alert('No bookmark selected.');
            return false;
        }
        removeBookmark(this.action, this.method, parameters, callback);
    })
}

function removeBookmark(url, method, parameters, callback)
{
    new Ajax.Request(url, {
        method: method,
        parameters: parameters,
        onSuccess: callback,
        onFailure: json_failure,
    })
}
