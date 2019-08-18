function _delete(e,a,msg) {
    if(e)
        e.preventDefault();
    else
        window.event.returnValue=false;
    if(window.confirm(msg))
        a.confirm.value=1;
        a.submit();
}
