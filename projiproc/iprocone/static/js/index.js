function updateView() {
    if (clientArea == null) clientArea = $('#clientArea');
    if (openFileDivision == null) openFileDivision = $('#openFileDivision');
    if (viewState.state == 'none') {
        $('#sidebar').css('visibility', 'hidden');
        $('#sidebarCollapse').css('visibility', 'hidden'); $('#sidebar').hide();
        $('#sidebarCollapse').hide();
        $('#sidebar').css('display', 'none');
        $('#sidebarCollapse').css('display', 'none');
        clientArea.html(openFileDivision);
        $('#fileOptions').css('visibility', 'hidden');
        $('#topBar').css('visibility', 'hidden');
    }
    if (viewState.state == 'opening') {
        $('#clientArea').html('<i class="fa fa-spinner fa-spin centered" style="font-size:24px"></i>');
    }
    if (viewState.state == 'open') {
        $('#sidebar').css('visibility', 'visible');
        $('#sidebarCollapse').css('visibility', 'visible');
        $('#sidebar').css('display', '');
        $('#sidebarCollapse').css('display', '');
        $('#sidebar').show();
        $('#sidebarCollapse').show();
        $('#fileOptions').css('visibility', 'visible');
        $('#topBar').css('visibility', 'visible');
        $('#clientArea').html("<img class='imageEditor' src='/iprocone/getImage?&xcsdf=" + encodeURI(new Date())
            + "'>");
    }
}


function closeFile() {
    viewState.state = 'none';
    updateView();
    $.ajax({
        url: "closeFile",
        type: "GET",
        cache: false,
        success: function (res) {
            // do nothing 
        }
    });
}

function openFile() {
    var emailValue=$('#email').val();
    var nameValue=$('#name').val();
    if(emailValue==null || nameValue==null || emailValue.trim().length==0 || nameValue.trim().length==0)
    {
        alert('Email id and name required');
    }
    else{
    var openFileForm = document.getElementById('openFileForm');
    var formData = new FormData(openFileForm);
    viewState.state = 'opening';
    updateView();
    $('#spinnerWrap').css('display', '');
    $('#spinnerWrap').css('visibility', 'visible');
    $('#spinnerWrap').show();
    $.ajax({
        url: "openFile",
        type: "POST",
        data: formData,
        enctype: 'multipart/form-data',
        processData: false, contentType: false,
        cache: false,
        success: function (res) {
            viewState.state = 'open';
            viewState.fileName = res.fileName;
            viewState.email = res.email;
            viewState.name = res.name;
            openFileForm.reset();
            updateView();
            $('#spinnerWrap').css('display', 'none');
            $('#spinnerWrap').css('visibility', 'hidden');
            $('#spinnerWrap').hide();
            $('#imageFileName').html('Image : ' + viewState.fileName);
        }
    });
}
}

function openFileForWaterMark()
{
    var openFileForm = document.getElementById('openFileForm');
    var formData = new FormData(openFileForm);
    viewState.state = 'opening';
    updateView();
    $('#spinnerWrap').css('display', '');
    $('#spinnerWrap').css('visibility', 'visible');
    $('#spinnerWrap').show();
    $.ajax({
        url: "openFile",
        type: "POST",
        data: formData,
        enctype: 'multipart/form-data',
        processData: false, contentType: false,
        cache: false,
        success: function (res) {
        }
    });

}

function addWatermark()
{
    var watermarkForm = document.getElementById('addWatermark')
    var formData = new FormData(watermarkForm)
    console.log("Text radio value :"+formData.get('textRadio'));
    console.log("Custom radio value :"+formData.get('customRadio1'));

    $.ajax({
        url: "addWatermark",
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
function addFilter(filterType)
{
    $('#spinnerWrap').css('display', '');
    $('#spinnerWrap').css('visibility', 'visible');
    $('#spinnerWrap').show();
    $.ajax({
        url: "filterImage",
        type: "POST",
        cache: false,
        data: {"filterType": filterType},
        success: function (res) {
            updateView(); $('#spinnerWrap').css('display', 'none');
            $('#spinnerWrap').css('visibility', 'hidden');
            $('#spinnerWrap').hide();
        }
    });
}


function flipHorizontal(flipURL)
{
    $('#spinnerWrap').css('display', '');
    $('#spinnerWrap').css('visibility', 'visible');
    $('#spinnerWrap').show();
    $.ajax({
        url: flipURL,
        type: "GET",
        cache: false,
        success: function (res) {
            updateView(); $('#spinnerWrap').css('display', 'none');
            $('#spinnerWrap').css('visibility', 'hidden');
            $('#spinnerWrap').hide();
        }
    });
}

function flipVertical(flipURL)
{
    $('#spinnerWrap').css('display', '');
    $('#spinnerWrap').css('visibility', 'visible');
    $('#spinnerWrap').show();
    $.ajax({
        url: flipURL,
        type: "GET",
        cache: false,
        success: function (res) {
            updateView(); $('#spinnerWrap').css('display', 'none');
            $('#spinnerWrap').css('visibility', 'hidden');
            $('#spinnerWrap').hide();
        }
    });
}

function toGrayscale() {
    $('#spinnerWrap').css('display', '');
    $('#spinnerWrap').css('visibility', 'visible');
    $('#spinnerWrap').show();
    $.ajax({
        url: "toGrayscale",
        type: "GET",
        cache: false,
        success: function (res) {
            updateView(); $('#spinnerWrap').css('display', 'none');
            $('#spinnerWrap').css('visibility', 'hidden');
            $('#spinnerWrap').hide();
        }
    });
}

function rotateImage() {
    var rotateForm = document.getElementById('rotateItForm');
    var rotateItFormData = new FormData(rotateForm);
    $.ajax({
        url: "rotateIt",
        type: "POST",
        data: rotateItFormData,
        processData: false,
        contentType: false,
        cache: false,
        success: function (res) {
            updateView();
        }
    });

}

function scaleIt() {
    var scaleForm = document.getElementById('scaleItForm');
    var scaleItFormData = new FormData(scaleForm);
    $.ajax({
        url: "scaleIt",
        type: "POST",
        data: scaleItFormData,
        processData: false,
        contentType: false,
        cache: false,
        success: function (res) {
            updateView();
        }
    });
}

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

