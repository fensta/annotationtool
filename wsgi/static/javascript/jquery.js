/**
 * Created by fensta on 6/21/2015.
 */
// Times in ms
var opinion_start = 0; // Offset when 3rd set of labels timers were started
var fact_start = 0; // Offset when 2nd set of labels timers were started
// Previously stored times for a tweet in seconds
var relevance_offset = 0;
var old_relevance_offset = 0; // Stores offset from DB when user clicked on "next" or "previous"
var opinion_offset = 0;
var old_opinion_offset = 0
var confidence_relevance_offset = 0;
var old_confidence_relevance_offset = 0;
var confidence_opinion_offset = 0;
var old_confidence_opinion_offset = 0;
var fact_offset = 0;
var old_fact_offset = 0;
var confidence_fact_offset = 0;
var old_confidence_fact_offset = 0;
// compared to the start of the 1st set of labels
var update_interval = 500;  // Update speed for timer in ms

var Relevance;
var Fact;
var Opinion;
var Con_relevance;
var Con_fact;
var Con_opinion;
var HAS_BEEN_CLICKED = "firststart";
// These variables are used to make the states independent of the text.
var p_state = 0;    // 0: "Pause", 1: "Continue"

// How to measure time: end time - start time - pause time at submission
$(document).ready(function(){
    // ******************
    // Annotation window
    // ******************
    var $a = $("#test1");
    var $b = $("#test2");
    var $c = $("#test3");
    var $d = $("#test4");
    var $e = $("#test5");
    var $f = $("#test6");
    var $relevance_buttons = $("#relevance_button_div");
    var $rel = $("#relevant");
    var $irr = $("#irrelevant");
    var $opinions = $("#opinion_div");
    //var $opinion_buttons = $("#opinion_button_div");
    //var $confidence_relevance = $("#confidence_relevance_div");
    //var $confidence_opinion = $("#confidence_opinion_div");
    //var $confidence_fact = $("#confidence_fact_div");
    var $load = $("#load_screen");
    var $fact = $("#factual");
    var $non_fact = $("#non_factual");
    var $facts = $("#fact_div");

    Relevance = new Timer(update_interval, $a);
    Opinion = new Timer(update_interval, $b);
    Fact = new Timer(update_interval, $c);
    Con_relevance = new Timer(update_interval, $d);
    Con_opinion = new Timer(update_interval, $e);
    Con_fact = new Timer(update_interval, $f);

    start_timers();
    // To indicate whether relevant was clicked for the first time
    $relevance_buttons.addClass(HAS_BEEN_CLICKED);
    $non_fact.addClass(HAS_BEEN_CLICKED);
    // Hide 2nd & 3rd set of labels
    $facts.hide();
    $opinions.hide();
    // Hide loading screen initially
    $load.hide();

    // Hide potential error messages
    hide_error_messages();

    // Hide inputs for next/previous
    $("#previous_div input:button, #next_div input:button").hide();

    // In the following part mainly the timers are stopped when clicking a
    // button

    // Show 2nd set of labels
    // Apply function to both buttons
    //$rel.add($irr).click(function(ev) {
    $rel.add($irr).bind("click", function(ev) {
        hide_error($("#rel_error"));
        // .show() displays also these errors shown below, so we hide them
        hide_error($("#fac_error"));
        hide_error($("#fac_conf_error"));
        // Show only if div not visible
        if (!$facts.is(":visible")) {
            $facts.show();
        }
        if ($relevance_buttons.hasClass(HAS_BEEN_CLICKED)) {
            fact_start = Fact.GetCurrentTime();
            console.log("fact offset: " + fact_start);
            $relevance_buttons.removeClass(HAS_BEEN_CLICKED);
        }
        else {
            console.log("fact offset won't be changed, it's still " + fact_start);
        }
        Relevance.Stop();
    });


    // Hide 2nd set of labels in case "irrelevant" was clicked -> also hide
    // 3rd set if it's visible. Unseelect all choices
    //$irr.on("click", function(){
    //    // Hide only if visible
    //    if ($facts.is(":visible")) {
    //        $facts.hide();
    //        if($opinions.is(":visible"))
    //        {
    //            $opinions.hide();
    //            $(".third_label_set, .second_label_set").prop("checked", false);
    //        }
    //    }
    //    Relevance.Stop();
    //});

    // Show 3rd set of labels
    //$non_fact.click(function () {
    $non_fact.bind("click", function () {
        hide_error($("#fac_error"));
        // .show() displays also these errors shown below, so we hide them
        hide_error($("#opi_error"));
        hide_error($("#opi_conf_error"));
        // Show only if div not visible
        if (!$opinions.is(":visible")) {
            $opinions.show();
        }
        if ($non_fact.hasClass(HAS_BEEN_CLICKED)) {
            opinion_start = Opinion.GetCurrentTime();
            console.log("opinion offset: " + opinion_start);
            $non_fact.removeClass(HAS_BEEN_CLICKED);
        }
        Fact.Stop();
    });

    // Hide 3rd set of labels
    //$fact.click(function(){
    $fact.bind("click", function(){
        hide_error($("#fac_error"));
        // Hide only if visible
        if ($opinions.is(":visible")) {
            $opinions.hide();
            $(".third_label_set").prop("checked", false);
        }
        Fact.Stop();
    });

    // Stop counter for 3rd set of labels
    //$("#positive, #negative").click(function() {
    $("#positive, #negative").bind("click", function() {
        hide_error($("#opi_error"));
        Opinion.Stop();
    });

    // Stop confidence button counter for 1st set of labels
    //$("#rel_low, #rel_high").click(function() {
    $("#rel_low, #rel_high").bind("click", function() {
        hide_error($("#rel_conf_error"));
        Con_relevance.Stop();
    });

    // Stop confidence button counter for 2nd set of labels
    //$("#fact_low, #fact_high").click(function() {
    $("#fact_low, #fact_high").bind("click", function() {
        hide_error($("#fac_conf_error"));
        Con_fact.Stop();
    });

    // Stop confidence button counter for 3rd set of labels
    //$("#opi_low, #opi_high").click(function() {
    $("#opi_low, #opi_high").bind("click", function() {
        hide_error($("#opi_conf_error"));
        Con_opinion.Stop();
    });

    // Change the styling of the confidence buttons on click
    $(".confidence").click(function() {
        $(this).toggleClass("chosen_confidence") ;
    });

    var $current_total = $("#current_total");
    var $current_session = $("#current_session");
    var $total_total = $("#total_total");
    var $total_session = $("#total_session");


    // Whenever the value of the hidden <div> blocks changes, update the
    // progress bars

    // Progress bar for total amount of labeled tweets
    $current_total.bind("currenttotalchanged", function(evt) {
        updateCurrentTotalBar($(this).text());
    });
    $total_total.bind("totaltotalchanged", function(evt) {
        updateTotalTotalBar($(this).text());
    });

    // Progress bar for total amount of tweets labeled in session
    $current_session.bind("currentsessionchanged", function(evt) {
        updateSessionCurrentBar($(this).text());
    });

    $total_session.bind("totalsessionchanged", function(evt) {
        updateSessionTotalBar($(this).text());
    });

    // Update textual representation of progress whenever the bars are updated
    $("#total").progressbar({
        change: function() {
            update_textual_representation_in_progress_bar("#total");
      }
    });
    $("#session").progressbar({
        change: function() {
            update_textual_representation_in_progress_bar("#session");
      }
    });

    // Set textual representation of initial progress bars because the %
    // isn't shown automatically, so do it manually
    update_textual_representation_in_progress_bar("#total");
    update_textual_representation_in_progress_bar("#session");

    // Get the current value of the hidden div and update the progress bar
    // with it
    changeTotalTotal("#total_total", $total_total.text());
    changeTotalSession("#total_session", $total_session.text())
    changeCurrentTotal("#current_total", $current_total.text());
    changeCurrentSession("#current_session", $current_session.text());

    // Disable NEXT/PREVIOUS according to what the server said
    $prev = $("#previous_tweet");
    $next = $("#next_tweet");
    //alert("NEXT: " + $next.html() + "? " + ($next.html() == "False"));
    // Disable NEXT if there's no next tweet
    if ($next.html() == "False") {
        $("#next_div").addClass("ctrl_btn_disabled");
        $("#next_tweet").html("False");
    }
    else {
        $("#next_div").removeClass("ctrl_btn_disabled");
        $("#next_tweet").html("False");
    }
    // Disable PREVIOUS if there's no next tweet
    if ($prev.html() == "False") {
        $("#previous_div").addClass("ctrl_btn_disabled");
        $("#previous_tweet").html("False");
    }
    else {
        $("#previous_div").removeClass("ctrl_btn_disabled");
        $("#previous_tweet").html("True");
    }

    // When refreshing the page, make sure GUI stays in a valid state, also
    // for group "L" when tweets to be annotated in session exceeds
    // TWEET_LIMIT
    // Show the popup if the DOM element exists
    if($("#abort_session:contains('True')").length > 0) {
        alert("anno is part of 'L' and popup should be shown");
        var $el = $("#session_finished");
        var msg = "<p> Dear annotator,</p>";
            msg += "<p>now you have completed annotating tweets in a" +
                " supervised" +
                " environment. <b>There are still some tweets left to" +
                " annotate" +
                " for you</b>, but you can continue at your own pace from" +
                " your" +
                " own computer.</p> <p>In case of any problems, please contact" +
                " us.</p>"
        show_popup($el, msg);
        // Disable "Pause" because otherwise all other buttons could be
        // enabled again when clicking "Continue"; also disable "Submit"
        $("#pause").prop("disabled", true);
        $("#submit").prop("disabled", true);
    }

});

