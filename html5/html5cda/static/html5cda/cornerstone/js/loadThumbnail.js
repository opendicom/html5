
function loadThumbnail(studyViewer, viewportModel, studyId) {
    var data = jQuery.parseJSON(sessionStorage.getItem('json_estudio'));
    var imageViewer = new ImageViewer(studyViewer, viewportModel);
    var seriesIndex = 0;
    data.seriesList.forEach(function(series) {
        var stack = {
            seriesDescription: series.seriesDescription,
            stackId: series.seriesNumber,
            imageIds: [],
            seriesIndex: seriesIndex,
            currentImageIdIndex: 0,
            frameRate: series.frameRate
        };


        // Populate imageIds array with the imageIds from each series
        // For series with frame information, get the image url's by requesting each frame
        if (series.numberOfFrames !== undefined) {
            var numberOfFrames = series.numberOfFrames;
            for (var i = 0; i < numberOfFrames; i++) {
                var imageId = series.instanceList[0].imageId + "?frame=" + i;
                /*if (imageId.substr(0, 4) !== 'http') {
                    imageId = "dicomweb://cornerstonetech.org/images/ClearCanvas/" + imageId;
                }*/
                stack.imageIds.push(imageId);
            }
        // Otherwise, get each instance url
        } else {
            series.instanceList.forEach(function(image) {
                var imageId = image.imageId;

                /*if (image.imageId.substr(0, 4) !== 'http') {
                    imageId = "dicomweb://cornerstonetech.org/images/ClearCanvas/" + image.imageId;
                }*/
                stack.imageIds.push(imageId);
            });
        }
        // Move to next series
        seriesIndex++;

        // Add the series stack to the stacks array
        imageViewer.stacks.push(stack);
    });
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
            $('.viewer').removeClass('hidden');
            //useItemStack(0, stackIndex);
        }).data('stack', stackIndex);
    });
}