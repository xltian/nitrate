Event.observe(window, 'load', function() {
    if (!checkCookie()) {
        $('login_info').innerHTML = "<font color=\"red\">Browser cookie support maybe disabled, please enable it for login.</font>";
        $('login_info').up().show();
        $('id_login_form').disable()
    }
    
    if ($('id_username')) {
        // $('id_username').observe('keydown', keydownUserName);
        $('id_password').observe('keydown', keydownPassword);
    };
})


function loginTCMS()
{
    username = $F('id_username');
    password = $F('id_password');

    if(username.replace(/\040/g, "").replace(/%20/g, "").length == 0)
    {
        Effect.Shake($('id_username'));
        $($('id_username')).focus()
        return false;
    }

    /*
    $('login_info').innerHTML = "Connecting to server ...";
    Effect.Appear('login_info');
    */
    var success = function(t) {
        var sURL = unescape(window.location.pathname);
    
        returnobj = t.responseText.evalJSON(true);
        response = returnobj.response;
        
        if (response == "ok") {
            // window.refresh();
            window.location.href = sURL;
        } else {
            Effect.Shake('id_username');
            $('login_info').innerHTML = response;
        }
    }

    var failure = function(t) {
        alert('Got some problem connect to the server');
    }
    
    $('id_login_form').submit();
}

function keydownUserName(event)
{
    if (event.keyCode == 13) 
        $('id_password').focus();
}

function keydownPassword(event)
{
    if (event.keyCode == 13)
        loginTCMS();
}