// Hide the respective error message but preserve the space
function hide_error($el) {
    $el.next().css('visibility','hidden');
}

// Shows a specific error message for an element
function show_error($el, msg) {
    $el.next().text(msg);
    $el.next().css('visibility','visible');
}

// Change the value of the hidden div and trigger an event that updates the
// respective progress bar value
function changeTotalTotal(selector, val) {
    $(selector).html(val);
    $(selector).triggerHandler('totaltotalchanged');
}

function changeCurrentTotal(selector, val) {
    $(selector).html(val);
    $(selector).triggerHandler('currenttotalchanged');
}

function changeTotalSession(selector, val) {
    $(selector).html(val);
    $(selector).triggerHandler('totalsessionchanged');
}

function changeCurrentSession(selector, val) {
    $(selector).html(val);
    $(selector).triggerHandler('currentsessionchanged');
}

function start_timers() {
    Relevance.Start();
    Opinion.Start();
    Fact.Start();
    Con_opinion.Start();
    Con_relevance.Start();
    Con_fact.Start();
}


// Hide all error messages, i.e. the labels inside the error divs
function hide_error_messages() {
    $("#rel_error").next().css('visibility','hidden');
    $("#rel_conf_error").next().css('visibility','hidden');
    $("#opi_error").next().css('visibility','hidden');
    $("#opi_conf_error").next().css('visibility','hidden');
    $("#session_finished").next().css('visibility','hidden');
    $("#fac_error").next().css('visibility','hidden');
    $("#fac_conf_error").next().css('visibility','hidden');
}


