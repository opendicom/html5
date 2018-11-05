// Load in HTML templates
var viewportTemplate; // the viewport template
loadTemplate("templates/viewport.html", function(element) {
    viewportTemplate = element;
});
var studyViewerTemplate; // the study viewer template
loadTemplate("templates/studyViewer.html", function(element) {
    studyViewerTemplate = element;
});
// Get study from JSON manifest
var study = jQuery.parseJSON(sessionStorage.getItem('json_estudio'));
var studyTab = '<li><a href="#x' + study.patientId + '" data-toggle="tab">' + study.patientName + '</a></li>';
$('#tabs').append(studyTab);
// Add tab content by making a copy of the studyViewerTemplate element
var studyViewerCopy = studyViewerTemplate.clone();
studyViewerCopy.attr("id", 'x' + study.patientId);
studyViewerCopy.removeClass('hidden');
studyViewerCopy.appendTo('#tabContent');
// Show the new tab (which will be the last one since it was just added
$('#tabs a:last').tab('show');
// Toggle window resize (?)
$('a[data-toggle="tab"]').on('shown.bs.tab', function(e) {
    $(window).trigger('resize');
});
resizeMain();
// Now load the study.json
loadStudy(studyViewerCopy, viewportTemplate, study.studyId);
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
