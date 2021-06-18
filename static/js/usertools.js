function toggle(id) {
  let parent = document.getElementById(id);
  let elem = document.getElementById(id+'-drop');
  let curr_display =  window.getComputedStyle(elem).getPropertyValue('display');
  if (curr_display == 'none'){
    parent.classList.add('open');
    parent.classList.remove('closed');
    document.getElementById(id+'-drop').style.display = elem.getAttribute("display");
  } else {
    parent.classList.remove('open');
    parent.classList.add('closed');
    elem.setAttribute("display", curr_display);
    document.getElementById(id+'-drop').style.display = "none";
  }
}

function toggle_select(select) {
  let elem = document.getElementById('filter-drop');
  let nodes = elem.childNodes;
  for (let i = 0; i < nodes.length; i++) {
    if (nodes[i].nodeName.toLowerCase() == 'label' &&
        nodes[i].firstChild &&
        nodes[i].firstChild.nodeName.toLowerCase() == 'input') {
          nodes[i].firstChild.checked = select;
     }
   }
}

function add_onclick(id) {
  let elem = document.getElementById(id);
  elem.classList.add('toggle');
  elem.classList.add('open');
  elem.onclick = function() { toggle(this.id) };
}

function select_toggle_onclick(id) {
  let elem = document.getElementById(id);
  let select_mode = elem.classList.contains('select')? true : false;
  elem.onclick = function() { toggle_select( select_mode) };
}
['tools', 'group', 'display', 'semester', 'filter', 'export'].forEach(add_onclick);
['showSelect', 'showDeselect'].forEach(select_toggle_onclick);
