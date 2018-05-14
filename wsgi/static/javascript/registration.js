/**
 * Created by fensta on 24.08.2015.
 */
// For validation the validation plugin is used
// http://bassistance.de/jquery-plugins/jquery-plugin-validation/
// http://docs.jquery.com/Plugins/Validation/
// http://docs.jquery.com/Plugins/Validation/validate#toptions
$(document).ready(function() {
    add_tooltips();

    // Add a custom function for validating the user name
    jQuery.validator.addMethod(
    // Function name
    "isValidName",
    // Actual validation function
    function(value, element) {
        return isValidUserName(value);
    },
    // Error message
    "Your name contains invalid characters. A valid user name may contain" +
    " letters, digits or '_'. Please, double-check your input."
    );

    // Add a custom function for validating the password
    jQuery.validator.addMethod(
    // Function name
    "isValidPw",
    // Actual validation function
    function(value, element) {
        return isValidPassword(value);
    },
    // Error message
    "Your password contains invalid characters. A valid password may contain" +
    " any combination of letters, digits and other symbols, but" +
    " only English letters are accepted. Please, double-check your input."
    );

    $("#data").validate({
        //onsubmit: true,
        onkeyup: false, //turn off auto validate whilst typing
        //onclick: true,
        //onfocusout: true,
        // Don't validate fields that are hidden or have the class "ignore"
        ignore: ".ignore :hidden",
        rules: {
            email: {
                required: true,
                email: true,
                remote: {
                    url: "register/validateEmail/",
                    data: {
                        email: function () {
                            return $("#email").val();
                        },
                        csrftoken: function () {
                            return getCookie('csrftoken');
                        }
                    }
                }
            },
            //username: {
            //    //isValidName: true,
            //    required: true
            //    // Send the entered user name to the server and check
            //    // whether it's available or already taken; CSRF token is
            //    // necessary too
            //    //remote: {
            //    //    url: "/register/validateUser/",
            //    //    data: {
            //    //        username: function(){
            //    //            return $("#username").val();
            //    //        },
            //    //        csrftoken: function() {
            //    //            return getCookie('csrftoken');
            //    //        }
            //    //    }
            //    //}
            //},
            password: {
                required: true,
                isValidPw: true
            },
            sex: {
              required: true
            },
            nation_list: {
                required: true
            },
            course: {
                required: true
            },
            level_list: {
                required: true
            },
            semester_list: {
                required: true
            },
            faculty_list: {
                required: true
            },
            //strategy_list: {
            //    required: true
            //},
            //annogroup_list: {
            //    required: true
            //}
        },
        // Placement of error messages per element
        errorPlacement: function(error, element) {
            // Place error messages for check boxes at the end of the line
            console.log("current element " + $(element).attr("id"));
            //if ($(element).hasClass("is_checkbox")) {
            //        console.log("insert error for checkbox " + $(element).attr("id"));
            //        //error.appendTo($(element).closest("div"));
            //        error.appendTo($(element).parent());
            //}
            //else {
            //    console.log("insert error after for " + $(element).attr("id"));
            //    error.insertAfter(element);
            //}
            if (element.is("input:radio")) {
                console.log("insert error for checkbox " + $(element).attr("id"));
                error.appendTo($(element).parent());
            }
            else {
                //console.log("insert error after for " + $(element).attr("id"));
                error.insertAfter(element);
            }
        },
        // Error messages for each <name>, but only the cases with special
        // messages need to be addressed, e.g. for a missing fields the
        // message "This field is required." is printed by default.
        messages: {
            //email: {
            //    //required: "Please, choose a user name.",
            //    remote: "Your email address does not exist in the DB. Either" +
            //    " use a different one or you have not been allowed to" +
            //    " participate yet or you are already registered."
            //},
            //username: {
            //    //required: "Please, choose a user name.",
            //    remote: "The username is already taken. Please, choose a" +
            //    " different one."
            //},
            //password: {
            //    required: "Please, enter a password."
            //},
            //sex: {
            //    required: "Please, select your gender."
            //},
            //nation_list: {
            //    required: "Please, choose your country of origin."
            //},
            //course: {
            //    required: "Please, enter your course of studies."
            //},
            //level_list: {
            //    required: "Please, specify your current position."
            //},
            //semester_list: {
            //    required: "Please, choose for how many semesters you have" +
            //    " studied in total."
            //},
            //faculty_list: {
            //    required: "Please, specify your faculty."
            //},
            //strategy_list: {
            //    required: "Please, specify the strategy you must use as" +
            //    " explained to you. If you don't know it, please ask."
            //},
            //annogroup_list: {
            //    required: "Please, specify the size of your dataset as" +
            //    " explained to you. If you don't know it, please ask."
            //}
        },
        // Submit after successful validation
        submitHandler: function(form) {
            console.log("entered data were valid - submit it");
            register();
        }
    });

    // Handle login/registration screen -> open respective tab
    $(".tab").click(function() {
        var $tab = $(this).attr('id');
        // User clicked on "Signup"
        if($tab == 'signup') {
            selectSignup();
        }
        else {
            selectLogin();
        }
    });

    // Change username according to email address
    $("#email").on("blur keypress keydown keyup", function(){

        $("#username").val($(this).val());
        //alert($("#email").val());
    });
});


