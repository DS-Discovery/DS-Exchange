const descriptionQuery = "div#description";
const projectInfoQuery = "div#project-sidebar"
var projects;

function loadProjects() {
    const jqxhr = $.ajax({
        url: "/projects/json",
    }).done((data) => {
        console.log(data);
        projects = data.projects;
        listProjects();
    }).fail(() => {
        alert("Could not load projects. Please refresh the page to continue.")
    });
    return jqxhr;
}

function listProjects() {
    for (i = 0; i < projects.length; i++) {
        var project =  projects[i];
        console.log(project);
        $("div#project-list").append(`
            <button 
                type="button" 
                class="list-group-item list-group-item-action project" 
                id="project-${ i }" 
                onclick="clickProject(${ i })"
            >${ project.project_name }</button>
        `);
    }
}

function clickProject(projectNum) {
    var projectId = "#project-" + projectNum;
    $("button.project.active").removeClass("active");
    $(projectId).addClass("active");
    replaceDescription(projectNum);
    loadSidebar(projectNum);
}

function replaceDescription(projectNum) {
    $(descriptionQuery).empty();
    var project = projects[projectNum];
    $(descriptionQuery).append(`
        <h5>${ project.project_name }</h5>
        <p class="mt-4"><strong>Project Description</strong></p>
        <p>${ project.description }</p>
    `);
}

function loadSidebar(projectNum) {
    var project = projects[projectNum];
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

            <p>Number of Students: <span class="text-muted">${ project.student_num }</span></p>
            <p>Applications Received: <span class="text-muted">${ project.num_applicants }</span></p>

        </div>

        <hr>

        <div class="d-flex flex-column my-1">

            <h5 class="text-center">Action Items</h5>

            <div class="my-1">

                <div class="d-flex flex-row justify-content-center mb-2">
                    <a href="${ project.project_name }/apply"><button type="button" class="btn btn-outline-info">Apply</button></a>
                </div>

            </div>

        </div>
    `;
    $(projectInfoQuery).append(sidebarHTML);
}
