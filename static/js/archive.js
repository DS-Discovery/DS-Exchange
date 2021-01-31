const projectJSONQuery = "script#projects-json";
const descriptionQuery = "div#description";
const projectInfoQuery = "div#project-sidebar"
const categoryFilterQuery = "div#category-filter";
const categoryFilterSelectId = "category-filter-select";

// showdown
const mdConverter = new showdown.Converter();

var projects;

function loadProjects() {
    projects = JSON.parse($(projectJSONQuery).text()).projects;

    // trim category whitespace
    for (i = 0; i < projects.length; i++) {
        for (j = 0; j < projects[i].project_category.length; j++) {
            projects[i].project_category[j] = projects[i].project_category[j].trim();
        }
    }

    listProjects([...Array(projects.length).keys()]);
}

function listProjects(projectIdxs) {
    $(descriptionQuery).empty().append("<p>No project selected.</p>");
    $(projectInfoQuery).empty();
    $("div#project-list").empty();
    for (i = 0; i < projectIdxs.length; i++) {
        var project =  projects[projectIdxs[i]];
        console.log(project);
        $("div#project-list").append(`
            <button 
                type="button" 
                class="list-group-item list-group-item-action project" 
                id="project-${ projectIdxs[i] }" 
                onclick='clickProject(${ projectIdxs[i] })'
            >${ project.project_name }</button>
        `);
    }
}

function clickProject(projectNum) {
    var projectId = "#project-" + projectNum;
    var project = projects[projectNum];
    $("button.project.active").removeClass("active");
    $(projectId).addClass("active");
    replaceDescription(project);
}

function replaceDescription(project) {
    $(descriptionQuery).empty();

    var htmlTemp = project.description;
    $(descriptionQuery).append(`
        <h5>${ project.project_name }</h5>
        <p class="mt-4"><strong>Project Deliverable</strong></p>
    `);
    $(descriptionQuery).append(htmlTemp);
}

