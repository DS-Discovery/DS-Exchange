const projectJSONQuery = "script#projects-json";
const descriptionQuery = "div#description";
const projectInfoQuery = "div#project-sidebar"
const categoryFilterQuery = "div#category-filter";
const categoryFilterSelectId = "category-filter-select";

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
    loadCategoryFilter();
}

function loadCategoryFilter() {
    var categories = new Set();
    for (i = 0; i < projects.length; i++) {
        for (j = 0; j < projects[i].project_category.length; j++) {
            categories.add(projects[i].project_category[j]);
        }
    }
    categories = Array.from(categories).sort();
    var filterHTML = `
        <select name="category_wanted" class="custom-select" id="${ categoryFilterSelectId }" onChange="filterProjects()">
            <option class="dropdown-item" value=""></option>
    `;
    for (i = 0; i < categories.length; i++) {
        var category = categories[i];
        filterHTML += `<option class="dropdown-item" value="${ category }">${ category }</option>\n`;
    }
    filterHTML += `
        </select>
    `;
    $(categoryFilterQuery).empty().append(filterHTML);
}

function filterProjects() {
    var category = $(`#${ categoryFilterSelectId }`).val();
    if (category === "") {
        return listProjects([...Array(projects.length).keys()]);
    }
    console.log(category);
    var filteredProjects = [];
    for (i = 0; i < projects.length; i++) {
        if (projects[i].project_category.includes(category)) {
            filteredProjects.push(i);
        }
    }
    listProjects(filteredProjects);
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
    loadSidebar(project);
}

function replaceDescription(project) {
    $(descriptionQuery).empty();
    $(descriptionQuery).append(`
        <h5>${ project.project_name }</h5>
        <p class="mt-4"><strong>Project Description</strong></p>
        <p class="render-whitespace">${ project.description }</p>
        
        <p class="mt-4"><strong>Project Timeline</strong></p>
        <p class="render-whitespace">${ project.timeline }</p>

        <p class="mt-4"><strong>Project Workflow</strong></p>
        <p class="render-whitespace">${ project.project_workflow }</p>

        <p class="mt-4"><strong>Dataset</strong></p>
        <p class="render-whitespace">${ project.dataset }</p>

        <p class="mt-4"><strong>Deliverables</strong></p>
        <p class="render-whitespace">${ project.deliverable }</p>

        <p class="mt-4"><strong>Applicant Skillset</strong></p>
        <p class="render-whitespace">${ project.skillset }</p>

        <p class="mt-4"><strong>Project Organization:</strong> ${ project.organization }</p>
        <p class="render-whitespace">${ project.organization_description }</p>
    `);
}

function loadSidebar(project) {
    $(projectInfoQuery).empty()
    var sidebarHTML = `
        <div class="flex-row my-1">
            <h5 class="text-center">Project Info</h5>

            <div class="d-flex flex-row flex-wrap align-items-start mb-3">
    `;
    for (i in project.project_category) {
        var label = project.project_category[i];
        sidebarHTML += `<span class="badge badge-pill badge-info mr-1 mt-1">${ label }</span>\n`;
    }
    sidebarHTML += `
            </div>

            <p>Number of Students Requested: <span class="text-muted">${ project.student_num }</span></p>
            <p>Applications Received: <span class="text-muted">${ project.num_applicants }</span></p>

        </div>

        <hr>

        <div class="d-flex flex-column my-1">

            <h5 class="text-center">Action Items</h5>

            <div class="my-1">

                <div class="d-flex flex-row justify-content-center mb-2">
                    <a href="${ encodeURIComponent(project.project_name) }/apply"><button type="button" class="btn btn-outline-info">Apply</button></a>
                </div>

            </div>

        </div>
    `;
    $(projectInfoQuery).append(sidebarHTML);
}
