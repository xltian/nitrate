Nitrate.Management = {};
Nitrate.Management.Accounts = {}

Nitrate.Management.Accounts.on_load = function()
{
    SortableTable.setup({
        tableSelector : ['table.itemList'],
        nosortClass : 'nosort'
    });
}

function keydownSearchUserName(event)
{
    if (event.keyCode == 13) {
        $('id_btn_search').focus();
    }
}

function getAccountParam(index_id)
{
    var param = new Object();

    param.user_name = "id_user_name_" + index_id;
    param.user_email = "id_user_email_" + index_id;
    param.btn_enable_user = "id_btn_enable_user_" + index_id;
    param.btn_disable_user = "id_btn_disable_user_" + index_id;
    
    param.user_form = "id_user_form_" + index_id;
    param.user_field = "id_user_" + index_id;
    param.submit_button = "id_btn_submit_" + index_id;
    
    return param;
}

function clickedBtnSearch()
{
    debug_output('The search user button clicked.');
    
    username = $F('id_username');
    group_id = $F('id_group_id');
    
    $('id_txt_need_more_condition').hide();
    
    // Detect the user name field is blank or not.
    // Limit to 3 texts as condition for DO NOT CRASH THE BROWSER
        
    if (group_id == '') {
        if (username.replace(/\040/g, "").replace(/%20/g, "").length < 3) {
            $('id_txt_need_more_condition').appear();
            Effect.Shake('id_username');
            return false;
        }
    }
    
    $('id_search_user_form').submit()
}

// To handle the search button clicked actions
function clickedSearchUser()
{
    debug_output('The search user button clicked.');
    
    username = $F('id_username');
    group_id = $F('id_group_id');
    
    $('id_txt_need_more_condition').hide();
    
    // Detect the user name field is blank or not.
    // Limit to 3 texts as condition for DO NOT CRASH THE BROWSER
    if (username.replace(/\040/g, "").replace(/%20/g, "").length < 3) {
        $('id_txt_need_more_condition').appear();
        Effect.Shake('id_username');
        return false;
    }

    // Search the user
    searchUser(username, group_id);
}

// Search the user
function searchUser()
{
    debug_output('Start to search the user');
    
    args = $A(arguments);
    username = args[0];
    group_id = args[1];
    
    var success = function(t) {
        returnobj = t.responseText.evalJSON(true);
        
        $('id_user_list').update("");
        for(i=0; i < returnobj.size(); i++) {
            userid = returnobj[i].userid;
            username = returnobj[i].name;
            email = returnobj[i].email;
            groups = returnobj[i].groups;

            debug_output('response from server: ' + username);

            $('id_user_list').innerHTML += createUserElement(userid, username, email, groups);
        }
    }
    
    var failure = function(t) {
        alert('Search user failed, please wait a moment and try again or contact to administrator.');
    }
    
    var url  = getURLParam().url_search_users;
    var params = $('id_search_user_form').serialize(true);

    debug_output('Search user values - ' + params.username);

    var edit_testcase_ajax = new Ajax.Request(url, { method:'get', 
                                                     parameters:params,
                                                     onSuccess:success, 
                                                     onFailure:failure
                                                   }
                                            );
}

