function deleConfirm(attachment_id,home,plan_id){

//var xmlHttp=new XMLHttpRequest();
//var url = "/management/deletefile/(?P<file_id>\d+)/$";
var url="/management/deletefile/"+attachment_id+"?"+home+"="+plan_id;
var answer=confirm("Arey you sure to delete the attachment?");
if(!answer)
    return false;

new Ajax.Request(url,{
    method:'get',
    onSuccess:function(response){
    //location.reload();
    returnobj=response.responseText.evalJSON(true);
    if(returnobj.rc==0){
    $(""+attachment_id).remove();
    jQ('#attachment_count').text(parseInt(jQ('#attachment_count').text())-1);
    }   
     else if (returnobj.response='auth_failure'){
    alert("Permission denied!");
}
    else {
    alert ("Server Exception");
}
}
});

}

