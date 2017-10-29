function validate_weightage(){
    total_weightage=0;
    $rows=$("#selection_table").find("tr");
    record="";
    for (i=0;i<$rows.length;i++){

        isChosen=$rows.eq(i).find("[type='checkbox']").eq(0).prop("checked");
        if (isChosen){
            pool_name=$rows.eq(i).find("[name='pool_name']").eq(0).html();
            weightage_item=$rows.eq(i).find("[name='weightage']").eq(0).val();
            number_to_select=$rows.eq(i).find("[name='number_to_select']").eq(0).val();
            if (isNaN(weightage_item) || isNaN(number_to_select)){
                alert("Weightage and number to select must be integer number!");
                return false;
            }
            max_number_to_select=$rows.eq(i).find("[name='max_number_to_select']").eq(0).val();
            if (Number(number_to_select)>Number(max_number_to_select)){
                alert("The max number of questions you can select from " + pool_name + " is "+max_number_to_select);
                return false;
            }
            total_weightage +=Number(weightage_item) * Number(number_to_select);
            id=$rows.eq(i).find("[name='id']").eq(0).val();
            record+=id +"," +weightage_item+","+number_to_select+";";
        }
    }

    if(total_weightage!=100){
        alert("total weightage is not 100!");
        return false;
    }

    // record the choice
    $("input[name='m2m_record']").val(record);
    return true;
}