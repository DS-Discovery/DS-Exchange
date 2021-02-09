const appJSONQuery = "script#applications-json";
const projectFilterQuery  = "div#project-filter";
const projectFilterSelectQuery  = projectFilterQuery + " select";
const skillFilterQuery = "div#skill-filter";
const skillFilterSelectQuery = skillFilterQuery + " select#skill-filter-select";
const levelFilterSelectQuery = skillFilterQuery + " select#level-filter-select";
const applicationQuestionsQuery = "div#application-questions";
const applicationSidebarQuery = "div#app-sidebar";
const appButtonQuery = "div#app-list";
var appInfo;

function loadApplications() {
    appInfo = JSON.parse($(appJSONQuery).text());
    loadProjectsFilter();
    loadSkillFilter();
    renderApplicantList();
}

function loadProjectsFilter() {
    var projectNamesAndIds = [];
    for (pId in appInfo.projects) {
        projectNamesAndIds.push([pId, appInfo.projects[pId].project_name]);
    }
    projectNamesAndIds.sort((a, b) => {
        if (a[1] < b[1]) return -1;
        else if (b[1] < a[1]) return 1;
        return 0;
    });

    var filterHTML = `
        <select name="project_wanted" class="custom-select mb-2" onchange="clearSkillFilter(); renderApplicantList()">
    `;
    for (i = 0; i < projectNamesAndIds.length; i++) {
        filterHTML += `
            <option class="dropdown-item" value="${ projectNamesAndIds[i][0] }">${ projectNamesAndIds[i][1] }</option>
        `;
    }
    filterHTML += `
        </select>
    `;
    $(projectFilterQuery).empty().append(filterHTML);
}

function renderApplicantList() {
    $(appButtonQuery).empty()
    clearRenderedApplication();

    var skill = $(skillFilterSelectQuery).val();
    var filterSkills = false;
    var level;
    if (skill !== "None") {
        filterSkills = true
        level = $(levelFilterSelectQuery).val();
    }

    const pId = $(projectFilterSelectQuery).val();
    const project = appInfo.projects[pId];

    for (appId in appInfo.applications) {
        var app = appInfo.applications[appId];
        var student = appInfo.students[app.student];
        if (app.project == pId && (!filterSkills || student.skills[skill] === level)) {
            var btn = `
                <button
                    type="button"
                    class="list-group-item list-group-item-action"
                    name="selected_applicant"
                    value="${ appId }"
                    onclick="renderApplication(${ appId })"
                    id="app-${ appId }"
                >${ appInfo.students[app.student].first_name } ${ appInfo.students[app.student].last_name }`;
            if (student.is_scholar) {
                btn += `<a href="https://data.berkeley.edu/academics/resources/data-scholars" target="_blank">
                    <span class="badge badge-pill badge-info ml-2" data-toggle="tooltip" data-placement="bottom" title="Data Scholar">S</span>
                </a>`;
            }
            btn += `</button>`;
            $(appButtonQuery).append(btn);
        }
    }
}