// Build the user zone for change the information
function createUserElement()
{   
    args = $A(arguments);
    userid = args[0];
    username = args[1];
    email = args[2];
    groups = args[3];
    
    var p = getAccountParam(userid);
    
    debug_output("Start to build the element: " + userid + username + email);
    for(i=0; i < groups.size(); i++) {
        debug_output("Add group " + groups[i].group_name + " to user " + username);
        if(groups[i].group_id == 7)
            var is_admin = true;
        else
            var is_admin = false;
    
        if(groups[i].group_id == 15)
            var is_tester = true;
        else
            var is_tester = false;
    }
        
    /* Element of content like following:
    
    <tr>
        <td>dli 's ID</td>
        <td>Danqing Li</td>
        <td>dli@redhat.com</td>
        <td class="changeable"> 
            <input type="checkbox" checked>Tester</input>&nbsp;&nbsp;
            <input type="checkbox">Admin</input>
            <input type="button" value="submit">
        </td>
    </tr>
    */
    
    /*
    var user_field = TR({className: 'user', id: 'id_user_' + userid}, [
         TD({className: "userid"}, userid),
         TD({className: "username"}, username),
         TD({className: "email"}, email),
    ]);
    */
         
    debug_output("The content of is_tester is: " + is_tester);
    debug_output("The content of is_admin is: " + is_admin);
    
    
    var user_field = "<tr>";
    debug_output("The content of user_field is: " + user_field);
    
    user_field += "<td>" + userid + "</td>";
    user_field += "<td>" + username + "</td>";
    user_field += "<td>" + email + "</td>";
    
    debug_output("The content of user_field is: " + user_field);

    user_field += "<td id=\"" + p.user_field + "\">";
    user_field += "<form id=\"" + p.user_form + "\">";
    user_field += "<input type=\"hidden\" name=\"userid\" value=" + userid + " />";
    if(is_tester)
        user_field += "<input type=\"checkbox\" name=\"is_tester\" onclick=\"changeAccountInfoToModified(" + userid + ")\" checked /><label>Tester</label>";
    else
        user_field += "<input type=\"checkbox\" name=\"is_tester\" onclick=\"changeAccountInfoToModified(" + userid + ")\" /><label>Tester</label>";
        
    if(is_admin)
        user_field += "<input type=\"checkbox\" name=\"is_admin\" onclick=\"changeAccountInfoToModified(" + userid + ")\" checked /><label>Admin</label>";
    else
        user_field += "<input type=\"checkbox\" name=\"is_admin\"onclick=\"changeAccountInfoToModified(" + userid + ")\" /><label>Admin</label>";

    user_field += "<input id=\"" + p.submit_button + "\" type=\"button\" value=\"Submit\" style=\"display: none\" onclick=\"changeUserGroup(" + userid + ")\" />";
    user_field += "</form>";
    user_field += "</td>";
    user_field += "</tr>";
    
    debug_output("Build the element finished.");
    return user_field;
}

function changeAccountInfoToModified(userid) 
{
    debug_output("Received changed signal from: " + userid);
    
    var p = getAccountParam(userid);
    if ($(p.user_field).className != "changeable") {        
        $(p.user_field).className = "changeable";
        $(p.submit_button).show();
    }
}

function changeAccountInfoToNormal(userid) 
{    
    var p = getAccountParam(userid);
    $(p.user_field).className = "";
    $(p.submit_button).hide();
}

function changeUserGroup(userid)
{
    debug_output("Change user " + userid + "'s Group");
    
    var p = getAccountParam(userid);
    
    var success = function(t) {
        debug_output('Change user group is finished');
        returnobj = t.responseText.evalJSON(true);
        if(returnobj.response == "ok")
            changeAccountInfoToNormal(userid);
        else
            alert("Unknow error");
    }
    
    var failure = function(t) {
        alert('Change group of user failed, please wait a moment and try again or contact to administrator.');
    }
    
    var url  = getURLParam(userid).url_change_user_group;
    var params = $(p.user_form).serialize(true);

    debug_output('Values of url is: ' + url);
    debug_output('Values of is_tester and is_admin are: ' + params.is_tester + ' ' + params.is_admin);
    
    var change_user_group = new Ajax.Request(url, { method:'get', 
                                                     parameters:params,
                                                     onSuccess:success, 
                                                     onFailure:failure
                                                   }
                                            );
}

function changeUserStatus(userid, enabled)
{
    var p = getAccountParam(userid);
    
    var success = function(t) {
        returnobj = t.responseText.evalJSON(true);

        debug_output(returnobj)

        if (returnobj.response != 'ok') {
            alert("Got some unknown error");
            return false
        }
        
        if (returnobj.enabled == 0) {
            // Setting interface for disabled user
            debug_output('Setting interface for disabled user')
            $(p.user_name).className = "disabled_user";
            $(p.user_email).className = "disabled_user";
            $(p.btn_enable_user).show();
            $(p.btn_disable_user).hide();
        } else {
            // Setting interface for enabled user
            debug_output('Setting interface for enabled user')
            $(p.user_name).className = '';
            $(p.user_email).className = '';
            $(p.btn_enable_user).hide();
            $(p.btn_disable_user).show();
        }
    }
    
    var failure = function(t) {
        alert('Change status of user failed, please wait a moment and try again or contact to administrator.');
    }
    
    var url  = getURLParam(userid).url_change_user_status;
    var params = { 'userid': userid, 'enabled': enabled, }
    var change_user_status = new Ajax.Request(url, { method:'get', 
                                                     parameters: params,
                                                     onSuccess:success, 
                                                     onFailure:failure
                                                   }
                                            );
}
