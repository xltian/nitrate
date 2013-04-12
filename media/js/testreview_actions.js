Nitrate.TestReviews = {};
Nitrate.TestReviews.New = {};
Nitrate.TestReviews.Details = {};

Nitrate.TestReviews.New.on_load = function()
{
    TableKit.Sortable.init('testcases');
}

Nitrate.TestReviews.Details.on_load = function()
{
    bindReviewCommentFormSubmit();
    bindReviewShowCommentLink();
}

function getTestReviewCaseParam(id)
{
    var id = id;
    
    var param = new Object();
    
    param.review_case_container  = 'id_review_case_container_' + id;
    param.review_case_form = 'id_form_case_' + id;
    return param;
}

function changeReviewCaseStatus(id, case_status_id)
{
    var p = getTestReviewCaseParam(id)
    
    var e_case_status_id = $(p.review_case_form).adjacent('input[name="case_status_id"]')[0]
    
    if(e_case_status_id.value == case_status_id) {
        alert('No changes for the case.');
        return false;
    }
    
    e_case_status_id.value = case_status_id;
    
    var complete = function(t) {
        fireEvent($(p.review_case_container).down(), 'click');
        unbindReviewCommentFormSubmit();
        unbindReviewShowCommentLink();
        
        bindReviewCommentFormSubmit();
        bindReviewShowCommentLink();
    }
    
    var failure = function(t) {
        alert('Change review case status failed');
        return false;
    }
    
    new Ajax.Updater(p.review_case_container, $(p.review_case_form).action, {
        method: 'get',
        parameters: $(p.review_case_form).serialize(true),
        onFailure: failure,
        onComplete: complete,
    });
}

function bindReviewCommentFormSubmit(container)
{
    $$('form.comment_form').invoke('observe', 'submit', function(e) {
        e.stop();
        
        var comment_container = this.up().previous().down().next();
        var parameters = this.serialize(true);
        if(parameters.comment) {
            comment_container.show();
            submitComment(comment_container, parameters);
            this.elements['comment'].value = '';
        }
    })
}

function unbindReviewCommentFormSubmit(container)
{
    $$('form.comment_form').invoke('stopObserving', 'submit');
}

function bindReviewShowCommentLink(container)
{
    $$('a.link_show_comments').invoke('observe', 'click', function(e) {
        var container = this.up(1).next();
        
        container.toggle();
        constructCommentZone(container, this.parentNode.serialize(true));
        
        if(container.getStyle('display') == 'none')
            this.update('Show comments');
        else
            this.update('Hide comments');
    })
}

function unbindReviewShowCommentLink(container)
{
    $$('a.link_show_comments').invoke('stopObserving', 'submit');
}
