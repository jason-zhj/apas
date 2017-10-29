$endtest_btn=$("#endtest_btn");
$reattempt_btn=$("#reattempt_btn");

$(document).ready(
    function(e){
        setTimer();
        $endtest_btn.click(
            function(e){
                return confirm("Do you really want to end the test?");
            }
        );
        end_time=new Date(Number(END_YEAR),Number(END_MONTH)-1,Number(END_DAY),Number(END_HOUR),Number(END_MINUTE),Number(END_SECOND),0);
        current_time=Date();
        if (current_time>=end_time){
            $reattempt_btn.remove();
        }
    }
);


function setTimer(){
          minutes=$("input[name='time_limit']").val();
          end_time=new Date(Number(END_YEAR),Number(END_MONTH)-1,Number(END_DAY),Number(END_HOUR),Number(END_MINUTE),Number(END_SECOND),0);
          $('#test_timer').countdown({until: end_time,
              compact: true, format: 'HMS',
              description: '', alwaysExpire: true, onExpiry: testExpired});
}

function testExpired() {
    alert("Time is over!");
    window.location.href=REDIRECT_URL;
}