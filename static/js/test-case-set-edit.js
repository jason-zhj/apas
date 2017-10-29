$modal=$("#test_case_modal");
$table=$("#test_case_table");
test_input_name="test_inputs";
expected_output_name="expected_outputs";
id_name="id";
output_mark_allocation_name="output_mark_allocation";
modal_field_name_prefix="edit_";

// output block tag
start_block_tag="[{(";
end_block_tag=")}]";

$modal_id=$modal.find("input[name='"+modal_field_name_prefix+id_name+"']");
$modal_test_inputs=$modal.find("textarea[name='"+modal_field_name_prefix+test_input_name+"']");
$modal_expected_outputs=$modal.find("textarea[name='"+modal_field_name_prefix+expected_output_name+"']");
$modal_output_mark_allocation=$modal.find("textarea[name='"+modal_field_name_prefix+output_mark_allocation_name+"']");
$modal_add_block=$modal.find("#add_block").eq(0);

min_id=-1;
row_template="<tr>\
    <td ><p name='test_inputs'></p>\
        <input type='hidden' name='"+test_input_name+"' value=''/></td>\
    <td><p name='expected_outputs'></p>\
        <input type='hidden' name='"+ expected_output_name+"' value=''/></td>\
    <td class='hidden'><input type='hidden' name='"+ id_name+"' value='0'/>\
    <input type='hidden' name='"+ output_mark_allocation_name+"'/>\
    </td>\
    <td>\
        <a role='edit_button' href='#'><i class='fa fa-edit'></i></a>\
    </td>\
    <td>\
        <a role='delete_button' href='#' ><i class='fa fa-gavel'></i> </a>\
    </td>\
</tr>";

$(document).ready(
    function(){
        bindEventListener();
    }
);

function bindEventListener(){
    $("#add_new_btn").click(
        function(e){
            clear_modal($modal);
            $modal.modal();
        }
    );

    $modal_add_block.click(
        function(e){
            empty_block_str=start_block_tag+"\nEnter output here\n" +end_block_tag;
            $modal_expected_outputs.val($modal_expected_outputs.val()+empty_block_str);
        }
    );

    $("#testcase_set_submit").click(
        function(e){

            $trs=$table.find("tr");
            if ($trs.length<2){
                alert("Please set at least one test case!");
                e.preventDefault();
            }
            else{
                return True;
            }
        }
    );

    bindEventListnersForRow();

    $("#test_case_cancel").click(
        function(e){
            $modal.modal('hide');
        }
    );

    $("#test_case_submit").click(
        function(e){
            _id=$modal_id.val();
            test_inputs=$modal_test_inputs.val();
            expected_outputs=$modal_expected_outputs.val();
            output_mark_allocation=$modal_output_mark_allocation.val();
            // do mark allocation checking
            expected_output_list=expected_outputs.split("\n");
            mark_allocation_list=output_mark_allocation.split("\n");
            if (!check_mark_allocation(expected_output_list,mark_allocation_list)){
                return;
            }
            output_mark_allocation="";
            for (i=0;i<mark_allocation_list.length;i++){
                output_mark_allocation +=mark_allocation_list[i];
                if (i!=mark_allocation_list.length-1){
                    output_mark_allocation +="\n";
                }
            }
            if (_id !="0"){
                // this is an edit
                $tr=get_row_by_id(_id);
                if ($tr){
                    set_row_data($tr,test_inputs,expected_outputs,null,output_mark_allocation);
                }
            }
            else{
                // this is a create
                $table.append(row_template);
                $new_tr=$table.find("tr").last();
                set_row_data($new_tr,test_inputs,expected_outputs,min_id,output_mark_allocation);
                min_id -=1;
            }
            bindEventListnersForRow();
            $modal.modal('hide');
        }

    );
}


