// Load in HTML templates
    var viewportTemplate; // the viewport template
    var data = $.ajax({
        type: "GET",
        url: "templates/viewport.html",
        cache: false,
        async: false
    }).responseText;
    var parsed = $.parseHTML(data);
    $.each(parsed, function(index, ele) {
        if(ele.nodeName === 'DIV')
        {
            viewportTemplate = $(ele);
        }
    });

    var study = jQuery.parseJSON(sessionStorage.getItem('json_estudio'));
    /*var studyTab = '<li class="active"><a href="#x' + study.patientId + '" data-toggle="tab">' + study.patientName + '</a></li>';
    $('#tabs').append(studyTab);*/
    /*var studyViewerCopy = studyViewerTemplate.clone();
    studyViewerCopy.attr("id", 'x' + study.patientId);
    studyViewerCopy.removeClass('hidden');
    studyViewerCopy.appendTo('#tabContent');
    $('#tabs a:last').tab('show');*/
    $('a[data-toggle="tab"]').on('shown.bs.tab', function(e) {
        $(window).trigger('resize');
    });

    loadStudy($('#studyViewerTemplate'), viewportTemplate, study.studyId);
    //loadThumbnail(studyViewerCopy, viewportTemplate, study.studyId);

// Show tabs on click
$('#tabs a').click (function(e) {
  e.preventDefault();
  $(this).tab('show');
});

// Resize main
function resizeMain() {
  var height = $(window).height();
  $('#main').height(height - 50);
  $('#tabContent').height(height - 50 - 42);
}


// Call resize main on window resize
$(window).resize(function() {
    resizeMain();
});
resizeMain();


// Prevent scrolling on iOS
document.body.addEventListener('touchmove', function(e) {
  e.preventDefault();
});
