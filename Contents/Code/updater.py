################################################################################
import re, urllib, os

FEED_URL = 'https://github.com/{0}/releases.atom'

################################################################################
TITLE = 'Plex-Plugin-Flickr'
GITHUB_REPOSITORY = 'rols1/Plex-Plugin-Flickr'
PREFIX = '/video/flickr'

# 09.10.2017: veraltetes releases.atom abgelöst durch api-url (Vorschlag @dane22)
################################################################################

# This gets the release name
def get_latest_version():
	try:
		release_feed_url = ('https://api.github.com/repos/{0}/releases/latest'.format(GITHUB_REPOSITORY))
		release_data = HTTP.Request(release_feed_url).content
		tag 	= stringextract('tag_name": "', '"', release_data)	# Version
		title	= stringextract('name": "', '"', release_data)		# Reponame
		summ	= stringextract('body": "', '"', release_data)		# Beschr.
		summ = (summ.replace('###','').replace('\\r\\n', " "))	# bei Bedarf erweitern

		zip_url = stringextract('browser_download_url": "', '"', release_data)
		Log(release_feed_url); Log(tag); Log(summ); Log(zip_url);
		return (title, summ, tag, zip_url)
	except Exception as exception:									# Github-Problem
		#Log.Error('Checking for new releases failed: {0}'.format(repr(exception)))
		Log.Error('Suche nach neuen Versionen fehlgeschlagen: {0}'.format(repr(exception))) 
		return (None, None, None)

################################################################################
def update_available(VERSION):
	try:
		title, summ, tag, zip_url = get_latest_version()	# summ=Beschr., tag=Name
		
		if tag:
			# wir verwenden auf Github die Versionierung nicht im Plugin-Namen
			# latest_version  = latest_version_str 
			latest_version  = tag			# Format hier: '1.4.1'
			current_version = VERSION
			int_lv = tag.replace('.','')	# Vergleichs-Format: 141
			int_lc = current_version.replace('.','')
			Log('Github: ' + latest_version); Log('lokal: ' + current_version); 
			# Log(int_lv); Log(int_lc)
			return (int_lv, int_lc, latest_version, summ, tag, zip_url)
	except:															# Github-Problem
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
				# 	https://forums.plex.tv/discussion/34771/nameerror-global-name-core-is-not-defined,
				#	Code intern: ../Framework/components/storage.py
				
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

#----------------------------------------------------------------  
def stringextract(mFirstChar, mSecondChar, mString):  	# extrahiert Zeichenkette zwischen 1. + 2. Zeichenkette
	pos1 = mString.find(mFirstChar)						# return '' bei Fehlschlag
	ind = len(mFirstChar)
	pos2 = mString.find(mSecondChar, pos1 + ind)		# ind+1 beginnt bei Leerstring um 1 Pos. zu weit
	rString = ''

	if pos1 >= 0 and pos2 >= 0:
		rString = mString[pos1+ind:pos2]	# extrahieren 
	return rString
