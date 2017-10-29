function validate_weightage(){

    total_weightage=0;
    _string="";
    $rows=$("#selection_table").find("tr");
    for (i=0;i<$rows.length;i++){

        isChosen=$rows.eq(i).find("[type='checkbox']").eq(0).prop("checked");
        if (isChosen){
            weightage_item=$rows.eq(i).find("[name='weightage']").eq(0).val();
            if (isNaN(weightage_item)){
                alert("Weightage value: " + weightage_item + " is not a number!");
                return false;
            }
            total_weightage +=Number(weightage_item);
            _id=$rows.eq(i).find("[name='id']").eq(0).val();
            _string +=_id + "," +weightage_item + ";" ;
        }
    }
    if(total_weightage!=100){
        alert("total weightage is not 100!");
        return false;
    }

    $("input[name='m2m_record']").eq(0).val(_string);
    return true;
}