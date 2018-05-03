    $(function () {

        var editor = editormd("editor_md_content", {
            width: "80%",
            height: 1000,
            // theme : "dark",
            // previewTheme : "dark",
            // editorTheme : "pastel-on-dark",
            // syncScrolling: "single",
            path: "/django_manager/editormd/lib/",
            emoji: true,
            imageUpload: true,
            imageUploadTokenURL: '/django_manager/upload',
            imageUploadURL: '/django_manager/upload',
            imageRequestBaseURL: '{{ imageRequestBaseURL }}',
            imageFormats: ["jpg", "jpeg", "gif", "png", "bmp", "webp", "svg"]
        });
    });