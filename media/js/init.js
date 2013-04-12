function enableShiftSelectOnCheckbox(className){
    jQ('.'+className).shiftcheckbox();
}

jQ(document).ready(function(){
    enableShiftSelectOnCheckbox('shiftselect');
})