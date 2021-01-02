const appJSONQuery = "script#applications-json";
const projectFilterQuery  = "div#project-filter";
const projectFilterSelectQuery  = projectFilterQuery + " select";
const skillFilterQuery = "div#skill-filter";
const skillFilterSelectQuery = skillFilterQuery + " select#skill-filter-select";
const levelFilterSelectQuery = skillFilterQuery + " select#level-filter-select";
const appButtonQuery = "div#app-list";
var appInfo;
// var filteredApplications;

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

    var skill = $(skillFilterSelectQuery).val();
    var filterSkills = false;
    var level;
    if (skill !== "None") {
        filterSkills = true
        level = $(levelFilterSelectQuery).val();
    }

    const pId = $(projectFilterSelectQuery).val();
    const project = appInfo.projects[pId];
    
    // filteredApplications = appInfo.applications.filter(app => app.project == pId);
    for (appId in appInfo.applications) {
        var app = appInfo.applications[appId];
        var student = appInfo.students[app.student];
        if (app.project == pId && (!filterSkills || student.skills[skill] === level)) {
            $(appButtonQuery).append(`
                <button 
                    type="button" 
                    class="list-group-item list-group-item-action" 
                    name="selected_applicant" 
                    value="${ appId }"
                    onclick="renderApplication(${ appId })"
                >${ appInfo.students[app.student].first_name } ${ appInfo.students[app.student].last_name }</button>
            `);
        }
    }
}

function renderApplication(appId)  {

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
