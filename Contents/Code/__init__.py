NAME = 'Syfy'
ART = 'art-default.jpg'
ICON = 'icon-default.jpg'

SHOWS_URL = 'http://tveatc-usa.nbcuni.com/awe3/live/5/syfy/containers/iPadRetina'
SECTIONS_URL = 'http://tveatc-usa.nbcuni.com/awe3/live/5/syfy/asset/iPadRetina/%s'
VIDEOS_URL = 'http://tveatc-usa.nbcuni.com/awe3/live/5/syfy/containers/iPadRetina/%s?seasonNumber=%s&filterBy=%s&requiresAuth=false'

####################################################################################################
def Start():

	ObjectContainer.title1 = NAME
	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'BRNetworking/2.7.0.1449 (iPad;iPhone OS-8.1)'

####################################################################################################
@handler('/video/syfy', NAME, art=ART, thumb=ICON)
def Shows():

	oc = ObjectContainer()

	for show in JSON.ObjectFromURL(SHOWS_URL)['results']:

		title = show['title']

		if title.lower() in ['syfy movies']:
			continue

		show_id = show['assetID']
		summary = show['description']
		thumb = show['images'][0]['images']['show_thumbnail_16_by_9']

		oc.add(DirectoryObject(
			key = Callback(Sections, show_id=show_id, show=title),
			title = title,
			summary = summary,
			thumb = Resource.ContentsOfURLWithFallback(thumb, fallback=ICON)
		))

	oc.objects.sort(key=lambda obj: Regex('^The ').split(obj.title)[-1])
	return oc

####################################################################################################
@route('/video/syfy/{show_id}/sections')
def Sections(show_id, show):

	oc = ObjectContainer(title2=show)
	json_obj = JSON.ObjectFromURL(SECTIONS_URL % (show_id))
	thumb = json_obj['images'][0]['images']['show_thumbnail_16_by_9']

	total_episodes = 0
	total_clips = 0

	for season in json_obj['seasons']:

		if season['hasEpisodes']:

			json_obj = JSON.ObjectFromURL(VIDEOS_URL % (show_id, season['number'], 'episode'))
			total_episodes += json_obj['metadata']['total']

		if season['hasClips']:

			json_obj = JSON.ObjectFromURL(VIDEOS_URL % (show_id, season['number'], 'clip'))
			total_clips += json_obj['metadata']['total']

	if total_episodes > 0:

		oc.add(DirectoryObject(
			key = Callback(Seasons, show_id=show_id, show=show, filter_by='episode'),
			title = 'Full Episodes',
			thumb = Resource.ContentsOfURLWithFallback(thumb, fallback=ICON)
		))

	if total_clips > 0:

		oc.add(DirectoryObject(
			key = Callback(Seasons, show_id=show_id, show=show, filter_by='clip'),
			title = 'Clips',
			thumb = Resource.ContentsOfURLWithFallback(thumb, fallback=ICON)
		))

	return oc

####################################################################################################
@route('/video/syfy/{show_id}/{filter_by}/seasons')
def Seasons(show_id, show, filter_by):

	oc = ObjectContainer(title2=show)
	json_obj = JSON.ObjectFromURL(SECTIONS_URL % (show_id))
	thumb = json_obj['images'][0]['images']['show_thumbnail_16_by_9']

	for season in json_obj['seasons']:

		if filter_by == 'episode' and season['hasEpisodes']:

			oc.add(DirectoryObject(
				key = Callback(Videos, show_id=show_id, show=show, filter_by='episode', season=season['number']),
				title = 'Season %s' % (season['number']),
				thumb = Resource.ContentsOfURLWithFallback(thumb, fallback=ICON)
			))

		elif filter_by == 'clip' and season['hasClips']:

			oc.add(DirectoryObject(
				key = Callback(Videos, show_id=show_id, show=show, filter_by='clip', season=season['number']),
				title = 'Season %s' % (season['number']),
				thumb = Resource.ContentsOfURLWithFallback(thumb, fallback=ICON)
			))

	return oc

####################################################################################################
@route('/video/syfy/{show_id}/{filter_by}/{season}/videos')
def Videos(show_id, show, filter_by, season):

	oc = ObjectContainer(title2=show)

	for episode in JSON.ObjectFromURL(VIDEOS_URL % (show_id, season, filter_by))['results']:

		if episode['requiresAuth']:
			continue

		parent_id = episode['parentContainerId']
		episode_id = episode['assetID']

		title = episode['title']

		try: ep_index = int(episode['episodeNumber'])
		except: ep_index = None

		try: thumb = episode['images'][0]['images']['video_detail_16_by_9']
		except: thumb = ''

		oc.add(EpisodeObject(
			url = 'syfy://%s/%s' % (parent_id, episode_id),
			show = show,
			title = title,
			summary = episode['description'],
			thumb = Resource.ContentsOfURLWithFallback(url=thumb),
			season = int(episode['seasonNumber']),
			index = ep_index,
			duration = episode['totalDuration'],
			originally_available_at = Datetime.FromTimestamp(episode['firstAiredDate'])
		))

	return oc
