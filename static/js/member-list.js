/**
 * Created by Administrator on 7/2/2015.
 */
$(document).ready(
    function(){
        $('#submit_change').click(
            function(e){
                // 1 collect the students to be added and the students to be removed
                // 1-1 students to be removed
                students_to_remove="";
                $table1=$("#students_in_group");
                $rows=$table1.find("tr");
                for (i=0;i<$rows.length;i++){
                    $row=$rows.eq(i);
                    if (!is_checked($row)){
                        students_to_remove += get_id($row) + ",";
                    }
                }
                // 1-2 students to be added
                students_to_add="";
                $table2=$("#students_not_in_group");
                $rows=$table2.find("tr");
                for (i=0;i<$rows.length;i++){
                    $row=$rows.eq(i);
                    if (is_checked($row)){
                        students_to_add += get_id($row) + ",";
                    }
                }
                // 2 set the string into form
                $form=$("#member_form").eq(0);
                $form.find("input[name='students_to_remove']").eq(0).val(students_to_remove);
                $form.find("input[name='students_to_add']").eq(0).val(students_to_add);
                // 3 submit the form
                $form.submit();

            }
        );
    }
);


function is_checked(row){
    $checkbox=row.find("input[type='checkbox']");
    if ($checkbox.length>0){
        $checkbox=$checkbox.eq(0);
    }
    if ($checkbox.prop("checked")==true){
        return true;
    }

    return false;
}

function get_id(row){
    $field=row.find("input[type='hidden']");
    if ($field.length>0){
        $field=$field.eq(0);
    }
    return $field.val();
}