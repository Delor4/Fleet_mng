Array.prototype.diff = function(a) {
    return this.filter(function(i) {
        return a.indexOf(i) < 0;
    });
};
var htmlEscapes = {
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&#x27;',
  '/': '&#x2F;'
};

// Regex containing the keys listed immediately above.
var htmlEscaper = /[&<>"'\/]/g;

// Escape a string for HTML interpolation.
function escape(string) {
  return ('' + string).replace(htmlEscaper, function(match) {
    return htmlEscapes[match];
  });
};

function create_links(wrapper, tab, class_str, tooltips_nrs, tooltips_texts, vo, note, note_desc){
    for (let i=0; i<tab.length; i++) {
        wrapper.append('<'+(vo?'div':'a')+' class="bar '+
            class_str+
            (rented.indexOf(tab[i])>=0?' rented':'')+
            (back.indexOf(tab[i])>=0?' not_back':'')+
            '"'+
            (vo?'':(' href="/rent/' + tab[i] + '/"'))+
            ' data-toggle="tooltip" data-html="true" title="'+
            escape(tooltips_texts[tooltips_nrs.indexOf(tab[i])])+
            '"'+
            '>'+
            (note.indexOf(tab[i])>=0?'<div class="note"'+
            ' data-toggle="tooltip" data-html="true" data-placement="left" title="'+
            escape(note_desc[note.indexOf(tab[i])])+
            '"'+
            '></div>':'')+
            '</'+(vo?'div':'a')+'>');
    }
};
function create_bars_in_table(){
    $('#week_table').find( ".rent_bar" ).each(function() {
        viewonly=false;
        if($(this).hasClass('viewonly')){
            viewonly=true;
        }
        data=$( this ).attr('data-bar').split(/\s+/);
        firsts=[]
        lasts=[]
        mids = []
        mids_tt = []
        tt = []
        rented=[]
        back=[]
        note=[]
        note_desc=[]
        //
         for (let i=0; i<data.length; i++) {
            beg = data[i].substr(0,2)
            nr = data[i].substr(2)
            if(beg=='l_'){
                lasts.push(nr)
            }else  if(beg=='f_'){
                firsts.push(nr)
                note_desc.push(escape($( this ).attr('data-bar_desc_'+nr)))
            }else  if(beg=='m_'){
                mids.push(nr)
                mids_tt.push(nr)
                tt.push(escape($( this ).attr('data-bar_tooltip_'+nr)))
            }else  if(beg=='r_'){
                rented.push(nr)
            }else  if(beg=='b_'){
                back.push(nr)
            }else  if(beg=='n_'){
                note.push(nr)
            }
         }
         //
        shared=[]
        for (let i=0; i<lasts.length; i++) {
            if(firsts.indexOf(lasts[i])!=-1){
                shared.push(lasts[i])
                firsts.splice(firsts.indexOf(lasts[i]),1)
                lasts.splice(i,1)
                i--
            };
        }
        //
        mids = mids.diff(firsts).diff(lasts).diff(shared)
        //
        $(this).append('<div class="rent_wrapper"></div>')
        wrapper=$(this).find(".rent_wrapper")
        //
        create_links(wrapper, lasts, "end_rent", mids_tt, tt, viewonly, note, note_desc)
        create_links(wrapper, shared, "start_end_rent", mids_tt, tt, viewonly, note, note_desc)
        create_links(wrapper, firsts, "start_rent", mids_tt, tt, viewonly, note, note_desc)
        create_links(wrapper, mids, "mid_rent", mids_tt, tt, viewonly, note, note_desc)
    });
    $(function () {
        $('[data-toggle="tooltip"]').tooltip()
    });
}

jQuery(document).ready(function($){
    create_bars_in_table()
})

function load_site(site_url){
    $.get( site_url, function( data ) {
              //update table data
              $('#week_table').html( data.table_html );
              create_bars_in_table()
              //update buttons data
              $('a.week_nav.prev').attr('data-nav_target', data.nav.prev.ajax_link)
              $('a.week_nav.prev').attr('href', data.nav.prev.link)

              $('a.week_nav.prev_week').attr('data-nav_target', data.nav.prev_week.ajax_link)
              $('a.week_nav.prev_week').attr('href', data.nav.prev_week.link)

              $('a.week_nav.next').attr('data-nav_target', data.nav.next.ajax_link)
              $('a.week_nav.next').attr('href', data.nav.next.link)

              $('a.week_nav.next_week').attr('data-nav_target', data.nav.next_week.ajax_link)
              $('a.week_nav.next_week').attr('href', data.nav.next_week.link)
              window.history.pushState({ page: data.nav.today_ajax_link }, "", data.nav.today_link);
            });
}
jQuery(document).ready(function($){
    $('body').find( "a.week_nav" ).click(function(event) {
        event.preventDefault();
        load_site($(this).attr('data-nav_target'));
    })
    window.onpopstate = function(event) {
        //window.location.reload()
  }
})