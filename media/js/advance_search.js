// Added by Chaobin Tang <ctang@redhat.com>

function getProdRelatedObj(prodIDs, target, targetID){
    /*
    Get Component, Version, Build, Category info
    of one or more product. Return value in a way
    like this:
    [[id, name], [id, name]]
    */
    if(typeof(prodIDs)=='string'){
        prodIDs = [prodIDs];
    }
    var data_api = '/ajax/get-prod-relate-obj/';
    var sep = ','; // used to join/split values
    var params   = {'p_ids': prodIDs.join(sep), 'target': target, 'sep': sep};
    var results;
    jQ.ajax({
        url: data_api,
        dataType: 'json',
        data: params,
        success: function(res){
            buildOptions(res, targetID);
        }
    });
}

function buildOptions(data, target){
    // target should be the ID of a select tag
    var options = new Array();
    for(var i=0;i<data.length;i++){
        var pair = data[i];
        options.push('<option value="'+pair[0]+'">'+pair[1]+'</option>');
    }
    options = options.join();
    jQ('#'+target).html(options);
}

function updateOptionOnProdChange(target, productID, targetID){
    /*
    @ target: component, version, category, build
    @ productID: select tag
    @ target select tag
    */
    jQ('#'+productID).change(function(){
        var prodIDs = jQ('#'+productID).val();
        getProdRelatedObj(prodIDs, target, targetID);
    });
    var prodIDs = jQ('#'+productID).val();
    if(prodIDs){
        getProdRelatedObj(prodIDs, target, targetID);
    }
}

jQ(function(){
    var searchForm = jQ('#frmSearch');
    var targetInp  = jQ('#inpTarget');
    // event listening for form submission
    jQ('#btnSearchPlan').click(function(){
        targetInp.val('plan');
        searchForm.submit();
    });
    jQ('#btnSearchCase').click(function(){
        targetInp.val('case');
        searchForm.submit();
    });
    jQ('#btnSearchRun').click(function(){
        targetInp.val('run');
        searchForm.submit();
    });
});

jQ(function(){
    // product select on change event binding
    updateOptionOnProdChange('version', 'pl_product', 'pl_version');
    updateOptionOnProdChange('version', 'r_product','r_version');
    updateOptionOnProdChange('build', 'r_product', 'r_build');
    updateOptionOnProdChange('component', 'pl_product', 'pl_component');
    updateOptionOnProdChange('component', 'cs_product', 'cs_component');
    updateOptionOnProdChange('category', 'cs_product', 'cs_category');
});
