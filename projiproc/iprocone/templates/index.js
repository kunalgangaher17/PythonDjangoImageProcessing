function setborder() {
    var borderForm = document.getElementById('setborder')
    var formData = new FormData(borderForm)

    $.ajax({
        url: "setBorder",
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,
        cache: false,
        success: function (response) {
            updateView()
        }
    });
}

function enhanceImage() {
    var enhanceImageForm=document.getElementById('enhanceImage');
    var formData=new FormData(enhanceImageForm)

    $.ajax({
        url:"enhanceImage",
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,
        cache: false,
        success: function(response) {
            updateView()
        }
    })



}

