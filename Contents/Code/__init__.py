SHOWS_URL = 'http://tve-atcnbc.nbcuni.com/ep-live/2/syfy/shows/iPad'
EPISODES_URL = 'http://tve-atcnbc.nbcuni.com/ep-live/2/syfy/container/x/iPad/%s'

####################################################################################################
def Start():

	ObjectContainer.title1 = 'Syfy'
	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36'

####################################################################################################
@handler('/video/syfy', 'Syfy')
@route('/video/syfy/shows')
def Shows():

	oc = ObjectContainer()

	if not Client.Platform in ('Android', 'iOS', 'Roku', 'Safari', 'Firefox', 'Chrome', 'Windows', 'Windows Phone'):
		oc.header = 'Not supported'
		oc.message = 'This channel is not supported on %s' % (Client.Platform if Client.Platform is not None else 'this client')
		return oc

	for show in JSON.ObjectFromURL(SHOWS_URL):
		show_id = show['assetID']
		title = show['title']

		if title in ('Syfy Original Movies'):
			continue

		summary = show['description']
		thumb = show['images'][0]['images']['show_tile']

		oc.add(DirectoryObject(
			key = Callback(Episodes, show_id=show_id, show=title),
			title = title,
			summary = summary,
			thumb = Resource.ContentsOfURLWithFallback(thumb)
		))

	oc.objects.sort(key = lambda obj: obj.title)
	return oc

####################################################################################################
@route('/video/syfy/episodes/{show_id}')
def Episodes(show_id, show):

	oc = ObjectContainer(title2=show)

	for episode in JSON.ObjectFromURL(EPISODES_URL % show_id)['assetsX']:

		if episode['type'] != 'video' or episode['subtype'] != 'episode' or episode['requiresAuth'] is not False:
			continue

		url = 'http://www.syfy.com/#%s|%s' % (show_id, episode['assetID'])

		oc.add(EpisodeObject(
			url = url,
			show = show,
			title = episode['title'],
			summary = episode['description'],
			thumb = Resource.ContentsOfURLWithFallback(episode['images'][0]['images']['episode_banner']),
			season = int(episode['seasonNumber']),
			index = int(episode['episodeNumber']),
			duration = episode['totalDuration'],
			originally_available_at = Datetime.FromTimestamp(episode['firstAiredDate'])
		))

	if len(oc) < 1:
		return ObjectContainer(header='Empty', message='There are no episodes available for this show')

	return oc
