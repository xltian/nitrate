Nitrate.Report = {};
Nitrate.Report.List = {};
Nitrate.Report.CustomSearch = {};
Nitrate.Report.CustomDetails = {};

Nitrate.Report.List.on_load = function(){
	
}

Nitrate.Report.Builds = {}

Nitrate.Report.Builds.on_load = function()
{
    if($('report_build')) {
        TableKit.Sortable.init('report_build',
        {
            rowEvenClass : 'roweven',
            rowOddClass : 'rowodd',
            nosortClass : 'nosort'
        });
    }
}

Nitrate.Report.CustomSearch.on_load = function()
{
    if($('id_pk__in')) {
        bind_build_selector_to_product(
            false, $('id_product'), $('id_pk__in')
        );
    };
    
    if($('id_build_run__product_version')) {
        bind_version_selector_to_product(
            true, false, $('id_product'), $('id_build_run__product_version')
        );
    };
    
    if($('id_testcaserun__case__category')) {
        bind_category_selector_to_product(
            true, false, $('id_product'), $('id_testcaserun__case__category')
        );
    };
    
    if($('id_testcaserun__case__component')) {
        bind_component_selector_to_product(
            true, false, $('id_product'), $('id_testcaserun__case__component')
        );
    };
    
    if($('id_table_report')) {
        TableKit.Sortable.init('id_table_report',
        {
            rowEvenClass : 'even',
            rowOddClass : 'odd',
            nosortClass : 'nosort'
        });
    };
    
    $$('.build_link').invoke('observe', 'click', function(e) {
        e.stop();
        var param = $('id_form_search').serialize(true);
        var build_id = this.siblings()[0].value;
        param.pk__in = build_id;
        
        postToURL(this.href, param, 'get')
    });
}

Nitrate.Report.CustomDetails.on_load = function()
{
    if($('id_pk__in')) {
        bind_build_selector_to_product(
            false, $('id_product'), $('id_pk__in')
        );
    };
    
    if($('id_build_run__product_version')) {
        bind_version_selector_to_product(
            true, false, $('id_product'), $('id_build_run__product_version')
        );
    };
}