// ############################################
// ############### Functions ##################
// ############################################

// Selects the "Signup" tab on the index page
function selectSignup() {
    // Handle login/registration screen
    $("#login").removeClass('select');
    $("#signup").addClass('select');
    $("#login_box").hide();
    $("#signup_box").show();
}


// Selects the "Login" tab on the index page
function selectLogin() {
    // Handle login/registration screen
    $("#signup").removeClass('select');
    $("#login").addClass('select');
    $("#login_box").show();
    $("#signup_box").hide();
}

// Validate username
function isValidUserName(str) {
//    regex: /^[A-Za-z\s`~!@#$%^&*()+={}|;:'",.<>\/?\\-]+$/
//NODE                     EXPLANATION
//--------------------------------------------------------------------------------
//  ^                        the beginning of the string
//--------------------------------------------------------------------------------
//  [A-Za-                   any character of: 'A' to 'Z', 'a' to 'z',
//  z\s`~!@#$%^&*()+={}|     whitespace (\n, \r, \t, \f, and " "), '`',
//  ;:'",.<>/?\\-]+          '~', '!', '@', '#', '$', '%', '^', '&',
//                           '*', '(', ')', '+', '=', '{', '}', '|',
//                           ';', ':', ''', '"', ',', '.', '<', '>',
//                           '/', '?', '\\', '-' (1 or more times
//                           (matching the most amount possible))
//--------------------------------------------------------------------------------
//  $                        before an optional \n, and the end of the
//                           string
    // valid user name contains upper/lower case letters, digits or underscore
    return /^[A-Za-z0-9\d=_.]@+[A-Za-z0-9\d=_.]$/.test(str);
}


