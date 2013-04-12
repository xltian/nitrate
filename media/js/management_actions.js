Nitrate.Management = {};
Nitrate.Management.Environment = {};
Nitrate.Management.Environment.Edit = {};

Nitrate.Management.Environment.Edit.on_load = function()
{
	SelectFilter.init("id_properties", "properties", 0, "/admin_media/");
}
Nitrate.Management.Environment.on_load=function(){
	
	$$('a.loglink').invoke('observe', 'click', function(e){
		this.up(1).next().toggle();
		})
	
	}
function addEnvGroup()
{
	var success = function(t) {
		returnobj = t.responseText.evalJSON(true);
		
		if (returnobj.response == 'ok') {
			if(returnobj.id)
				window.location.href=getEnvURLParams().edit_group + '?id=' + returnobj.id;
			return true;
		} else {
			alert(returnobj.response);
			return false;
		}
	}
	
	var group_name = prompt("New environment group name");
	
	if(group_name) {
		new Ajax.Request(getEnvURLParams().add_group, {
				method: 'get',
				onSuccess: success,
				parameters: {
					action: 'add',
					name: group_name,
				}
		})
	}
}

function deleteEnvGroup(id, env_group_name)
{
	var answer = confirm("Are you sure you wish to remove environment group - " + env_group_name);
	
	if(!answer) {
        return false;
	}

    var url=getEnvURLParams().delete_group + '?action=del&id=' + id;
    new Ajax.Request(url,{
    method:'get',
    onComplete:function(response){
        returnobj=response.responseText.evalJSON(true);
        if(returnobj.response == 'Permission denied.'){
            alert(returnobj.response);    
            }
        else if(returnobj.response == 'ok'){
        $(""+id).remove();
        }
        }
    })
 }

function selectEnvProperty(property_id)
{
	$$('#id_properties_container li').each(function(obj) {
		obj.className = '';
	})
	
	$('id_property_' + property_id).className = 'focus';
		
	new Ajax.Updater('id_values_container', getEnvURLParams().list_property_values, {
		method: 'get',
		parameters: {
			action: 'list',
			property_id: property_id,
		}
	})
}

function addEnvProperty()
{
	var success = function(t) {
		returnobj = t.responseText.evalJSON(true);

		if (returnobj.response == 'ok') {
			$$('#id_properties_container li').each(function(obj) {
				obj.className = '';
			});

			id = returnobj.id;
			name = returnobj.name;
			
			html = '<li id="id_property_'
				+ id
				+ '">'
				+'<input type="checkbox">'
				+'<a id="id_property_name_'
				+ id
				+ '"'
				+ ' onclick="javascript:selectEnvProperty(\''
				+ id
				+ '\')">'
				+ name
				+ '</a>'
				+'<span class="right-action">'
				+'<a onclick="editEnvProperty(\''
				+ id
				+'\')"'
				+'class="editlink"'
				+'>'
				+'Rename'
				+'</a>'
				+'</li>';
			$('id_properties_container').innerHTML += html;

			selectEnvProperty(id);
		} else {
			alert(returnobj.response);
			return false;
		}	
	}

	var property_name = prompt("New property name");

	if(property_name) {
		new Ajax.Request(getEnvURLParams().add_property, {
				method: 'get',
				onSuccess: success,
				parameters: {
					action: 'add',
					name: property_name,
				},
		})
	}
}

function editEnvProperty(id)
{	
	var new_property_name = prompt("New property name", $('id_property_name_' + id).innerHTML);
	
	var success = function(t) {
		returnobj = t.responseText.evalJSON(true);

		if (returnobj.response == 'ok') {
			$('id_property_name_' + id).innerHTML = new_property_name;
		} else {
			alert(returnobj.response);
			return false;
		}	
	}

	if(new_property_name) {
		new Ajax.Request(getEnvURLParams().edit_property, {
				method: 'get',
				onSuccess: success,
				parameters: {
					action: 'edit',
					id: id,
					name: new_property_name,
				},
		})
	}
}

function deleteEnvProperty()
{
	var answer = confirm("Are you sure you wish to remove these environment property?");
	
	if(answer) {
		window.location.href=getEnvURLParams().del_property + '?action=del&' + $('id_property_form').serialize()
	}
}

function enableEnvProperty()
{
	if(!$$('#id_properties_container input[name="id"]:checked').length)  {
		alert("Please click the checkbox to choose properties");
		return false;
	}

	window.location.href=getEnvURLParams().modify_property + '?action=modify&status=1&' + $('id_property_form').serialize()
	
}


function disableEnvProperty()
{
	if(!$$('#id_properties_container input[name="id"]:checked').length) {
		alert("Please click the checkbox to choose properties");
		return false;
	}
	window.location.href=getEnvURLParams().modify_property + '?action=modify&status=0&' + $('id_property_form').serialize()
}

function addEnvPropertyValue(property_id)
{
	var value_name = $F('id_value_name');
	
	if(value_name.replace(/\040/g, "").replace(/%20/g, "").length == 0) {
		alert('Value name could not be blank or space.');
		return false;
	}

	if(value_name) {
		new Ajax.Updater('id_values_container', getEnvURLParams().add_property_value, {
			method: 'get',
			parameters: {
				action: 'add',
				property_id: property_id,
				value: value_name,
			}
		}
	)}
}

function editEnvPropertyValue(property_id, value_id)
{
	var value_name = prompt('New value name', $('id_value_' + value_id).innerHTML);

	if(value_name) {
		new Ajax.Updater('id_values_container', getEnvURLParams().add_property_value, {
			method: 'get',
			parameters: {
				action: 'edit',
				property_id: property_id,
				id: value_id,
				value: value_name,
			}
		}
	)}
}

function enableEnvPropertyValue(property_id)
{
	if(!$$('#id_values_container input[name="id"]:checked').length) {
		alert('Please click the checkbox to choose properties');
		return false;
	}
	
	new Ajax.Updater('id_values_container', getEnvURLParams().add_property_value, {
		method: 'get',
		parameters: {
			action: 'modify',
			property_id: property_id,
			status: 1,
			id: $('id_value_form').serialize(true).id,
		}
	})
}

function disableEnvPropertyValue(property_id)
{
	if(!$$('#id_values_container input[name="id"]:checked').length) {
		alert('Please click the checkbox to choose properties');
		return false;
	}
	
	new Ajax.Updater('id_values_container', getEnvURLParams().add_property_value, {
		method: 'get',
		parameters: {
			action: 'modify',
			property_id: property_id,
			status: 0,
			id: $('id_value_form').serialize(true).id,
		}
	})
}
