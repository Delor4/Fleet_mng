function _delete(e,a,msg) {
    if(e)
        e.preventDefault();
    else
        window.event.returnValue=false;
    if(window.confirm(msg))
        document.forms.delete_form.confirm.value=1;
        document.forms.delete_form.submit();
}
