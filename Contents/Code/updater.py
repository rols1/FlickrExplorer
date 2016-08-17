################################################################################
import re, urllib, os

ICON_OK = "icon-ok.png"				# gtk themes / Adwaita checkbox-checked-symbolic.symbolic.png
ICON_WARNING = "icon-warning.png"	# gtk themes / Adwaita dialog-warning-symbolic.symbolic.png
ICON_ERROR = "icon-error.png"		# gtk themes / Adwaita dialog-error.png
ICON_UPDATER = "icon-updater.png"	# gtk themes / Adwaita system-software-update.png
ICON_RELEASES = "icon-releases.png"	# gtk themes / Adwaita view-list-symbolic.symbolic.png
ICON_NEXT = "icon-next.png"			# gtk themes / Adwaita go-next-symbolic.symbolic.png 

FEED_URL = 'https://github.com/{0}/releases.atom'

################################################################################
TITLE = "Plex Plugin für die deutsche ARD Mediathek - mit Live-TV der ARD + weiteren Sendern"
REPO_NAME = 'Plex-Plugin-Flickr'
GITHUB_REPOSITORY = 'rols1/' + REPO_NAME
PREFIX = "/video/flickr"
################################################################################

# This gets the release name
def get_latest_version():
	try:
		# releases.atom liefert Releases-Übersicht als xml-Datei 
		release_feed_url = ('https://github.com/{0}/releases.atom'.format(GITHUB_REPOSITORY))
		release_feed_data = RSS.FeedFromURL(release_feed_url, cacheTime=0, timeout=10)
		link = release_feed_data.entries[0].link
		tags = link.split('/')
		tag = tags[len(tags)-1]
		summary = cleanSummary((release_feed_data.entries[0].content[0]))
		Log(link); Log(tags); Log(tag); Log(summary); 
		return (release_feed_data.entries[0].title, summary, tag)
	except Exception as exception:
		#Log.Error('Checking for new releases failed: {0}'.format(repr(exception)))
		Log.Error('Suche nach neuen Versionen fehlgeschlagen: {0}'.format(repr(exception)))
		return (None, None, None)

################################################################################
def update_available(VERSION):
	try:
		latest_version_str, summ, tag = get_latest_version()
		#latest_version_str = getOnlyVersionNumber(latest_version_str) # hier n.b.
		Log(latest_version_str); Log(summ); Log(tag); 
		
		if tag:
			# wir verwenden auf Github die Versionierung nicht im Plugin-Namen
			# latest_version  = latest_version_str 
			latest_version  = tag		# Format hier: '1.4.1'
			current_version = VERSION
			int_lv = tag.replace('.','')
			int_cv = current_version.replace('.','')
			Log(latest_version); Log(current_version); Log(int_lv); Log(int_cv)
			return (int_lv, int_cv, latest_version, summ, tag)
	except:
		pass
	return (False, None, None, None)

################################################################################
@route(PREFIX + '/update')
def update(url, ver):
		
	if ver:
		msg = 'Plugin Update auf  Version {0}'.format(ver)
		msgH = 'Update erfolgreich - Plugin bitte neu starten'
		try:
			zip_data = Archive.ZipFromURL(url)
			#return ObjectContainer(header=msgH, message=msg)   # Test
			
			for name in zip_data.Names():
				data	= zip_data[name]
				parts   = name.split('/')
				shifted = Core.storage.join_path(*parts[1:])
				full	= Core.storage.join_path(Core.bundle_path, shifted)
				# full = '/tmp/Plex-Plugin-ARDMediathek2016.bundle'	# Test (sandbox - lässt Plex nicht zu)
				Log(full)

				if '/.' in name:
					continue
				# Verwendung 'Core' problembehaftet, bei Fehler 'Core ist not defined!' ist 
				# 	Elevated in Info.plist erforderlich  - s.a.
				# 	https://forums.plex.tv/discussion/34771/nameerror-global-name-core-is-not-defined
				
				if name.endswith('/'):	
					Core.storage.ensure_dirs(full)   
				else:	
					if Core.storage.file_exists(full):
						os.remove(full)
						Core.storage.save(full, data)
					else:
						Core.storage.save(full, data)
		except Exception as exception:
			msg = 'Error: ' + str(exception)
			msgH = 'Update fehlgeschlagen'
		
		try:
			os.remove(zip_data)
			Log('unzipped')
		except Exception as exception:
			pass
		
		return ObjectContainer(header=msgH, message=msg)
	else:
		return ObjectContainer(header='Update fehlgeschlagen', message='Version ' + ver + 'nicht gefunden!')

################################################################################
# @route(PREFIX + '/updateold')	
# def updateold(title, feed, ver):	# Funktion updateold nicht verwendet

	
# clean tag names based on your release naming convention
def cleanSummary(summary):
	summary = summary['value']
	summary = summary.replace('<p>','- ')
	summary = summary.replace('</p>','')
	summary = summary.replace('<ul>','-')
	summary = summary.replace('</ul>','')
	summary = summary.replace('<li>','- ')
	summary = summary.replace('</li>','')
	summary = summary.replace('\n',' ')
	summary = summary.replace('</br>',' ')
	summary = summary.replace('<br />',' - ')
	summary = summary.replace('<br/>',' - ')
	summary = summary.replace('&amp;','&')
	return summary.lstrip()
