$(function(){
    $('#join').click(function(){
        var input = $('#confirm').val();
        var url = window.location.href;
        var patt = /gp+[0-9]*/g;
        url = url.match(patt)[0];
        patt = /[^0-9]/g;
        var group_id = url.replace(patt, '');
        $.getJSON($SCRIPT_ROOT + '/_join_group',
            {group_id: group_id, confirm:input},
            function(data){
                if(data.status == 'joined'){
                    alert('joined!');
                }else if(data.status == 'fail'){
                    alert('fail!!');
                }else if(data.status == 'non-ex') {
                    alert('non-ex!');
                }
                location.reload();
        });
    });
});

$(function(){
    $('#quit').click(function(){
        var url = window.location.href;
        var patt = /gp+[0-9]*/g;
        url = url.match(patt)[0];
        patt = /[^0-9]/g;
        var group_id = url.replace(patt, '');
        $.getJSON($SCRIPT_ROOT + '/_quit_group',
            {group_id: group_id},
            function(data){
                if(data.status == '0'){
                    alert('fail!!');
                }else if(data.status == '1') {
                    alert('success');
                }
                location.reload();
        });
    });
});

$(function(){
    $('.discuss-delete').click(function(){
        var discuss_id = Number($(this).attr('victim'));
        var div = $(this).parent();
        console.log(discuss_id);
        $.getJSON($SCRIPT_ROOT + '/_delete_discussion',
            {discuss_id: discuss_id},
            function(data){
                if(data.success == '0'){
                    alert('failed');
                }else{
                    $(div).remove();
                    alert('succeeded!');
                }
        });
    });
});


$(function () {
    $(".countdown_timepicker").datetimepicker({
        //showOn: "button",
        //buttonImage: "./css/images/icon_calendar.gif",
        //buttonImageOnly: true,
        showButtonPanel: false,
        timeOnly: true,
        showSecond: true,
        timeFormat: 'hh:mm:ss',
        stepHour: 1,
        stepMinute: 1,
        stepSecond: 1
    });

    $(".ui_timepicker").datetimepicker({
        //showOn: "button",
        //buttonImage: "./css/images/icon_calendar.gif",
        //buttonImageOnly: true,
        //showButtonPanel: false,
        //timeOnly: true,
        showSecond: true,
        timeFormat: 'hh:mm:ss',
        stepHour: 1,
        stepMinute: 1,
        stepSecond: 1
    });
});

// if I have time, I want to realize the drag part;
$(function(){
    var options = 0;
    $('.addOption').click(function(){
        ++options;
        var vote_options_num = document.getElementById('vote-options-num');
        vote_options_num.setAttribute('value',options.toString());

        //var vote_option = document.createElement('input');
        //vote_option.setAttribute('type','radio');
        //vote_option.setAttribute('class','vote-option');
        //vote_option.setAttribute('name','vote-option[]');

        var vote_option_content = document.createElement('input');
        //vote_option_content.setAttribute('type','text');
        vote_option_content.setAttribute('class','vote-option-content form-control');
        vote_option_content.setAttribute('name','vote-option-content-'+options.toString());
        vote_option_content.readOnly = true;
        vote_option_content.setAttribute('value','double click to change value');

        vote_option_content.ondblclick = function()
        {
            this.readOnly = false;
            this.className = "vote-option-content-edit";
        }
        vote_option_content.onblur = function()
        {
            this.readOnly = true;
            this.className = "vote-option-content";
        }
        //var vote_change_row = document.createElement('br');
        var vote_wrap = document.createElement('lable');
        var vote_order = String.fromCharCode(64+options); //limit to 26 options


        vote_wrap.innerHTML = vote_order;
        //vote_wrap.appendChild(vote_option);
        vote_wrap.appendChild(vote_option_content);


        var vote_add_form = document.getElementById("vote-add-form");
        var vote_add_button = document.getElementById("vote-add-button");

        //vote_add_form.insertBefore(vote_option,vote_add_button);
        //vote_add_form.insertBefore(vote_option_content,vote_add_button);
        //vote_add_form.insertBefore(vote_change_row,vote_add_button);
        vote_add_form.insertBefore(vote_wrap,vote_add_button);
    });
});

$(function(){
    $('.changeTimeSet').click(function(){
        var time = document.getElementById("timeinterval");
        var datetime = document.getElementById("datetime");
        var endtime_selection = document.getElementById("endtime-selection");

        if (endtime_selection.value == "2")
        {
            datetime.style['display'] = "none";
            time.style['display'] = "block";
            endtime_selection.value = "1";
        }
        else
        {
            time.style['display'] = "none";
            datetime.style['display'] = "block";
            endtime_selection.value = "2";
        }
    });
});