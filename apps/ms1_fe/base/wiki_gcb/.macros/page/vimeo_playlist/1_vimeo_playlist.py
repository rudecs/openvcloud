import os
import re


def main(j, args, params, tags, tasklet):
    '''
        Create a playlist of a group of vimeo videos, using bootstrap 3 tabs

        This is an example

        {{vimeo_playlist:
        Title goes here
        followed by subtitle
        http://player.vimeo.com/video/1234
        ---------------
        Title 2
        Subtitle 2
        http://player.vimeo.com/video/8799
        }}
    '''
    page = args.page
    params.result = page

    groups = re.split(r'-{2,}', args.cmdstr) # Split by group separator
    groups = [g.strip().splitlines() for g in groups]
    groups = [(g[0].strip(), g[1].strip(), g[2].strip()) for g in groups]

    # Add tab buttons
    page.addMessage('<ul class="nav-pills nav-stacked col-md-3" role="tablist">')
    for i, (title, subtitle, url) in enumerate(groups):
        active = 'class="active"' if i == 0 else ''
        page.addMessage('<li {active}><a data-toggle="tab" role="tab" href="#tab{i}"><strong>{title}</strong><br>{subtitle}</a></li>'.format(
            i=i, active=active, title=title, subtitle=subtitle))
    page.addMessage('</ul>')

    # Add tabs
    page.addMessage('<div class="tab-content col-md-9">')
    for i, (title, subtitle, url) in enumerate(groups):
        active = 'in active' if i == 0 else ''
        page.addMessage('''<div id="tab{i}" class="tab-pane fade {active}">
                              <iframe id="player{i}" src="{url}?title=0&amp;byline=0&amp;portrait=0&api=1&player_id=player{i}"
                                  frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen>
                              </iframe>
                            </div>'''.format(i=i, active=active, title=title, subtitle=subtitle, url=url))
    page.addMessage('</div>')

    page.addJS(jsContent='''$(function() {
        var togglers = $('a[data-toggle="tab"]');
        togglers.each(function() {
            var toggler = $(this);
            var next = toggler.parents('li').next();
            var tab = $(toggler.attr('href'));

            // when a tab is activated, play its video & stop the previous video
            toggler.on('shown.bs.tab', function (e) {
                var player = $($(e.relatedTarget).attr('href')).find('iframe');
                if (player.length > 0) {
                    var prevPlayer = $f(player[0]);
                    prevPlayer.api('pause');
                    prevPlayer.api('seekTo', 0);
                    var thisPlayer = $($(e.target).attr('href')).find('iframe');
                    if (thisPlayer.length > 0)
                        $f(thisPlayer[0]).api('play');
                }
            });
        });

        // when a video is finished playing, go with the next
        $('iframe[src*=vimeo]').load(function() {
            var player = $f(this);
            player.addEvent('pause', function(player_id) {console.log(player_id + ' paused')});
            player.addEvent('finish', function(player_id) {
                $('a[href=#' + $('#' + player_id).parent('.tab-pane').attr('id') + ']').parent().next().find('a[data-toggle=tab]').tab('show');
            });
        });
    });''')

    return params


def match(j, args, params, tags, tasklet):
    return True