function renderApplication(appId)  {
    $(appButtonQuery + " button.active").removeClass("active");
    $(`#app-${ appId }`).addClass("active");

    var application = appInfo.applications[appId];
    var questions = appInfo.projects[application.project].questions;
    var answers = application.answers;
    var student = appInfo.students[application.student];

    var appHTML = "";

    for (i = 0; i < questions.length; i++) {
        var question = questions[i];
        var answer = "NUH-UH";
        for (j = 0; j < answers.length; j++) {
            if (answers[j].question == question.id) {
                answer = answers[j];
            }
        };

        appHTML += `
            <div class="application-question m-3">
                <h6>${ question.question_text }</h6>
        `;

        if (answer === "NUH-UH") {
            appHTML += `
                    <div class="alert alert-danger">Student submitted no response for this question.</div>
                </div>
            `;
            continue;
        }

        if (question.question_type === "text") {
            appHTML += `
                <textarea
                    class="form-group form-control"
                    placeholder="Your response here."
                    style="width: 80%;"
                    required
                    disabled
                >${ answer.answer_text }</textarea>
            `;
        } else if (question.question_type === "mc") {
            var options = question.question_data.split(";");
            for (j = 0; j < options.length; j++) {
                var radio = options[j];
                appHTML += `
                    <input
                        type="radio"
                        value ="${ radio }"
                        required
                        disabled
                `;
                if (radio === answer.answer_text) {
                    appHTML += `
                        checked
                    `;
                }
                appHTML += `
                    > ${ radio }<br>
                `;
            }
        } else if (question.question_type === "dropdown") {
            var options = question.question_data.split(";");
            appHTML += `
                <select class="custom-select" required disabled>
                    <option value=""></option>
            `
            for (j = 0; j < options.length; j++) {
                var radio = options[j];
                appHTML += `
                    <option value="${ radio }"
                `;
                if (radio === answer.answer_text) {
                    appHTML += `
                        selected
                    `;
                }
                appHTML += `
                    >${ radio }</option>
                `;
            }
            appHTML += `
                </select>
            `;
        } else if (question.question_type === "checkbox") {
            var options = question.question_data.split(";");
            for (j = 0; j < options.length; j++) {
                var radio = options[j];
                appHTML += `
                    <input
                        type="checkbox"
                        value ="${ radio }"
                        required
                        disabled
                `;
                if (answer.answer_text.split(";").includes(radio)) {
                    appHTML += `
                        checked
                    `;
                }
                appHTML += `
                    > ${ radio }<br>
                `;
            }
        } else if (question.question_type === "multiselect") {
            var options = question.question_data.split(";");
            appHTML += `
                <select class="custom-select" multiple required disabled>
            `
            for (j = 0; j < options.length; j++) {
                var radio = options[j];
                appHTML += `
                    <option value="${ radio }"
                `;
                if (answer.answer_text.split(";").includes(radio)) {
                    appHTML += `
                        selected
                    `;
                }
                appHTML += `
                    >${ radio }</option>
                `;
            }
            appHTML += `
                </select>
            `;
        } else if (question.question_type === "range") {
            var options = question.question_data.split(";");
            appHTML += `
                <script>
                    function updateSlider(i, slideAmount) {
                        slideAmount = parseInt(slideAmount);  // to prevent an syntax error below due to template syntax
                        var sliderDiv = document.getElementById("sliderAmount-" + i);
                        sliderDiv.innerHTML = slideAmount;
                    };
                </script>

                <input
                    type="range" min="${ options[0] }"
                    max="${ options[1] }" step="1"
                    value="${ answer.answer_text }"
                    onchange="updateSlider(${i}, this.value)"
                    disabled
                >
                <span id="sliderAmount-${ i }"></span>
                <script>updateSlider(${ i }, "${ answer.answer_text }")</script>
            `;
        }

        appHTML += `
            </div>
        `;
    }

    appProfileHTML = `
        <h5>General Interest Statement</h5>

        <p class="text-sm"><em>Why are you interested in the Discovery program? What do you hope to gain?</em></p>

        <p class="render-whitespace">${ student.general_question }</p>

        <h5>Skills</h5>

        <table class="table my-3">
            <tr>
                <th>Skill</th>
                <th>Skill Level</th>
            </tr>
    `
    for (skill in student.skills) {
        var level = student.skills[skill];
        appProfileHTML += `
            <tr>
                <td>${ skill }</td>
                <td>${ level }</td>
            </tr>
        `;
    }

    appProfileHTML += `
        </table>

        <h6>Additional Skills</h6>

        <p class="render-whitespace">${ student.additional_skills }</p>

        <h5>Application Questions</h5>

        ${ appHTML }
    `

    $(applicationQuestionsQuery).empty().append(appProfileHTML);
    loadApplicationSidebar(appId);
}

function clearRenderedApplication() {
    $(applicationQuestionsQuery).empty().append("<p>Please select an applicant on the left.</p>");
    $(applicationSidebarQuery).empty();
}

