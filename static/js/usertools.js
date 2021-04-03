function toggle(id) {
  let elem = document.getElementById(id+'-drop');
  let curr_display =  window.getComputedStyle(elem).getPropertyValue('display');
  console.log(curr_display);
  if (curr_display == 'none'){
    document.getElementById(id+'-drop').style.display = elem.getAttribute("display");
  } else {
    elem.setAttribute("display", curr_display);
    document.getElementById(id+'-drop').style.display = "none";
  }
}
function add_onclick(id) {
  let elem = document.getElementById(id);
  elem.classList.add('toggle');
  elem.onclick = function() { toggle(this.id) };
}
['tools', 'group', 'semester', 'filter', 'show', 'hide', 'export'].forEach(add_onclick);
