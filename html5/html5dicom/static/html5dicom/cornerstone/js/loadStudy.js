
// Load JSON study information for each study
function loadStudy(studyViewer, viewportModel, studyId) {

    // Get the JSON data for the selected studyId
    //$.getJSON('studies/' + studyId, function(data) {
    var data = jQuery.parseJSON(sessionStorage.getItem('json_estudio'));
    cornerstoneWADOImageLoader.external.cornerstone = cornerstone;
    cornerstoneWebImageLoader.external.cornerstone = cornerstone;

    let webWorkerUrl = 'lib/cornerstoneWADOImageLoaderWebWorker.min.js';
    let codecsUrl = 'cornerstoneWADOImageLoaderCodecs.js';

    try {
        window.cornerstoneWADOImageLoader.webWorkerManager.initialize({
            maxWebWorkers: 4,
            startWebWorkersOnDemand: true,
            webWorkerPath: webWorkerUrl,
            webWorkerTaskPaths: [],
            taskConfiguration: {
                decodeTask: {
                    loadCodecsOnStartup: true,
                    initializeCodecsOnStartup: false,
                    codecsPath: codecsUrl,
                    usePDFJS: false,
                    strict: true
                }
            }
        });
    } catch (error) {
        throw new Error('cornerstoneWADOImageLoader is not loaded');
    }


        
        

        var imageViewer = new ImageViewer(studyViewer, viewportModel);
        imageViewer.setLayout('1x1'); // default layout

        function initViewports() {
            imageViewer.forEachElement(function(el) {
                cornerstone.enable(el);
                $(el).droppable({
                    drop : function(evt, ui) {
                        var fromStack = $(ui.draggable.context).data('stack'), toItem = $(this).data('index');
                        useItemStack(toItem, fromStack);
                    }
                });
            });
        }

        // setup the tool buttons
        setupButtons(studyViewer);

        // layout choose
        $(studyViewer).find('.choose-layout a').click(function(){
            var previousUsed = [];
            imageViewer.forEachElement(function(el, vp, i){
                if (!isNaN($(el).data('useStack'))) {
                    previousUsed.push($(el).data('useStack'));
                }
            });

            var type = $(this).text();
            imageViewer.setLayout(type);
            initViewports();
            resizeStudyViewer();
            if (previousUsed.length > 0) {
                previousUsed = previousUsed.slice(0, imageViewer.viewports.length);
                var item = 0;
                previousUsed.forEach(function(v){
                    useItemStack(item++, v);
                });
            }

            //return false;
        });

        // Load the first series into the viewport (?)
        //var stacks = [];
        //var currentStackIndex = 0;
        var seriesIndex = 0;

        // Create a stack object for each series
        data.seriesList.forEach(function(series) {
            var stack = {
                seriesDescription: series.seriesDescription,
                stackId: series.seriesNumber,
                imageIds: [],
                seriesIndex: seriesIndex,
                currentImageIdIndex: 0,
                frameRate: series.frameRate
            };

            series.instanceList.forEach(function(image) {
                if (image.numFrames > 1){
                    for (var i = 0; i < image.numFrames; i++) {
                        var imageId = image.imageId + "&frame=" + i;
                        stack.imageIds.push(imageId);
                    }
                }else{
                    stack.imageIds.push(image.imageId);
                }
            });
            // Move to next series
            seriesIndex++;

            // Add the series stack to the stacks array
            imageViewer.stacks.push(stack);
        });

        // Resize the parent div of the viewport to fit the screen
        var imageViewerElement = $(studyViewer).find('.imageViewer')[0];
        var viewportWrapper = $(imageViewerElement).find('.viewportWrapper')[0];
        var parentDiv = $(studyViewer).find('.viewer')[0];

        //viewportWrapper.style.width = (parentDiv.style.width - 10) + "px";
        //viewportWrapper.style.height = (window.innerHeight - 150) + "px";

        var studyRow = $(studyViewer).find('.studyRow')[0];
        var width = $(studyRow).width();

        //$(parentDiv).width(width - 170);
        //viewportWrapper.style.width = (parentDiv.style.width - 10) + "px";
        //viewportWrapper.style.height = (window.innerHeight - 150) + "px";

        // Get the viewport elements
        var element = $(studyViewer).find('.viewport')[0];

        // Image enable the dicomImage element
        initViewports();
        //cornerstone.enable(element);

        // Get series list from the series thumbnails (?)
        var seriesList = $(studyViewer).find('.thumbnails')[0];
        imageViewer.stacks.forEach(function(stack, stackIndex) {

            // Create series thumbnail item
            var seriesEntry = '<a class="list-group-item" + ' +
                'oncontextmenu="return false"' +
                'unselectable="on"' +
                'onselectstart="return false;"' +
                'onmousedown="return false;">' +
                '<div class="csthumbnail"' +
                'oncontextmenu="return false"' +
                'unselectable="on"' +
                'onselectstart="return false;"' +
                'onmousedown="return false;"></div>' +
                "<div class='text-center small'>" + stack.seriesDescription + '</div></a>';

            // Add to series list
            var seriesElement = $(seriesEntry).appendTo(seriesList);

            // Find thumbnail
            var thumbnail = $(seriesElement).find('div')[0];

            // Enable cornerstone on the thumbnail
            cornerstone.enable(thumbnail);

            // Have cornerstone load the thumbnail image
            cornerstone.loadAndCacheImage(imageViewer.stacks[stack.seriesIndex].imageIds[0]).then(function(image) {
                // Make the first thumbnail active
                if (stack.seriesIndex === 0) {
                    $(seriesElement).addClass('active');
                }
                // Display the image
                cornerstone.displayImage(thumbnail, image);
                $(seriesElement).draggable({helper: "clone"});
            });

            // Handle thumbnail click
            $(seriesElement).on('click touchstart', function() {
              useItemStack(0, stackIndex);
            }).data('stack', stackIndex);
        });

        function useItemStack(item, stack) {
            var imageId = imageViewer.stacks[stack].imageIds[0], element = imageViewer.getElement(item);
            if ($(element).data('waiting')) {
                imageViewer.viewports[item].find('.overlay-text').remove();
                $(element).data('waiting', false);
            }
            $(element).data('useStack', stack);

            displayThumbnail(seriesList, $(seriesList).find('.list-group-item')[stack], element, imageViewer.stacks[stack], function(el, stack){
                if (!$(el).data('setup')) {
                    setupViewportOverlays(el, data);
                    setupViewport(el, stack, this);
                    
                    $(el).data('setup', true);
                }
            });
            cornerstone.loadAndCacheImage(imageId).then(function(image){
                setupViewportOverlays(element, data);
                setupViewport(element, imageViewer.stacks[stack], image);
                
            });
        }
        // Resize study viewer
        function resizeStudyViewer() {
            var studyRow = $(studyViewer).find('.studyContainer')[0];
            var height = $(studyRow).height();
            var width = $(studyRow).width();
            console.log($(studyRow).innerWidth(),$(studyRow).outerWidth(),$(studyRow).width());
            $(seriesList).height("100%");
            $(parentDiv).width(width - $(studyViewer).find('.thumbnailSelector:eq(0)').width());
            $(parentDiv).css({height : '100%'});
            $(imageViewerElement).css({height : $(parentDiv).height() - $(parentDiv).find('.text-center:eq(0)').height()});

            imageViewer.forEachElement(function(el, vp) {
                cornerstone.resize(el, true);

                if ($(el).data('waiting')) {
                    var ol = vp.find('.overlay-text');
                    if (ol.length < 1) {
                        ol = $('<div class="overlay overlay-text">Please drag a stack onto here to view images.</div>').appendTo(vp);
                    }
                    var ow = vp.width() / 2, oh = vp.height() / 2;
                    ol.css({top : oh, left : ow - (ol.width() / 2)});
                }
            });
        }
        // Call resize viewer on window resize
        $(window).resize(function() {
            resizeStudyViewer();
        });
        resizeStudyViewer();
        if (imageViewer.isSingle())
            useItemStack(0, 0);

    //});
}
