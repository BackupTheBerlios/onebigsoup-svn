function toggle_display(id){
  var el = document.getElementById(id)
  if (el.style.display != 'none') {
    el.style.display = 'none';
  }
  else {
    el.style.display = '';
  }
}