function loadSkillFilter() {
    var filterHTML = `
        <select name="skill_wanted" class="custom-select mb-2" onchange="filterSkills()" id="skill-filter-select">
    `;
    for (i = 0; i < appInfo.skills.length; i++) {
        var skill = appInfo.skills[i];
        filterHTML += `
            <option class="dropdown-item" value="${ skill }">${ skill }</option>
        `;
    }
    filterHTML += `
        </select>
    `;
    $(skillFilterQuery).empty().append(filterHTML);
}

function filterSkills()  {
    var skill = $(skillFilterSelectQuery).val();
    if (skill === "None") {
        $(levelFilterSelectQuery).remove();
        renderApplicantList();
        return
    } else if (!$(levelFilterSelectQuery).length) {
        var filterHTML = `
            <select name="level_wanted" class="custom-select" onchange="renderApplicantList()" id="level-filter-select">
        `;
        for (i = 0; i < appInfo.levels.length; i++) {
            var level = appInfo.levels[i];
            filterHTML += `
                <option class="dropdown-item" value="${ level }" >${ level }</option>
            `;
        }
        filterHTML += `
            </select>
        `;
        $(skillFilterQuery).append(filterHTML);

    }
    renderApplicantList();
}

function clearSkillFilter() {
    $(skillFilterSelectQuery).val("None");
    filterSkills();
}

function loadApplicationSidebar(appId) {
    var application = appInfo.applications[appId];
    var student = appInfo.students[application.student];
    sidebarHTML = `
        <div class="d-flex flex-column my-1">
            <h5 class="text-center">Basic Information</h5>

            <div class="d-flex flex-column my-1">
                <p>Name: <span class="text-muted">${ student.first_name } ${ student.last_name }</span></p>
                <p>Email: <span class="text-muted">${ student.email_address }</span></p>
                <p>Major: <span class="text-muted">${ student.major }</span></p>
                <p>Graduation Term: <span class="text-muted">${ student.year }</span></p>
            </div>

            <div class="d-flex flex-column align-items-center">
                <a class="btn btn-outline-info" href="${ student.resume_link }" role="button" target="_blank" rel="noopener noreferrer">Resume</a>
            </div>

        </div>

        <hr>

        <div class="d-flex flex-column my-1">

            <h5 class="text-center">Application Status</h5>

            <div class="my-1">

    `;
    for (short in application.app_status_choices) {
        if (short !== "SUB") {
            sidebarHTML += `
                <div class="d-flex flex-row justify-content-center mb-2">
                    <button
                        type="button"
                        class="btn
            `;
            if (short === application.status) {
                sidebarHTML += `btn-info disabled" disabled`;
             } else {
                 sidebarHTML += `btn-outline-info"`;
             }
             sidebarHTML += `
                        id="btn-${ short }"
                        onclick="updateStatusAndSubmit(${ appId }, '${ short }')"
                    >${ application.app_status_choices[short] }</button>
                </div>
            `;
        }
    }

    sidebarHTML += `
            </div>
        </div>
    `;

    $(applicationSidebarQuery).empty().append(sidebarHTML);
}

function updateStatusAndSubmit(appId, newStatus) {
    const csrftoken = getCookie('csrftoken');
    $.ajax({
        url: `/applications/status`,
        data: {
            application_id: appId,
            new_status: newStatus,
        },
        type: "POST",
        mode: "same-origin",
        beforeSend: (xhr) => xhr.setRequestHeader('X-CSRFToken', csrftoken),
        success: (data) => {
            $(applicationSidebarQuery + " button.disabled")
                .removeClass("disabled")
                .removeClass("btn-info")
                .addClass("btn-outline-info")
                .attr("disabled", false);
            $(`#btn-${ newStatus }`).addClass("disabled btn-info").removeClass("btn-outline-info").attr("disabled", true);
            console.log(data);
            sendAlert(data, 5000);
            appInfo.applications[appId].status = newStatus;
        },
    }).fail((xhr) => {
        alert(`The operation could not be performed. The server responded with the error:\n\n${ xhr.responseText }`);
    });
}

