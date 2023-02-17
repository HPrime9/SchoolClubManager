const BttnAddGeneralQuestion = document.querySelector('#addgeneralquestion');
const generalQuestionparent = document.querySelector('#generalquestions')

const BttnAddRole = document.querySelector('#addrole');
const AddRoleparent = document.querySelector('#roles')

const AddRoleSpecificQuestionparent = document.querySelector('#insertrolespecificquestionshere')

const SubmitApplicationCheckbox = document.querySelector('#showsubmitapplication')

if (BttnAddGeneralQuestion) {
    BttnAddGeneralQuestion.addEventListener('click', AddGeneralQuestion);
}
if (BttnAddRole) {
    BttnAddRole.addEventListener('click', AddRole);
}

if (SubmitApplicationCheckbox) {
    SubmitApplicationCheckbox.addEventListener('change', AddApplicationSubmitSaveButton);
}

function AddApplicationSubmitSaveButton() {
    if (SubmitApplicationCheckbox.checked) {
        document.getElementById('submitapplicationbutton1').value = 'Submit application'
        document.getElementById('submitapplicationbutton2').value = 'Submit application'
        document.querySelectorAll('.makerequiredgq').forEach(element => {
            element.required = true;
        });
        document.querySelectorAll('.makerequiredrsq').forEach(element => {
            element.required = true;
        });
    } else {
        document.getElementById('submitapplicationbutton1').value = 'Save Draft'
        document.getElementById('submitapplicationbutton2').value = 'Save Draft'
        document.querySelectorAll('.makerequiredgq').forEach(element => {
            element.required = false;
        });
        document.querySelectorAll('.makerequiredrsq').forEach(element => {
            element.required = false;
        });
    }
}

function AddGeneralQuestion() {
    generalQuestionparent.insertAdjacentHTML('afterbegin', `
    <div class='row mb-3'>
    <div class='col-4'>
            <label>Enter General Question</label>
            <input type='text' class='form-control' name='GeneralQuestions'>
    </div>
    <div class='col-6'>
            <label>Maximum character length for the response?</label>
            <input type='number' class='form-control' minlength='2' name='GeneralQuestionsLengthOfResponse'>
        </div>
    <div class='col-2'>
            <label>Enter Order Number</label>
            <input type='number' class='form-control' minlength='1' name='GeneralQuestionOrderNumbers'>
    </div>
    </div>
    `)
}
function OnAddRoleSpecificQuestion(button) {
    z = button.parentElement.children
    y = z[5]
    y.insertAdjacentHTML('afterbegin', `
    <div class='row mb-2'>
        <div class='col-4'>
            <label>Enter a question</label>
            <input class='form-control' type='text' name='RoleSpecificQuestion'>
        </div>
        <div class='col-6'>
            <label>Maximum character length for the response?</label>
            <input type='number' class='form-control' min='2' name='LengthOfResponse'>
        </div>
        <div class='col-2'>
            <label>Question Order</label>
            <input class='form-control' type='number' min='1' max='20' name='RoleSpecificQuestionOrderNumber'>
        </div>
    </div>
    `)
}

function AddRole() {
    AddRoleparent.insertAdjacentHTML('afterbegin', `
    <div class='row'>
        <div class='col-6'>
            <label>Enter role</label>
            <input class='form-control' type='text' name='Role'>
        </div>
        <div class='col-6'>
            <label>Enter Role Description</label>
            <input class='form-control' type='text' name='RoleDescription'>
        </div>
    </div>
    `)
}

// <div class='col-2'>
//         <br>
//             <button class='btn btn-secondary' type='button' onclick='onAddQuestion(this)'>Add question</button>
//         </div>

// function onAddQuestion(button) {
//     let question = document.createElement('input');
//     question.setAttribute('type', 'text');
//     question.setAttribute('class', 'col-10');
//     button.parentElement.parentElement.appendChild(question);
// }

// function onAddQuestion(button) {
//     counteranswerlength = 1
    
//     button.parentElement.parentElement.insertAdjacentHTML('beforeend', `
//     <div class='col-6'>
//         <label>Enter a question</label>
//         <input class='form-control' type='text' name='Role${counter}_Question'>
//     </div>
//     <div class='col-4'>
//             <label>Maximum character length for the response?</label>
//             <input type='number' class='form-control' name='ResponseLength${counter}'>
//         </div>
//     <div class='col-2'>
//         <label>Question Order</label>
//         <input class='form-control' type='number' min='1' max='20' name='OrderNumber${counter}'>
//     </div>
//     `)
// }