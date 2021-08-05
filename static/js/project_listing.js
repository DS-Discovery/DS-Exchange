const projectJSONQuery = "script#projects-json";
const descriptionQuery = "div#description";
const projectInfoQuery = "div#project-sidebar"
const categoryFilterQuery = "div#category-filter";
const categoryFilterSelectId = "category-filter-select";
const copyButtonId = "copy-link";
const linkSVG = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="1.25rem"
style="margin-bottom: 2px; padding-bottom: 5px; margin-left: 5px; opacity: 0.5;">
    <path fill-rule="evenodd" d="M7.775 3.275a.75.75 0 001.06 1.06l1.25-1.25a2 2 0 112.83 2.83l-2.5
    2.5a2 2 0 01-2.83 0 .75.75 0 00-1.06 1.06 3.5 3.5 0 004.95 0l2.5-2.5a3.5 3.5 0 00-4.95-4.95l-1.25
    1.25zm-4.69 9.64a2 2 0 010-2.83l2.5-2.5a2 2 0 012.83 0 .75.75 0 001.06-1.06 3.5 3.5 0 00-4.95
    0l-2.5 2.5a3.5 3.5 0 004.95 4.95l1.25-1.25a.75.75 0 00-1.06-1.06l-1.25 1.25a2 2 0 01-2.83 0z">
    </path>
</svg>`;

// showdown
const mdConverter = new showdown.Converter();

var projects;

function loadProjects(selectedProj) {
    projects = JSON.parse($(projectJSONQuery).text()).projects;

    // trim category whitespace
    for (i = 0; i < projects.length; i++) {
        for (j = 0; j < projects[i].project_category.length; j++) {
            projects[i].project_category[j] = projects[i].project_category[j].trim();
        }
    }

    listProjects([...Array(projects.length).keys()]);
    loadCategoryFilter();


    let projId = parseInt(selectedProj);
    if (projId && projId > 0) {
        for (i = 0; i < projects.length; i++) {
            if (projects[i].id == projId) {
              clickProject(i);
              return;
            }
        }
    }
}

function loadCategoryFilter() {
    var categories = new Set();
    for (i = 0; i < projects.length; i++) {
        categories.add(projects[i].project_category);
        // for (j = 0; j < projects[i].project_category.length; j++) {
        //     categories.add(projects[i].project_category[j]);
        // }
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

function projectLink(projId) {
  var e = document.createElement("textarea");
  e.value = window.location.origin + window.location.pathname + "?selected=" + projId;
  e.setAttribute("readonly", "");
  e.style = {position: "absolute", left: "-9999px"};
  document.body.appendChild(e);
  e.select();
  document.execCommand("copy");
  document.body.removeChild(e);
}

function replaceDescription(project) {
    $(descriptionQuery).empty();

    var htmlSkillset = `
        <table class="table my-3">
            <tr>
                <th>Skill</th>
                <th>Skill Level</th>
            </tr>
    `;
    for (skill in project.skillset) {
        htmlSkillset += `
            <tr>
                <td>${ skill }</th>
                <td>${ project.skillset[skill] }</td>
            </tr>
        `;
    }
    htmlSkillset += `
        </table>
    `;

    var htmlDescription = mdConverter.makeHtml(project.description);
    var htmlTimeline = mdConverter.makeHtml(project.timeline);
    var htmlWorkflow = mdConverter.makeHtml(project.project_workflow);
    var htmlOrgDescription = mdConverter.makeHtml(project.organization_description);

    $(descriptionQuery).append(`
        <h5 style="display: inline;">${ project.project_name }</h5>
        <span class="copy" id="${ copyButtonId }" onclick="projectLink(${ project.id })">${ linkSVG }</span>
        <p class="mt-4"><strong>Project Description</strong></p>
        ${ htmlDescription }

        <p class="mt-4"><strong>Project Timeline</strong></p>
        ${ htmlTimeline }

        <p class="mt-4"><strong>Project Workflow</strong></p>
        ${ htmlWorkflow }

        <p class="mt-4"><strong>Dataset</strong></p>
        <p class="render-whitespace">${ project.dataset }</p>

        <p class="mt-4"><strong>Deliverables</strong></p>
        <p class="render-whitespace">${ project.deliverable }</p>

        <p class="mt-4"><strong>Applicant Skillset</strong></p>
        ${ htmlSkillset }

        <p class="mt-4"><strong>Additional Skills</strong></p>
        <p class="render-whitespace">${ project.additional_skills }</p>

        <p class="mt-4"><strong>Technical Requirements</strong></p>
        <p class="render-whitespace">${ project.technical_requirements }</p>

        <p class="mt-4"><strong>Project Organization:</strong> ${ project.organization }</p>
        ${ htmlOrgDescription }
    `);

    setUpCopyButton();
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

function setUpCopyButton() {
    $(`#${ copyButtonId }`).on("mouseover", () => {
        $(this).css("content", "copy link");
        $(this).css("cursor", "pointer")
    })
}