function downloadApplicants() {
  var data = {}
  const student_col = ["email_address", "first_name", "last_name", "college", "major",
                       "year", "resume_link", "general_question", "additional_skills",
                       "is_scholar"]
  var skill = $(skillFilterSelectQuery).val();
  var filterSkills = false;
  var level;
  if (skill !== "None") {
      filterSkills = true
      level = $(levelFilterSelectQuery).val();
  }

  const pId = $(projectFilterSelectQuery).val();
  const project = appInfo.projects[pId];

  for (appId in appInfo.applications) {
      var app = appInfo.applications[appId];
      var questions = appInfo.projects[app.project].questions;
      var answers = app.answers;
      var student = appInfo.students[app.student];
      if (app.project == pId && (!filterSkills || student.skills[skill] === level)) {
        // Student Information
        student_col.forEach(function(column){
          if (!data[column]) {
              data[column] = [];
          }
          data[column].push(appInfo.students[app.student][column]);
        })

        // Student Skills
        for (const [ column, value ] of Object.entries(appInfo.students[app.student].skills)) {
            if (!data[column]) {
                data[column] = [];
            }
            data[column].push(value);
        }

        //Application Answers
        for (i = 0; i < questions.length; i++) {
            var question = questions[i];
            if (!data[question]) {
                data[question] = [];
            }

            var answer = "NUH-UH";
            for (j = 0; j < answers.length; j++) {
                if (answers[j].question == question.id) {
                    answer = answers[j];
                }
            };

            if (answer === "NUH-UH") {
                data[question].push(null);
            } else {
                data[question].push(answer.answer_text);
            }
        }
      }
  }

  data_matrix = [];
  for (const [ key, value ] of Object.entries(data)) {
      row = [key];
      row.push.apply(row, value);
      data_matrix.push(row);
  }

  csv = "";
  // Assume all the same length
  if (data_matrix.length > 0) {
    for (var j = 0; j < data_matrix[0].length; j++) {
        for (var i = 0; i < data_matrix.length; i++) {
            csv += "\"" + `${data_matrix[i][j]}`.replace(/"/g, "'") + "\"";
            if (i == data_matrix.length - 1) {
              csv += "\n";
            } else {
              csv += ",";
            }
        }
    }
  }

  var hiddenElement = document.createElement('a');
  hiddenElement.href = 'data:text/csv;charset=utf-8,' + encodeURI(csv);
  hiddenElement.target = '_blank';
  hiddenElement.download = `${appInfo.projects[pId].project_name} Applicants.csv`;
  hiddenElement.click();
}

function listMembers(list, getMember, showCond) {

  teamRoster = "<ul>";
  team = ""
  for (idx in list) {
      var project = list[idx];
      if (showCond(project)) {
          var member = getMember(project);
          team += `<li><b>${member.first_name} ${member.last_name}</b>: ${member.email_address}</li>`;
      }
  }
  if (team === "") {
    teamRoster += "<li>None yet!</li>";
  } else {
    teamRoster += team;
  }
  teamRoster += "</ul>";

  return teamRoster
}

function renderTeamRoster() {
    var teamRoster = "Please select a project first!";

    const pId = $(projectFilterSelectQuery).val();
    const project = appInfo.projects[pId];

    if (pId > 0) {
        teamRoster = `<h3>Team Roster for ${project.project_name}</h3>`;
  
        teamRoster += "<br><h4>Partners</h4>";
        teamRoster += listMembers(appInfo.projectPartners, (x)=>x, (x)=>x.project == pId);
  
        teamRoster += "<br><h4>Students</h4>";
        teamRoster += listMembers( appInfo.applications, (x)=>appInfo.students[x.student], (x)=>x.project == pId && x.status === "OFA");
      }

    $(applicationQuestionsQuery).empty().append(teamRoster);
}