// ##########
// Loading screen
//http://stackoverflow.com/questions/68485/how-to-show-loading-spinner-in-jquery
$(document).ajaxStart(function() {
  $("#load_screen").show();
});

$(document).ajaxStop(function() {
  $("#load_screen").hide();
  //$("#st-tree-container").show();
});


function pause_anno(ev) {
    // Start time if "Continue" is clicked
    if (p_state == 1)
    {
        $(ev.target).attr("value", "Pause");
        p_state = 0;
        unfreeze_ui();
        resume_timers()
    }
    else // "Pause" is clicked
    {
        freeze_ui();
        stop_all_timers();
        $(ev.target).attr("value", "Continue");
        p_state = 1;
    }
}


function send_data(event) {
    // Submit button was pushed -> send entered data back to server.
    // Prevent default behavior of submit button, i.e. sending POST
    // because we do it manually
    event.preventDefault();
    // TODO: show loading screen
    var data = fetch_data();
    var csrftoken = getCookie('csrftoken');
    // Send only data if all necessary fields were filled in
    if (Object.keys(data).length > 0) {
        stop_all_timers();
        // TODO: remove next linne + setTimeout
        $("#load_screen").show();
        $("#tweet_text_span").hide();
        // Commented code waits 3s before displaying next tweet
        //setTimeout(function() {
        //$.ajax({
        //    type: "POST",
        //    dataType: "json",
        //    async: true,
        //    data: {
        //        // Without stringify the JS object isn't formatted as dict and
        //        // can't be parsed by Python
        //        data: JSON.stringify(data),
        //        csrfmiddlewaretoken: csrftoken
        //    },
        //    success: function (json) {
        //        reload_contents(json);
        //        // Enable previous button after submitting a tweet
        //        $("#previous_div").removeClass("ctrl_btn_disabled");
        //        $("#previous_tweet").html("True");
        //    },
        //    error: function (jqXHR, textStatus, errorThrown) {
        //        var err = JSON.parse(jqXHR.responseText);
        //        alert(err.error);
        //    }
        //});
        //    }, 3000); // End setTimeout
        $.ajax({
            type: "POST",
            dataType: "json",
            async: true,
            data: {
                // Without stringify the JS object isn't formatted as dict and
                // can't be parsed by Python
                data: JSON.stringify(data),
                csrfmiddlewaretoken: csrftoken
            },
            success: function (json) {
                reload_contents(json);
                // Enable previous button after submitting a tweet
                $("#previous_div").removeClass("ctrl_btn_disabled");
                $("#previous_tweet").html("True");
            },
            error: function (jqXHR, textStatus, errorThrown) {
                var err = JSON.parse(jqXHR.responseText);
                alert(err.error);
            }
        });

    }
}


