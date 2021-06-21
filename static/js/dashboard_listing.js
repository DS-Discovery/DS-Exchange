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

    var htmlTimeline = mdConverter.makeHtml(project.timeline);
    var htmlWorkflow = mdConverter.makeHtml(project.project_workflow)

    $(descriptionQuery).append(`
        <p class="mt-4"><strong>Project Timeline</strong></p>
        ${ htmlTimeline }

        <p class="mt-4"><strong>Project Workflow</strong></p>
        ${ htmlWorkflow }

        <hr>
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

    sidebarHTML += `
            </div>

            <p> # of total applications <span class="text-muted">${ project.num_applicants }</span></p>
            <p> # of offer sent <span class="text-muted">${ project.offer_sent }</span></p>
            <p> # of accepted offers <span class="text-muted">${ project.offer_accepted }</span></p>
            <p> # of accepted students <span class="text-muted">${ project.student_accepted }</span></p>

        </div>

        <hr>

        <div class="d-flex flex-column my-1">

            <h5 class="text-center">Next Steps</h5>

            <div class="my-1">

                <div class="d-flex flex-row justify-content-center mb-2">
                    <a href=""><button type="button" class="btn btn-outline-info">Download roster - Final team</button></a>
                </div>

                <div class="d-flex flex-row justify-content-center mb-2">
                    <a href=""><button type="button" class="btn btn-outline-info">Need more student - waitlist</button></a>
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
