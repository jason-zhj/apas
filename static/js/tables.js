$(document).ready(
    function(){
        // hide the file path in the file input controls
        bind_search_event();

        bind_checkall_event();

        bind_sort_event();

        bind_single_delete_event();
    }
);

function bind_single_delete_event(){
    $("a[role='single-delete']").click(
        function(e){
            $tr=$(this).parent().parent();
            id=$tr.find("input[name='delete']").eq(0).val();
            if (!confirm("Are you sure to delete this item?")){
                return false;
            }
            else{
                $("#msg_modal").modal({backdrop: 'static',
                keyboard: false});
                $('<form action="'+group_delete_url+'" method="POST">' +
            '<input type="hidden" name="delete" value="' + id + '">' +
            '</form>').submit();
            }

        }
    )
}

function bind_checkall_event(){
        $("input[name='checkall']").click(
            function(e){
                $table=$(this).parent().parent().parent();
                $table.find("input[name='delete']").prop("checked",$(this).prop("checked"));
            }
    )
}

function bind_search_event(){
    $search_btn=$("#list_search");
    $search_btn.click(
        function(e){
            search_content=$("#search_content").val();
            search_field_value=$("#search_field").val();
            current_url=window.location.pathname;
            new_url=current_url + "?" + search_field_value + "=" + search_content;
            window.location.href=new_url;
        }
    );
}

function bind_sort_event(){
    $sort_select=$("#list_sort");
    $sort_select.change(
        function(e){
            current_url=window.location.pathname;
            new_url=current_url + "?";
            url_dict=getUrlVars();
            url_dict["sort_by"]=$(this).val();
            for (key in url_dict){
                new_url += key + "=" + url_dict[key] + "&";
            }
            window.location.href=new_url;
        }
    );
}

function getUrlVars()
{
    var vars = {};
    if (window.location.href.indexOf('?')==-1){
        return vars;
    }
    var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
    for(var i = 0; i < hashes.length && hashes[i].length>0; i++)
    {
        hash = hashes[i].split('=');
        vars[hash[0]]=hash[1];
    }
    return vars;
}