// Any character is allowed, but only English letters and no "§"
function isValidPassword(str) {
    return /^[A-Za-z0-9\s`~!@#$%^&*()+={}|;:'",_.<>/?\\-]+$/.test(str);
}


// Add tooltip to every field
function add_tooltips() {
    $("#data").find("a.tooltip_text").each(function() {
        //alert("connect tooltip " + $(this).attr("id"));
        var $link = $(this);
        var res = getIdOfLastElement($link);
        res = "#" + res;
        //alert("of = " + res);
        $(this).tooltip({
            // Display tooltip on the right
            position: {
                of: res,
                my: 'left center',
                at: 'right center'
            },
            // Name of the class for styling purposes
            tooltipClass: "ui_tooltip"
        })
    });


    // Show the title attribute as a tooltip which is stored in a link when
    // hovering over the tooltip button
    // For each span in the form
    $("#data").find("span.question").each(function() {
        // If you hover over it
        $(this).hover(function(e) {
            // Select corresponding <a> which precedes <span .tooltip_next>
            var $link = $(e.target).prev(".tooltip_text");
            //alert("connect" + $link.attr("id"));
            // Open tooltip
            $link.tooltip('open');
        }, function(e){
            // Select corresponding <a> which precedes <span .tooltip_next>
            var $link = $(e.target).prev(".tooltip_text");
            //alert("connect" + $link.attr("id"));
            // Close tooltip
            $link.tooltip('close');
        });
    });
}

// Finds the type of the last element in a <p><\p> block
// Input: a_el - <a> element inside of a <p>
// Returns: DOM element - the last DOM element in the block.
function getTypeOfLastElement(a_el) {
    var $p = $(a_el).parent().children().last();
    //alert("type of last element:" + $p.prop("tagName"));
    // Next element is "Gender" -> add tooltip next to  tooltip
    if ($p.prop("tagName") == "BR")
    {
        //alert($(a_el).next().attr("id"));
        $p = $(a_el).next();
    }
    //alert("type of last element:" + $p.attr("id"));
    return $p;
}

// Input: a_el - <a> element inside of a <p>
// Returns: ID of last DOM element in that <p>.
function getIdOfLastElement(a_el) {
    var $el = getTypeOfLastElement(a_el);
    //alert("result of getlastid:" + $el.attr("id"));
    return $el.attr("id");
}

// Sends login data entered by a user to the server and forwards him/her to
// the next page
function login(event) {
    // Submit button was pushed -> send entered data back to server.
    // Prevent default behavior of submit button, i.e. sending POST
    // because we do it manually
    event.preventDefault();
    var data = fetch_data_login();
    var csrftoken = getCookie('csrftoken');
    // Send only data if all necessary fields were filled in
    if (Object.keys(data).length > 0) {
        $.ajax({
            type: "POST",
            //url: "/labeler/a/1/",
            dataType: "json",
            async: true,
            data: {
                // Without stringify the JS object isn't formatted as dict and
                // can't be parsed by Python
                data: JSON.stringify(data),
                csrfmiddlewaretoken: csrftoken
            },
            success: function (json) {
                // Pw/username incorrect
                if ("error" in json) {
                     var $error = $("#login_submit");
                    $error.next().remove();
                    // Remove current error message
                    var s = "<label class='error'>" + json.error + "</label>";
                    // Add new message
                    $(s).insertAfter($error);
                }
                else if ("message" in json) {
                    // 404 error -> forward to error URL
                    window.location.replace(json.url);
                }
                else {
                    // Add username to the end of the menu
                    var $user = "<label class='logged_user'>" +
                        "Logged in as '" + json.username + "'" + "</label>";
                    $($user).insertAfter($("#menu a:last-child"))
                    // Forward to annotation page -> don't allow to go back
                    // in history, otherwise use window.location.href = ...
                    window.location.replace(json.url);
                }
            },
            error: function (jqXHR, textStatus, errorThrown) {
                alert(errorThrown);
            }
        });
    }
}

// Extract all user data from the form and return them as an object.
function fetch_data_login(){
    // Variables in case user navigates to previous/next tweet
    var data = {};
    var $name = $("#username_log").val();
    var $pw = $("#password_log").val();
    data["username"] = $name;
    data["password"] = $pw;
    return data;
}

// Submits data about a user to the server and forwards him/her to the next
// page.
function register() {
    // Submit button was pushed -> send entered data back to server.
    // Prevent default behavior of submit button, i.e. sending POST
    // because we do it manually
    //event.preventDefault();
    var data = fetch_data_register();
    var csrftoken = getCookie('csrftoken');
    // Send only data if all necessary fields were filled in
    if (Object.keys(data).length > 0) {
        $.ajax({
            type: "POST",
            url: "/register/",
            dataType: "json",
            async: true,
            data: {
                // Without stringify the JS object isn't formatted as dict and
                // can't be parsed by Python
                data: JSON.stringify(data),
                csrfmiddlewaretoken: csrftoken
            },
            success: function (json) {
                // Pw/username incorrect
                if ("error" in json) {
                    console.log("forward to error after registration");
                    var s = "<label class='error'>" + json.error + "</label>";
                    $(s).appendTo($("#register_error"));
                }
                //else if ("message" in json) {
                //     404 error -> forward to error URL
                //    //console.log("forward to 404 after registration");
                //    //window.location.replace(json.url);
                //}
                else {
                    // Forward to annotation URL
                    console.log("forward to index after registration");
                    deleteRegistrationForm();
                    //selectLogin();
                    showConfirmation();
                    // Remove potential error messages from login panel
                    $("#login_submit label.error").text("");
                }
            },
            error: function (jqXHR, textStatus, errorThrown) {
                alert(errorThrown);
            }
        });
    }
}

// Deletes all user entered data of the form after submitting the data
// successfully
function deleteRegistrationForm() {
    $("#data")[0].reset();
}

function showConfirmation() {
    var msg =  "<label class='success'>Registration successful! Please, log in.</label>";
    $(msg).insertAfter($("#register")).show().delay(5000).fadeOut();

}

// Extract all user data from the form and return them as an object.
function fetch_data_register(){
    // Variables in case user navigates to previous/next tweet
    var data = {};
    var $email = $("#email").val();
    var $name = $("#username").val();
    var $pw = $("#password").val();
    var $sex = $("input[name='sex']:checked", "#data").val();
    var $nation = $("#nation option:selected").text();
    var $course = $("#course").val();
    var $level = $("#level option:selected").text();
    var $semesters = $("#semesters option:selected").text();
    var $faculty = $("#faculty option:selected").val();
    //var $strategy = $("#strategy option:selected").text();
    //var $group = $("#annogroup option:selected").val();
    data["username"] = $name;
    data["password"] = $pw;
    data["sex"] = $sex;
    data["nation"] = $nation;
    data["course"] = $course;
    data["level"] = $level;
    data["semesters"] = $semesters;
    data["faculty"] = $faculty;
    //data["strategy"] = $strategy;
    //data["group"] = $group;
    data["email"] = $email;
    return data;
}


// TODO: Write extra .js file for this function to use it in all other .js files
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