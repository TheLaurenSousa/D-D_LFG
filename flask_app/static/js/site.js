var modify_field = document.getElementById("field");

function role_selected(){
    var form = document.getElementById("role");
    var selected_role = form.options[form.selectedIndex].value;
    var initial_question = document.getElementById("initial_question");
    modify_field = setup_questions(selected_role);
    initial_question.remove();
}

function setup_questions(selected_role){
    if (selected_role == "player"){
        document.getElementById("player_questions").style.display = 'block';
    }
    if (selected_role == "dm"){
        document.getElementById("dm_questions").style.display = 'block';
    }
}

function create_account(){
    var signin = document.getElementById("signin");
    signin.remove();
    modify_field.style.display = "block";
}