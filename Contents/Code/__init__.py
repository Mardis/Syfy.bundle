SHOWS_URL = 'http://tve-atcnbce.nbcuni.com/live/3/syfy/containers/iPad'
VIDEOS_URL = 'http://tve-atcnbce.nbcuni.com/live/3/syfy/containers/%s/iPad'

####################################################################################################
def Start():

	ObjectContainer.title1 = 'Syfy'
	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'BRNetworking/2.7.0.1449 (iPad;iPhone OS-8.1)'

####################################################################################################
@handler('/video/syfy', 'Syfy')
@route('/video/syfy/shows')
def Shows():

	oc = ObjectContainer()

	for show in JSON.ObjectFromURL(SHOWS_URL):

		show_id = show['assetID']
		title = show['title']

		if 'movies' in title.lower():
			continue

		summary = show['description']
		thumb = show['images'][0]['images']['show_tile']

		oc.add(DirectoryObject(
			key = Callback(Episodes, show_id=show_id, show=title),
			title = title,
			summary = summary,
			thumb = Resource.ContentsOfURLWithFallback(thumb)
		))

	oc.objects.sort(key=lambda obj: obj.title)
	return oc

####################################################################################################
@route('/video/syfy/episodes/{show_id}')
def Episodes(show_id, show):

	oc = ObjectContainer(title2=show)
	clips_available = False

	for episode in JSON.ObjectFromURL(VIDEOS_URL % show_id)['results']:

		if episode['type'] == 'video' and episode['subtype'] == 'clip' and episode['requiresAuth'] == False:
			clips_available = True

		if episode['type'] != 'video' or episode['subtype'] != 'episode' or episode['requiresAuth']:
			continue

		url = 'http://www.syfy.com/#%s|%s' % (show_id, episode['assetID'])
		thumb = episode['images'][0]['images']['episode_banner'] if 'episode_banner' in episode['images'][0]['images'] else ''

		oc.add(EpisodeObject(
			url = url,
			show = show,
			title = episode['title'],
			summary = episode['description'],
			thumb = Resource.ContentsOfURLWithFallback(url=thumb),
			season = int(episode['seasonNumber']),
			index = int(episode['episodeNumber']),
			duration = episode['totalDuration'],
			originally_available_at = Datetime.FromTimestamp(episode['firstAiredDate'])
		))

	if clips_available:

		oc.add(DirectoryObject(
			key = Callback(Clips, show_id=show_id, show=show),
			title = 'Clips'
		))

	if len(oc) < 1:
		return ObjectContainer(header='Empty', message='There are no videos available for this show')

	return oc

####################################################################################################
@route('/video/syfy/clips/{show_id}')
def Clips(show_id, show):

	oc = ObjectContainer(title2=show)

	for clip in JSON.ObjectFromURL(VIDEOS_URL % show_id)['results']:

		if clip['type'] != 'video' or clip['subtype'] != 'clip' or clip['requiresAuth']:
			continue

		url = 'http://www.syfy.com/#%s|%s' % (show_id, clip['assetID'])
		thumb = clip['images'][0]['images']['episode_banner'] if 'episode_banner' in clip['images'][0]['images'] else ''

		oc.add(VideoClipObject(
			url = url,
			title = clip['title'],
			summary = clip['description'],
			thumb = Resource.ContentsOfURLWithFallback(url=thumb),
			duration = clip['totalDuration'],
			originally_available_at = Datetime.FromTimestamp(clip['firstAiredDate'])
		))

	return oc