function check_mark_allocation(output_list,allocation_list){
    // get number of output parts
    in_block=false;
    // note: for block, increment num_output_parts at the closing tag
    num_output_parts=0;
    for (i=0;i<output_list.length;i++){
        cur_line=output_list[i];
        if (!in_block){
            if (cur_line.indexOf(start_block_tag)==-1){
                num_output_parts++;
            }
            else{
                in_block=true;
            }
        }
        else{
            if (cur_line.indexOf(end_block_tag)!=-1){
                in_block=false;
                num_output_parts++;
            }
        }
    }
    if (in_block){
        alert("Output blocks are not closed correctly!");
        return false;
    }
    // check whether the number of output parts match the number of allocations
    if (num_output_parts!=allocation_list.length){
        alert("The number of output parts is " + num_output_parts + ", but the number of mark allocation is " + allocation_list.length +
            "\nThe number of output parts need to match the number of mark allocations!");
        return false;
    }
    // 2 check whether allocation list is all numbers
    sum=0;
    for (i=0;i<allocation_list.length;i++){
        if (isNaN(allocation_list[i])){
            alert("Mark allocations must all be numbers!");
            return false;
        }
        sum +=Number(allocation_list[i]);
    }
    // 3 check whether add up to 100
    if (sum!=100){
        if (confirm("Mark allocations don't add up to 100!\nDo you want convert them into percentage automatically?")){
            // normalize the allocation
            remaining=100;
            for (j=0;j<allocation_list.length-1;j++){
                value=Math.floor(Number(allocation_list[j]) * 100 /sum);
                remaining -=value;
                allocation_list[j]=value+"";
            }
            allocation_list[j]=remaining + "";
            return true;
        }
        return false;
    }
    return true;

}


function normalize_mark_allocation(allocation_list){

}

function bindEventListnersForRow(){
    $("a[role='edit_button']").click(
        function(e){
            // get the inputs and outputs
            $tr=$(this).parent().parent();
            test_inputs=$tr.find("input[name='"+test_input_name+"']").val();
            expected_outputs=$tr.find("input[name='"+expected_output_name+"']").val();
            output_mark_allocation=$tr.find("input[name='"+output_mark_allocation_name+"']").val();
            id=$tr.find("input[name='"+id_name+"']").val();
            populate_modal($modal,test_inputs,expected_outputs,id,output_mark_allocation);
            // show edit box
            $modal.modal();
        }
    );

    $("a[role='delete_button']").click(
       function(e){
           $tr=$(this).parent().parent();
           id=$tr.find("input[name='"+id_name+"']").val();
           if (Number(id)>0){
               record_deleted_id(id);
           }
           $tr.remove();
       }
    );
}

function set_row_data($tr,test_inputs,expected_outputs,id,output_mark_allocation){
    $tr.find("input[name='"+test_input_name+"']").val(test_inputs);
    $tr.find("p[name='test_inputs']").html(test_inputs);
    $tr.find("input[name='"+expected_output_name+"']").val(expected_outputs);
    $tr.find("input[name='"+output_mark_allocation_name+"']").val(output_mark_allocation);
    $tr.find("p[name='expected_outputs']").html(expected_outputs);
    if (id){
        $tr.find("input[name='"+id_name+"']").val(id);
    }
}

function get_row_by_id(id){
    $id_inputs=$("#test_case_table").find("input[name='"+id_name+"']");
    for (i=0;i<$id_inputs.length;i++){
        if ($id_inputs.eq(i).val()==id){
            return $id_inputs.eq(i).parent().parent();
        }
    }
    return null;
}

function record_deleted_id(id){
    $input=$("input[name='_deleted_ids']");
    current_val=$input.val();
    if (current_val.length==0){
        $input.val(id);
    }
    else{
        $input.val(current_val + "," +id);
    }
}

function clear_modal($modal){
    $modal.find("textarea").val("");
    $modal_id.val("0");
}

function populate_modal($modal,test_inputs,expected_outputs,id,output_mark_allocation){
    $modal_test_inputs.val(test_inputs);
    $modal_expected_outputs.val(expected_outputs);
    $modal_output_mark_allocation.val(output_mark_allocation);
    $modal_id.val(id);
}