function next_tweet(event) {
    // Next button was pushed -> send entered data back to server.
    // Prevent default behavior of submit button, i.e. sending POST
    // because we do it manually
    event.preventDefault();
    console.log("client clicked next");
    // TODO: show loading screen
    var data = {};
    // This entry indicates the annotator wants to go to the next tweet
    data["NEXT_TWEET"] = null;
    data["tweet_id"] = $("#tweet_id").text();
    var csrftoken = getCookie('csrftoken');
    $("#load_screen").show();
    $("#tweet_text_span").hide();
    // Send only data if all necessary fields were filled in
    stop_all_timers();
    $.ajax({
        type: "POST",
        dataType: "json",
        async: true,
        data: {
            // Without stringify the JS object isn't formatted as dict and
            // can't be parsed by Python
            data: JSON.stringify(data),
            csrfmiddlewaretoken: csrftoken
        },
        success: function (json) {
            //console.log("next tweet response: " + json);
            //console.log("length: " + Object.keys(json).length);
            //$.showDict(json);
            // > 1 because always "has_next: true/false" will be sent anyway
            if (Object.keys(json).length > 1) {

                reload_contents_next_prev(json);
                var $prev = $("#previous_div");
                // If I could click on "next", I can now click on "previous"
                $prev.removeClass("ctrl_btn_disabled");
                $("#previous_tweet").html("True");
            }
            else {
                // Disable "next"
                var $next = $("#next_div");
                //$next.prop("disabled", true);
                $next.addClass("ctrl_btn_disabled");
                $("#next_tweet").html("False");
                console.log("Empty tweet was returned by pressing 'next' ->" +
                    " disable button");
            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
            alert(errorThrown);
        }
    });
}


function previous_tweet(event) {
    // Previous button was pushed -> send entered data back to server.
    // Prevent default behavior of submit button, i.e. sending POST
    // because we do it manually
    event.preventDefault();
    console.log("client clicked previous");
    // TODO: show loading screen
    var data = {};
    // This entry indicates the annotator wants to go to the previous tweet
    data["PREVIOUS_TWEET"] = null;
    data["tweet_id"] = $("#tweet_id").text();
    var csrftoken = getCookie('csrftoken');
    // Send only data if all necessary fields were filled in
    stop_all_timers();
    $.ajax({
        type: "POST",
        dataType: "json",
        async: true,
        data: {
            // Without stringify the JS object isn't formatted as dict and
            // can't be parsed by Python
            data: JSON.stringify(data),
            csrfmiddlewaretoken: csrftoken
        },
        success: function (json) {
            console.log(json);
            if (Object.keys(json).length > 0) {
                reload_contents_next_prev(json);
                var $next = $("#next_div");
                // If I could click on "previous", I can now click on "next"
                $next.removeClass("ctrl_btn_disabled");
                $("#next_tweet").html("True");
                // Enable pause
                $("#pause").prop("disabled", false);
            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
            alert(errorThrown);
        }
    });
}


//*******************
// Utility functions
//*******************
/**
 Function updates the elements in the document with new content delivered by
 the server and resets all necessary elements.

 @param res: Response object from server which is JSON-encoded
 **/
function reload_contents (res) {
    update_counters_and_tweet(res);
    // Disable/enable next/previous
    var $next = $("#next_div");
    //alert("has next in reload_contents: " + res.has_next + "? " + res.has_next == false);
    // The last annotated tweet was already displayed -> disable
    if (res.has_next == false) {
        $next.addClass("ctrl_btn_disabled");
        $("#next_tweet").html("False");
    }
    else {
        $next.removeClass("ctrl_btn_disabled");
        $("#next_tweet").html("True");
    }
    reset_gui();
    if (res.hasOwnProperty("SESSION_FINISHED"))
    {
        var $el = $("#session_finished");
        var msg = "<p> Dear " + res.username + ", </p>";
        msg += "<p>you have completed this annotation session. Thank you" +
            " very " +
            "much for your contribution! Please sign out, unless you want to" +
            " edit some of the labels you assigned in this session.</p> " +
            "<p> Remember that there" +
            " will be more annotation sessions in the future depending on" +
            " your annotation group.</p><p>Stefan</p>";
        // Annotator belongs to group "L" and can continue labeling after
        // logout because only TWEET_LIMIT tweets remain
        if (res.hasOwnProperty("can_continue")) {
            $("#abort_session").text("True");
            msg = "<p> Dear " + res.username + ", </p>";
            msg += "<p>now you have completed annotating tweets in a" +
                " supervised" +
                " environment. <b>There are still some tweets left to" +
                " annotate" +
                " for you</b>, but you can continue at your own pace from" +
                " your" +
                " own computer.</p> <p>In case of any problems, please contact" +
                " us.</p>"
        }

        show_popup($el, msg);
        update_prev_next(res);
        // Disable "Pause" because otherwise all other buttons could be
        // enabled again when clicking "Continue"; also disable "Submit"
        $("#pause").prop("disabled", true);
        $("#submit").prop("disabled", true);
    }
}


/**
 * Reloads the previous/next tweet with the stored data from the server
 *
 * @param res: Response from server
 */
function reload_contents_next_prev (res) {
    // Works only if the relevance_label is identical with the button value!
    console.log("returned relevance_label: " + res.relevance_label);
    // Button that was selected, either Relevant or Irrelevant
    var $rel_btn = $("input[type='radio'][name='relevance'][value=" + res.relevance_label + "]");
    var $rel_btns = $("input[type='radio'][name='relevance']");
    var $rel_conf_btn = $("input[type='radio'][name='toggle_rel'][value=" + res.confidence_relevance + "]");
    var $rel_conf_btns = $("input[type='radio'][name='toggle_rel']");
    reset_gui();
    // Enable all buttons
    unfreeze_ui();
    // Disable "Next" if no more tweet can be loaded from the DB
    update_prev_next(res);

    // Update the page with new data from the DB
    // Tweet text
    update_counters_and_tweet(res);

    // Handle fact buttons and times
    // Relevance buttons
    $rel_btns.each(function () {
        if ($rel_btn.val() == $(this).val()){
            console.log("Anno selected earlier rel label: " + $(this).val());
            $(this).prop("checked", true);
        }
    });
    // Relevance confidence
    $rel_conf_btns.each(function () {
        if ($rel_conf_btn.val() == $(this).val()){
            console.log("Anno selected earlier rel conf: " + $(this).val());
            $(this).prop("checked", true);
        }
    });
    // Store times from server
    // TODO: uncomment these next 2 lines for previous behavior
    //relevance_offset = res.relevance_time;
    //confidence_relevance_offset = res.confidence_relevance_time;
    // No offset initially - we start initially new
    old_relevance_offset = res.relevance_time
    old_confidence_relevance_offset = res.confidence_relevance_time;
    console.log("previous time for choosing rel label: " + old_relevance_offset);
    console.log("previous time for choosing rel conf: " + old_confidence_relevance_offset);

    // Fact buttons
    // Did the user assign the 2nd set of labels? - has to be conditional
    // because when clicking "next", the set of labels might not exist, so they
    // shouldn't be shown
    console.log("has fact? " + res.hasOwnProperty("fact_label"));
    if (res.hasOwnProperty("fact_label")) {
        var $fac_btn = $("input[type='radio'][name='fact'][value=" + res.fact_label + "]");
        var $fac_btns = $("input[type='radio'][name='fact']");
        var $fac_conf_btn = $("input[type='radio'][name='toggle_fac'][value=" + res.confidence_fact + "]");
        var $fac_conf_btns = $("input[type='radio'][name='toggle_fac']");
        var $facts = $("#fact_div");
        $fac_btns.each(function () {
            if ($fac_btn.val() == $(this).val()) {
                console.log("Anno selected earlier fac label: " + $(this).val());
                $(this).prop("checked", true);
            }
        });
        // Fact confidence
        $fac_conf_btns.each(function () {
            if ($fac_conf_btn.val() == $(this).val()) {
                console.log("Anno selected earlier fact conf: " + $(this).val());
                $(this).prop("checked", true);
            }
        });
        $facts.show();
        old_fact_offset = res.fact_time;
        old_confidence_fact_offset = res.confidence_fact_time;
        console.log("previous time for choosing fac label: " + old_fact_offset);
        console.log("previous time for choosing fac conf: " + old_confidence_fact_offset);
    }
    console.log("has opinion? " +  res.hasOwnProperty("opinion_label"));

    // Did the user assign the 3rd set of labels?
    if (res.hasOwnProperty("opinion_label")) {
        var $opi_btn = $("input[type='radio'][name='opinion'][value=" + res.opinion_label + "]");
        var $opi_btns = $("input[type='radio'][name='opinion']");
        var $opi_conf_btn = $("input[type='radio'][name='toggle_opi'][value=" + res.confidence_opinion+ "]");
        var $opi_conf_btns = $("input[type='radio'][name='toggle_opi']");
        var $opinions = $("#opinion_div");
        // Opinion buttons
        $opi_btns.each(function () {
        if ($opi_btn.val() == $(this).val()){
            $(this).prop("checked", true);
            console.log("Anno selected earlier opi label: " + $(this).val());
        }
        });
        // Opinion confidence
        $opi_conf_btns.each(function () {
            if ($opi_conf_btn.val() == $(this).val()){
                console.log("Anno selected earlier opi conf: " + $(this).val());
                $(this).prop("checked", true);
            }
        });
        // Display opinion related buttons
        $opinions.show();
        old_opinion_offset = res.opinion_time;
        old_confidence_opinion_offset = res.confidence_opinion_time;
        console.log("previous time for choosing opi label: " + old_opinion_offset);
        console.log("previous time for choosing opi conf: " + old_confidence_opinion_offset);
    }
}

/**
 * Calculates the annotation time.
 *
 * @param t: Timer object.
 * @param diff: Milliseconds that should be subtracted, e.g. opinion start time
 * @param off: Offset of time.
 *
 * Returns
 * -------
 * Time in seconds
 */
function compute_time(t, diff, off) {
    if (diff === undefined) diff = 0;
    // If the time was used, calculate time accordingly
    if (t.GetElapsedTime() > 0)
        return (t.GetElapsedTime() - diff) / 1000 + off;
    else
        // If annotator just changed some other labels during "previous"/"next",
        // the timer wasn't used,
        // so only the previous time (from the DB) should be considered
        return off;
}

/**
 * Collect the inputs from the annotator and store them in a dictionary
 * @returns: Data (dictionary) to be sent to client with the respective key
 * value pairs.
 */
function fetch_data(){
    // Variables in case user navigates to previous/next tweet
    var isValid = true;
    var msg = "";
    var data = {};
    // Get 1st set of labels
    var $relevance = $("input[type='radio'][name='relevance']");
    // Error message for relevance button
    var $rel_error = $("#rel_error");

    // if($('#radio_button').is(':checked')) not working in IE:
    //http://stackoverflow.com/questions/2272507/find-out-if-radio-button-is-checked-with-jquery
    // Check that 1st label was chosen
    if ($relevance.is(":checked")) {
        //$rel_error.empty();
        hide_error($rel_error);
        data["relevance"] = $("input[type='radio'][name='relevance']:checked").val();
        data["relevance_time"] = compute_time(Relevance, 0, relevance_offset) + old_relevance_offset;
        console.log("relevance time: " + (Relevance.GetElapsedTime() / 1000.0));
        console.log("rel time from previous annotation: " + old_relevance_offset);
        console.log("relevance time total: " + (data["relevance_time"]));
    } else {
        //remove_status_messages();
        msg = "Please, choose a label.";
        //show_in_message_box($rel_error, msg);
        show_error($rel_error, msg);
        isValid = false;
    }
    // Check that confidence was chosen
    var $conf_rel = $("input[type='radio'][name='toggle_rel']");
    var $conf_rel_error = $("#rel_conf_error");
    if ($conf_rel.is(":checked")) {
        //$conf_rel_error.empty();
        hide_error($conf_rel_error);
        data["confidence_relevance_time"] = compute_time(Con_relevance, 0, confidence_relevance_offset) + old_confidence_relevance_offset;
        data["confidence_relevance"] = $("input[type='radio'][name='toggle_rel']:checked").val();
        console.log("relevance conf time: " + (Con_relevance.GetElapsedTime() / 1000.0));
        console.log("rel conf time from previous annotation: " + old_confidence_relevance_offset);
        console.log("relevance conf time total: " + (data["confidence_relevance_time"]));
    } else {
        //remove_status_messages();
        msg = "Please, choose a label";
        //show_in_message_box($conf_rel_error, msg);
        show_error($conf_rel_error, msg);
        isValid = false;
    }
    // Check 2nd set of labels
    var $facts = $("input[type='radio'][name='fact']");
    var $fac_error = $("#fac_error");
    // Make error labels invisible because due to show() they'd be visible
    hide_error($fac_error);
    if ($facts.is(":checked")) {
        hide_error($fac_error);
        data["fact"] = $("input[type='radio'][name='fact']:checked").val();
        console.log("how much time passed before 2nd label set was shown? " + fact_start);
        data["fact_time"] = compute_time(Fact, fact_start, fact_offset) + old_fact_offset;
        console.log("fact time: " + ((Fact.GetElapsedTime() - fact_start) / 1000));
        console.log("fac time from previous annotation: " + old_fact_offset);
        console.log("fact time total: " + (data["fact_time"]));
    } else {
        //remove_status_messages();
        msg = "Please, choose a label";
        //show_in_message_box($fac_error, msg);
        show_error($fac_error, msg);
        isValid = false;
    }
    // Check 2nd set of confidence buttons
    var $conf_fac = $("input[type='radio'][name='toggle_fac']");
    var $conf_fac_error = $("#fac_conf_error");
    // Make error labels invisible because due to show() they'd be visible
    hide_error($conf_fac_error);
    if ($conf_fac.is(":checked")) {
        //$fact_opi_error.empty();
        hide_error($conf_fac_error);
        data["confidence_fact_time"] = compute_time(Con_fact, fact_start, confidence_fact_offset) + old_confidence_fact_offset;
        data["confidence_fact"] = $("input[type='radio'][name='toggle_fac']:checked").val();
        console.log("fact confidence time: " + ((Con_fact.GetElapsedTime() - fact_start) / 1000));
        console.log("fact conf time from previous annotation: " + old_confidence_fact_offset);
        console.log("fact confidence time total: " + (data["confidence_fact_time"]));
    } else {
        //remove_status_messages();
        msg = "Please, choose a label";
        //show_in_message_box($fac_error, msg);
        show_error($conf_fac_error, msg);
        isValid = false;
    }
    // Only if "Non-factual" is checked, the 3rd set of labels was used
    if ($("#non_factual").is(":checked")) {
        // Check 3rd set of labels
        var $opinions = $("input[type='radio'][name='opinion']");
        var $opi_error = $("#opi_error");
        if ($opinions.is(":checked")) {
            hide_error($opi_error);
            console.log("how much time passed before 2nd label set was shown? " + fact_start);
            console.log("how much time passed before 3rd label set was shown?" +
                " " + opinion_start);
            data["opinion"] = $("input[type='radio'][name='opinion']:checked").val();
            data["opinion_time"] = compute_time(Opinion, opinion_start, opinion_offset) + old_opinion_offset;
            console.log("opinion time: " + ((Opinion.GetElapsedTime() - opinion_start) / 1000));
            console.log("opi time from previous annotation: " + old_opinion_offset);
            console.log("opinion time total: " + (data["opinion_time"]));
        } else {
            //remove_status_messages();
            msg = "Please, choose a label";
            //show_in_message_box($opi_error, msg);
            show_error($opi_error, msg);
            isValid = false;
        }
        // Check 3rdset of confidence buttons
        var $conf_opi = $("input[type='radio'][name='toggle_opi']");
        var $conf_opi_error = $("#opi_conf_error");
        if ($conf_opi.is(":checked")) {
            hide_error($conf_opi_error);
            data["confidence_opinion_time"] = compute_time(Con_opinion, opinion_start, confidence_opinion_offset) + old_confidence_opinion_offset;
            data["confidence_opinion"] = $("input[type='radio'][name='toggle_opi']:checked").val();
            console.log("opinion confidence time: " + ((Con_opinion.GetElapsedTime() - opinion_start) / 1000));
            console.log("opi conf time from previous annotation: " + old_confidence_opinion_offset);
            console.log("opinion confidence time total: " + (data["confidence_opinion_time"]));
        } else {
            //remove_status_messages();
            msg = "Please, choose a label";
            //show_in_message_box($opi_error, msg);
            show_error($conf_opi_error, msg);
            isValid = false;
        }
    }
    if (isValid)
    {
        var now = new Date();
        // Store date in UTC time and not local time
        data["annotation_timestamp"] = now.toUTCString();
        // Add tweet ID
        data["tweet_id"] = $("#tweet_id").text();
        console.log("Annotation information sent about tweet " + data["tweet_id"]);
        // Reset the offsets of the timers
        opinion_start = 0;
        fact_start = 0;
        return data;
    }
    else{
        data = {};
        return data;
    }
}


// Display a dictionary's content
$.showDict = function(data){
    for (var key in data) {
        if (data.hasOwnProperty(key)) { // this will check if key is owned by data object and not by any of it's ancestors
            alert(key + ': ' + data[key]); // this will show each key with it's value
        }
    }
};


/**
 * Enables/disables the previous and next button.
 * @param res: Response from server
 */
function update_prev_next(res) {
    var $next = $("#next_div");
    var $prev = $("#previous_div");
    console.log("next: " + res.has_next);
    // The last annotated tweet was already displayed -> disable
    if (res.has_next == false) {
        $next.addClass("ctrl_btn_disabled");
        $("#next_tweet").html("False");
    }
    else {
        $next.removeClass("ctrl_btn_disabled");
        $("#next_tweet").html("True");
    }
    // Disable "Previous" if annotator arrived at first tweet of seesion.
    // The last annotated tweet was already displayed -> disable
    if (res.has_previous == false) {
        $prev.addClass("ctrl_btn_disabled");
        $("#previous_tweet").html("False");
    }
    else {
        $prev.removeClass("ctrl_btn_disabled");
        $("#previous_tweet").html("True");
    }
    // If annotator already labeled all tweets, when going back, the GUI is
    // frozen
    //unfreeze_ui();
}


/**
 * Updates the progress counters and the displayed tweet message
 *
 * @param res: Response from server
 */
function update_counters_and_tweet(res) {
    // Update the page with new data from the DB
    // Tweet text
    //$("#tweet_text").hide().html(res.tweet).slideDown('slow');
    $("#tweet_text_span").hide().html(res.tweet).slideDown('slow');
    // Counters at the top
    $("#tweet_id").text(res.tweet_id);
    $("#total_prog").html("Total progress: " + res.current_prog + " / " + res.total_prog);
    $("#session_prog").html("Session progress: " + res.current_sess + " / " + res.total_sess);
    //$("#session").progressbar(
        // Current value
        //{"value": parseInt(res.current_sess, 10)}),
    // Initialize progress bars
    console.log("total max progress: " + parseInt(res.total_prog, 10));
    console.log("session max progress: " + parseInt(res.total_sess, 10));
    //changeHtml("#current_total", res.current_prog);

    // Get the current value of the hidden div and update the progress bar
    // with it
    //changeTotalTotal("#total_total", res.total_prog);
    //changeTotalSession("#total_session", res.total_sess);
    changeCurrentTotal("#current_total", res.current_prog);
    changeCurrentSession("#current_session", res.current_sess);
}


// Get CSRF token
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


// Stop all timers
function stop_all_timers() {
    stop_timer(Relevance);
    stop_timer(Opinion);
    stop_timer(Fact);
    stop_timer(Con_fact);
    stop_timer(Con_relevance);
    stop_timer(Con_opinion);
}


// Stops the specified timer object.
function stop_timer(timer) {
    if (timer.IsRunning()) {timer.Pause();}
}


/**
 * Resume all timers where no choice has been made yet
 */
function resume_timers() {
    Relevance.Resume();
    Con_relevance.Resume();
    Fact.Resume();
    Con_fact.Resume();
    Opinion.Resume();
    Con_opinion.Resume();
}


// Reset all values after submitting the data
function reset_gui(){
    // Uncheck buttons
    var $rel = $("input[type='radio'][name='relevance']");
    var $opi = $("input[type='radio'][name='opinion']");
    var $fac = $("input[type='radio'][name='fact']");
    var $rel_conf = $("input[type='radio'][name='toggle_rel']");
    var $fac_conf = $("input[type='radio'][name='toggle_fac']");
    var $opi_conf = $("input[type='radio'][name='toggle_opi']");
    var $facts = $("#fact_div");
    var $opinions = $("#opinion_div");
    var $non_fact = $("#non_factual");
    var $relevance_buttons = $("#relevance_button_div");
    // Indicates whether the button has been clicked for the first time or not
    $relevance_buttons.addClass(HAS_BEEN_CLICKED);
    $non_fact.addClass(HAS_BEEN_CLICKED);
    $rel.prop("checked", false);
    $opi.prop("checked", false);
    $fac.prop("checked", false);
    $rel_conf.prop("checked", false);
    $opi_conf.prop("checked", false);
    $fac_conf.prop("checked", false);
    // Hide 2nd set of labels
    $facts.hide();
    // Hide 3rd set of labels
    $opinions.hide();
    reset_times();
}


// Reset all timers
function reset_times() {
    relevance_offset = 0;
    old_relevance_offset = 0;
    opinion_offset = 0;
    old_opinion_offset = 0;
    fact_offset = 0;
    old_fact_offset = 0;
    confidence_relevance_offset = 0;
    old_confidence_relevance_offset = 0;
    confidence_opinion_offset = 0;
    old_confidence_opinion_offset = 0;
    confidence_fact_offset = 0;
    old_confidence_fact_offset = 0;
    opinion_start = 0;
    fact_start = 0;
    reset_timers();
    start_timers();
}


// Reset timers to start from 0 again
function reset_timers() {
    Relevance.ResetTimer();
    Opinion.ResetTimer();
    Fact.ResetTimer();
    Con_relevance.ResetTimer();
    Con_opinion.ResetTimer();
    Con_fact.ResetTimer();
}


// Disable all clickable elements in GUI
function freeze_ui() {
    //var $opinion = $("input[type='radio'][name='opinion']");
    //var $fact = $("input[type='radio'][name='fact']");
    //var $relevance = $("input[type='radio'][name='relevance']");
    //var $opi_conf = $("input[type='radio'][name='toggle_opi']");
    //var $fac_conf = $("input[type='radio'][name='toggle_fac']");
    //var $rel_conf = $("input[type='radio'][name='toggle_rel']");
    //var $buttons = $("#anno_buttons");
    var $submit = $("#submit");
    //var $next = $("#next");
    //var $previous = $("#previous");
    // Select all input elements inside the annotation button div
    var buttons = $("#anno_buttons :input");
    buttons.disable();
    $submit.prop("disabled", true);
    //$next.prop("disabled", true);
    //$previous.prop("disabled", true);
    $("#previous_div,#next_div").addClass("ctrl_btn_disabled");
    $("#next_tweet,#previous_tweet").html("False");
}

$.prototype.enable = function () {
    $.each(this, function (index, el) {
        $(el).prop("disabled", false);
    });
}

$.prototype.disable = function () {
    $.each(this, function (index, el) {
        $(el).prop("disabled", true);
    });
}

// Enable all clickable elements in GUI
function unfreeze_ui() {
    var buttons = $("#anno_buttons :input");
    //var $opinion = $("input[type='radio'][name='opinion']");
    //var $fact = $("input[type='radio'][name='fact']");
    //var $relevance = $("input[type='radio'][name='relevance']");
    //var $opi_conf = $("input[type='radio'][name='toggle_opi']");
    //var $fac_conf = $("input[type='radio'][name='toggle_fac']");
    //var $rel_conf = $("input[type='radio'][name='toggle_rel']");
    var $submit = $("#submit");
    var $next = $("#next");
    var $previous = $("#previous");
    buttons.enable();
    //$fact.prop("disabled", false);
    //$fac_conf.prop("disabled", false);
    //$opinion.enable();
    //$opi_conf.prop("disabled", false);
    //$relevance.prop("disabled", false);
    //$rel_conf.prop("disabled", false);
    $submit.prop("disabled", false);
    //$next.prop("disabled", false);
    //$previous.prop("disabled", false);
    $("#previous_div,#next_div").removeClass("ctrl_btn_disabled");
    $("#next_tweet,#previous_tweet").html("True");
}


function updateCurrentTotalBar(value) {
    $("#total").progressbar("option", "value", parseInt(value, 10));
}

function updateTotalTotalBar(value) {
    $("#total").progressbar({
        max: parseInt(value, 10)
    });
}

function updateSessionCurrentBar(value) {
    $("#session").progressbar("option", "value", parseInt(value, 10));
}

function updateSessionTotalBar(value) {
    $("#session").progressbar({
        max: parseInt(value, 10)
    });
}

// Logs a user out and sends him/her back to the index page
function logout(event) {
    event.preventDefault();
    // Extract the username from the text
    var $user = $("#logout").next().children("span").first().html();
    var csrftoken = getCookie('csrftoken');
    $.ajax({
        type: "GET",
        url: "/" + $user + "/logout/",
        dataType: "json",
        async: true,
        data: {
            csrftoken: csrftoken
        },
        success: function (json) {
            if (json.url) {
                //alert("URL To forward to:" + json.url);
                window.location.replace(json.url);
            }
            else {
                // Forward to index page
                window.location.replace("/");
            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
            alert("Error: " + errorThrown);
        }
    });
}



/**
 * Displays a popup window with a specific message.
 * @param $el: Selected DOM element where the message should be added.
 * @param msg: The message to be displayed.
 */
function show_popup($el, msg) {
    $el.html(msg);
    $el.dialog({
        title: "Annotation session finished",
        width: 640,
        minWidth: 640,
        height: 480,
        minHeight: 480,
        modal: true,
        buttons: {
            Close: function () {
                $(this).dialog("close");
            }
        }
    });
}


/**
 *
 * @param bar: String of the identifier of the progress bar
 */
function update_textual_representation_in_progress_bar(bar) {
        // Set textual representation of initial progress bars because the %
    // isn't shown automatically, so do it manually
    var val = parseInt($(bar).progressbar( "value" ), 10);
    // Compute percentage: new value / max value * 100
    val = 100.0 * val / $(bar).progressbar("option", "max");
    val = parseInt(val, 10);
    if(bar.match("session$")){
        $(bar + " .inner_text").text( "#Annotated tweets in session: " + val + "%" );
    }
    else {
        $(bar + " .inner_text").text( "#Annotated tweets overall: " + val + "%" );
    }

    //alert("set total bar initially to: " + val + "%");

    //val = parseInt($("#session").progressbar( "value" ), 10);
    //// Compute percentage: new value / max value * 100
    //val = 100.0 * val / $("#session").progressbar("option", "max");
    //val = parseInt(val, 10);
    ////$("#session_progress").text( "Current Progress: " + val + "%" );
    //$("#session .inner_text").text( "#Annotated tweets in session: " + val + "%" );
    //alert("set session bar initially to: " + val + "%");

}