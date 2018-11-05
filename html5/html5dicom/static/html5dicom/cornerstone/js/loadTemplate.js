function loadTemplate(url, callback) {
    var data = $.ajax({
        type: "GET",
        url: url,
        cache: false,
        async: false
    }).responseText;
    var parsed = $.parseHTML(data);
    $.each(parsed, function(index, ele) {
        if(ele.nodeName === 'DIV')
        {
            var element = $(ele);
            callback(element);
        }
    });
}

    