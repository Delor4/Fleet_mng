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

function create_links(wrapper, tab, class_str, params, viewonly){
    tooltips_nrs = params.mids_tt;
    tooltips_texts = params.tt

    for (var i=0; i<tab.length; i++) {
        wrapper.append('<'+(viewonly?'div':'a')+' class="bar '+
            class_str+
            (params.rented.indexOf(tab[i])>=0?' rented':'')+
            (params.back.indexOf(tab[i])>=0?' not_back':'')+
            '"'+
            (viewonly?'':(' href="/rent/' + tab[i] + '/"'))+
            ' data-toggle="tooltip" data-html="true" title="'+
            tooltips_texts[tooltips_nrs.indexOf(tab[i])]+
            '"'+
            '>'+
            (params.note.indexOf(tab[i])>=0?'<div class="note"'+
            ' data-toggle="tooltip" data-html="true" data-placement="left" title="'+
            params.note_desc[params.note.indexOf(tab[i])]+
            '"'+
            '></div>':'')+
            '</'+(viewonly?'div':'a')+'>');
    }
};
function create_bars_in_table(){
    $('#week_table').find( ".rent_bar" ).each(function() {
        var viewonly=false;
        if($(this).hasClass('viewonly')){
            viewonly=true;
        }
        data=$( this ).attr('data-bar').split(/\s+/);
        var bars = {
            firsts: [],
            lasts: [],
            mids: []
        };
        var params = {
            mids_tt: [],
            tt: [],
            rented: [],
            back: [],
            note: [],
            note_desc: []
        }
        //
        for (var class_name of data) {
            var beg = class_name.substr(0,2)
            var nr = class_name.substr(2)
            switch(beg) {
                case 'l_':
                    bars.lasts.push(nr);
                    break;
                case 'f_':
                    bars.firsts.push(nr)
                    params.note_desc.push(escape($( this ).attr('data-bar_desc_'+nr)))
                    break;
                case 'm_':
                    bars.mids.push(nr)
                    params.mids_tt.push(nr)
                    params.tt.push(escape($( this ).attr('data-bar_tooltip_'+nr)))
                    break;
                case 'r_':
                    params.rented.push(nr)
                    break;
                case 'b_':
                    params.back.push(nr)
                    break;
                case 'n_':
                    params.note.push(nr)
                    break;
            }
        }
        //
        bars.shared=[]
        for (var i=0; i<bars.lasts.length; i++) {
            if(bars.firsts.indexOf(bars.lasts[i])!=-1){
                bars.shared.push(bars.lasts[i])
                bars.firsts.splice(bars.firsts.indexOf(bars.lasts[i]),1)
                bars.lasts.splice(i,1)
                i--
            };
        }
        //
        bars.mids = bars.mids.diff(bars.firsts).diff(bars.lasts).diff(bars.shared)
        //
        $(this).append('<div class="rent_wrapper"></div>')
        var wrapper=$(this).find(".rent_wrapper")
        //
        create_links(wrapper, bars.lasts, "end_rent", params, viewonly)
        create_links(wrapper, bars.shared, "start_end_rent", params, viewonly)
        create_links(wrapper, bars.firsts, "start_rent", params, viewonly)
        create_links(wrapper, bars.mids, "mid_rent", params, viewonly)
    });
    $(function () {
        $('[data-toggle="tooltip"]').tooltip()
    });
}

jQuery(document).ready(function($){
    $('#week_table').show();
    create_bars_in_table()
})

function set_site_data( data ){
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

}

function load_site(site_url){
    $.get( site_url, function( data ) {
        set_site_data(data);
        window.history.pushState({ page: data }, "", data.nav.today_link);
    });
}

jQuery(document).ready(function($){
    $('body').find( "a.week_nav" ).click(function(event) {
        event.preventDefault();
        load_site($(this).attr('data-nav_target'));
    })

    //window.history.replaceState(...); TODO:

    window.onpopstate = function(event) {
        if(event.state == null ){
            window.location.reload()
        } else {
            set_site_data(event.state.page)
        }
        //
    }
})

// Position of week's navbar: fixed/inherit
var footerResize = function() {
            if ($('.week_nav_bar').css('position') == "fixed")
                $('.week_nav_bar').css('position', $("body").height() + $(".week_nav_bar").height() > $(window).innerHeight() ? "fixed" : "inherit");
            else
                $('.week_nav_bar').css('position', $("body").height() > $(window).innerHeight() ? "fixed" : "inherit");
};

jQuery(document).ready(function($) {
    $(window).resize(footerResize).ready(footerResize);
});
