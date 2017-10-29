var ace_edtiors=[];
TEST_COMPILATION_URL="/question/test-compilation/";
compilation_underway=false;
$(document).ready(
    function(e){
        setupAceEditor();
        bindCheckCompilationEvent();
    }
);

function setupAceEditor(){
    $editors=$("div[role='code_editor']");
    for (i=0;i<$editors.length;i++){
        $this_edior=$editors.eq(i);
        _id=$this_edior.attr("id");
        ace_edtiors[i] = ace.edit(_id);
        ace_edtiors[i].setTheme("ace/theme/monokai");
        // set editor language
        language_name=$this_edior.parent().find("input[name='editor_language_name']").eq(0).val();
        ace_edtiors[i].getSession().setMode("ace/mode/" + language_name);
    }
}

function bindCheckCompilationEvent(){
    $compilation_buttons=$("a[role='trigger_compilation']");
    for (i=0;i<$compilation_buttons.length;i++){
        $compilation_buttons.eq(i).on("click",function(e){
            // get the code in the editor
            $ul=$(this).parent().parent();
            code_editor_number=Number($ul.find("div[role='code_editor']").eq(0).attr("rank"));
            code=ace_edtiors[code_editor_number].getValue();
            // prevent multiple compilation request
            if (compilation_underway){
                alert("You cannot submit multiple compilation requests at the same time!");
                return;
            }
            // toggle image and button
            toggleImgAndButton($(this));
            $this_button=$(this);
            $alert_div=$(this).parent().find("div[role='alert']").eq(0);
            compilation_underway=true;
            // send ajax request
            var data={
                    required_language:$(this).parent().find("input[name='required_language']").val(),
                    code:code
                };
            $.ajax({
                    url: TEST_COMPILATION_URL,
                    type: "POST",
                    data: data,
                    cache:false,
                    dataType: "json",
                    success: function(response,status){
                       if (response && response['success'] == true) {
                            alert("Compilation is successful!");
                            $alert_div.addClass("hidden");
                       }
                        else{
                           $alert_div.html(response["message"]);
                            $alert_div.removeClass("hidden");
                       }
                       // toggle image and button
                        toggleImgAndButton($this_button);
                        // release compilatio request lock
                        compilation_underway=false;
                    }
                });
        });
    }
}

function toggleImgAndButton($button){
    $wait_img=$button.parent().find("img").eq(0);
    if ($button.hasClass("hidden")){
        // show the button and hide the image
        $button.removeClass("hidden");
        $wait_img.addClass("hidden");
    }
    else{
        // hide the button and show the image
        $button.addClass("hidden");
        $wait_img.removeClass("hidden");
    }
}