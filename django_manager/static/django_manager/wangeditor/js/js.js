function wang_edit_init(id) {
    if ($("#"+id).val()){
        var editor = new wangEditor(id);
        editor.config.printLog = false;
        editor.config.height = 200;
        editor.config.uploadImgUrl = "/django_manager/upload?upload_type=wangEditor";
        editor.config.uploadImgFileName = 'uploadFile';
        editor.create();
    }
}

$(function () {
    wang_edit_init('wang_editor_content');
    $(".wangEditor-txt").height($(window).height()- 140);
    // $(".wangEditor-txt").width($(window).width()- 200);
    left = $("label[for='wang_editor_id']").width();
    var div_css = {
        "position": "relative",
        "background-color": "#fff",
        "border": "1px solid #ccc",
        "z-index": 1,
        "width": "94%",
        "left": left
    };
    $(".wangEditor-container").css(div_css);
});
