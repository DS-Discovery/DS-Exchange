function loadProjects(projects) {
    var i = 0;
    for (project in projects) {
        $("project-list").append(`
            <button 
                type="button" 
                class="list-group-item list-group-item-action project" 
                id="project-${i}" 
                onclick="clickProject(${i})"
            >${project.project_name}</button>
        `);
        i++;
    }
}

function clickProject(projectNum) {
    var projectId = "#project-" + projectNum;
    $("button.project.active").removeClass("active");
    $(projectId).addClass("active");
}

$(window).on("ready", () => {
    const jqxhr = $.get("/projects/json", loadProjects);
})
