# -*- coding: utf-8 -*-
import string
import os 			# u.a. Behandlung von Pfadnamen
import re			# u.a. Reguläre Ausdrücke, z.B. in CalculateDuration
import datetime
import locale
import sys
import lxml.html 

import updater

# +++++ Plex-Plugin-Flickr +++++
VERSION =  '0.5.6'		
VDATE = '01.07.2018'

''' 
####################################################################################################
'''

# Copyright (c) 2017 Roland Scholz, rols1@gmx.de
#
# 
#   Functions -> README.md
# 
# 	Licensed under MIT License (MIT)
# 	(previously licensed under GPL 3.0)
# 	A copy of the License you find here:
#		https://github.com/rols1/Plex-Plugin-Flickr/blob/master/LICENSE.md
#
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING 
# BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND 
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
# OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT 
# OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.



####################################################################################################

NAME 				= 'Plex-Plugin-Flickr'
PREFIX				= '/video/flickr'			
												

ART 				= 'art-flickr.png'		# Hintergrund			
ICON_FLICKR 		= 'icon-flickr.png'						
ICON_SEARCH 		= 'icon-search.png'						


ICON_OK 			= "icon-ok.png"
ICON_WARNING 		= "icon-warning.png"
ICON_NEXT 			= "icon-next.png"
ICON_CANCEL 		= "icon-error.png"
ICON_MEHR 			= "icon-mehr.png"
ICON_MEHR_1 		= "icon-mehr_1.png"
ICON_MEHR_10 		= "icon-mehr_10.png"
ICON_MEHR_100 		= "icon-mehr_100.png"
ICON_MEHR_500 		= "icon-mehr_500.png"
ICON_WENIGER_1		= "icon-weniger_1.png"
ICON_WENIGER_10  	= "icon-weniger_10.png"
ICON_WENIGER_100 	= "icon-weniger_100.png"
ICON_WENIGER_500 	= "icon-weniger_500.png"

ICON_WORK 			= "icon-work.png"

ICON_GALLERY 		= "icon-gallery.png"

ICON_MAIN_UPDATER	= 'plugin-update.png'		
ICON_UPDATER_NEW 	= 'plugin-update-new.png'
ICON_INFO 			= "icon-info.png"

myhost 				= 'http://127.0.0.1:32400'

BASE 				= "https://www.flickr.com"
GALLERY_PATH 		= "https://www.flickr.com/photos/flickr/galleries/"
PHOTO_PATH 			= "https://www.flickr.com/photos/"

REPO_NAME 			= 'Plex-Plugin-Flickr'
GITHUB_REPOSITORY 	= 'rols1/' + REPO_NAME
REPO_URL 			= 'https://github.com/{0}/releases/latest'.format(GITHUB_REPOSITORY)

#----------------------------------------------------------------
def Start():
	Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
	Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
	Plugin.AddViewGroup("Pictures", viewMode="Pictures", mediaType="photos")
	
	ObjectContainer.art        = R(ART)  # Hintergrund
	ObjectContainer.title1     = NAME

	HTTP.CacheTime = CACHE_1HOUR 
	Dict.Reset()
	ValidatePrefs()
	Dict['nsid'] = ''		# belegt in MyMenu, Abgleich mit user_id

#----------------------------------------------------------------
def ValidatePrefs():
	Log('ValidatePrefs')
	try:
		lang = Prefs['language'].split('/') # Format Bsp.: "English/en/en_GB"
		loc 		= str(lang[1])		# de
	except:
		loc 		= 'en_GB'			# Fallback 
		
	MyContents = Core.storage.join_path(Core.bundle_path, 'Contents')	
	loc_file = Core.storage.abs_path(Core.storage.join_path(MyContents, 'Strings', '%s.json' % loc))
	# Log(loc_file)		
	if os.path.exists(loc_file):
		Locale.DefaultLocale = loc
	else:
		Locale.DefaultLocale = 'en-us'	# Fallback
		
	Dict['loc'] 		= loc
	Dict['loc_file'] 	= loc_file
	Log('loc: %s | loc_file: %s' % (loc,loc_file))
	return
	
#----------------------------------------------------------------
# handler bindet an das bundle
@route(PREFIX)
@handler(PREFIX, NAME, thumb = ICON_FLICKR)		# Thumb = Pluginsymbol
def Main():
	Log('Funktion Main'); Log(PREFIX); Log(VERSION); Log(VDATE)
	client_platform = str(Client.Platform)								# Client.Platform: None möglich
	client_product = str(Client.Product)								# Client.Product: None möglich
	Log('Client-Platform: ' + client_platform)							
	Log('Client-Product: ' + client_product)
											
	oc = ObjectContainer(view_group="InfoList", title1=NAME, title2='', art=ObjectContainer.art, no_cache=True)	
						
	title=L('Suche') + ': ' +  L('im oeffentlichen Inhalt')
	if 'Web' in client_product:
		# DirectoryObject ist Deko für das nicht sichtbare InputDirectoryObject dahinter:
		oc.add(DirectoryObject(key=Callback(Main),title=title, 
			summary=L('Suchbegriff im Suchfeld eingeben und Return druecken'), thumb=R(ICON_SEARCH)))

	oc.add(InputDirectoryObject(key=Callback(Search, title=title),
		title=title, prompt=L('Suche') + ' ' + L('Fotos'), thumb=R(ICON_SEARCH)))
		
	if Prefs['username']:
		summ = 'User: ' + Prefs['username']
		oc.add(DirectoryObject(key=Callback(MyMenu), title='MyFlickr',
			summary=summ, thumb=R('icon-my.png')))
			
	title=L('Photostream')								
	oc.add(DirectoryObject(key=Callback(Search_Work, query='None', user_id='None'), 
		title=title, summary=title, thumb=R('icon-stream.png')))
		
	title = L('Web Galleries')
	oc.add(DirectoryObject(key=Callback(WebGalleries, pagenr=1), title=title, thumb=R(ICON_GALLERY)))

	title = L('Flickr Nutzer')
	summ = L("Suche nach") + ': ' + Prefs['FlickrPeople']	
	oc.add(DirectoryObject(key=Callback(FlickrPeople, title), title=title, 
		summary=summ, thumb=R('icon-user.png')))
	
	# Menü Einstellungen (obsolet) ersetzt durch Info-Button
	summary = L('Stoerungsmeldungen an Forum oder rols1@gmx.de')
	oc.add(DirectoryObject(key = Callback(Main), title = 'Info', summary = summary, thumb = R(ICON_INFO)))
	
	# Updater-Modul einbinden:		
	oc = SearchUpdate(title=NAME, start='true', oc=oc)	

	return oc
	
####################################################################################################
@route(PREFIX + '/home')
# Doppelnutzung MyMenu:  Prefs['username'] + FlickrPeople 
#
# Rücksprung aus MyMenu/User				-> Main
# Rücksprung aus MyMenu/Prefs['username']	-> FlickrPeople
# Rücksprung aus Untermenüs	ohne user_id	-> Main
# Rücksprung aus Untermenüs	mit user_id		-> MyMenu 
#
def home(cont,user_id,username='', returnto=''):			# Home-Button, Aufruf: oc = home(cont=oc)
	Log('home')					# eingetragener User (Einstellungen)
	Log('user_id: %s, username: %s, returnto: %s' % (str(user_id), str(username), str(returnto)))	
	
	if returnto == 'FlickrPeople':				# MyMenu -> FlickrPeople 
		title = L('Zurueck zu') + ' ' + L('Flickr Nutzer')
		cont.add(DirectoryObject(key=Callback(FlickrPeople),
			title=title, thumb=R('homePeople.png')))	
		return cont
	if returnto == 'Main':
		title = L('Zurueck zum Hauptmenue')		# MyMenu -> Hauptmenue
		cont.add(DirectoryObject(key=Callback(Main),title=title, thumb=R('home.png')))			
		return cont

	if user_id:									# Untermenüs: User ( Prefs['username'] oder Flickr People)
		if username == '':
			user_id,nsid,username,realname = GetUserID(user_id) 					
		title = L('Zurueck zu') + ' ' + username
		cont.add(DirectoryObject(key=Callback(MyMenu, username=username,user_id=user_id),
			title=title, thumb=R('homePeople.png')))
		return cont
		
	title = L('Zurueck zum Hauptmenue')			# Untermenüs:  ohne user_id
	cont.add(DirectoryObject(key=Callback(Main),title=title, thumb=R('home.png')))

	return cont
	
####################################################################################################
# Userabhängige Menüs 
@route(PREFIX + '/MyMenu')
# 2-fache Verwendung:
#	1. Aufrufer Main 			- für den User aus Einstellungen Prefs['username']
#	2. Aufrufer FlickrPeople 	- für einen ausgewählten User aus FlickrPeople 
#
def MyMenu(username='',user_id=''):
	Log('MyMenu')
	Log('user_id: %s, username: %s' % (str(user_id), str(username)))	
		
	if username=='' and user_id=='':								# aus Main, User aus Einstellungen
		if Prefs['username']:								
			user = Prefs['username'].strip()
			user_id,nsid,username,realname = GetUserID(user) 
			# Ergebnis zusätzl. in Dicts (nicht bei ausgewählten usern (FlickrPeople):
			Dict['user_id']=user; Dict['nsid']=nsid; Dict['username']=username; Dict['realname']=realname
			Log('user_id: %s, nsid: %s, username: %s, realname: %s' % (user_id,nsid,username,realname))
			
			if 'User not found'	in user_id:							# err code aus GetUserID
				msg = L("User not found") + ': %s' % user	
				return ObjectContainer(header=L('Info'), message=msg)
				
	Log(Dict['nsid'])	
	nsid = user_id				
	if nsid == Dict['nsid']:	
		returnto ='Main' 
	else:
		returnto ='FlickrPeople' 	
	oc = ObjectContainer(view_group="InfoList", title2='MyMenu: %s' % username, art=ObjectContainer.art)
	oc = home(cont=oc, user_id=user_id, returnto=returnto)			# Home-Button -> Main / FlickrPeople		
	
	client_product = str(Client.Product)			# Client.Product: None möglich
	title='Search: content owned by %s' % (username)
	if 'Web' in client_product:
		# DirectoryObject ist Deko für das nicht sichtbare InputDirectoryObject dahinter:
		oc.add(DirectoryObject(key=Callback(Main),title=title, 
			summary=L('Suchbegriff im Suchfeld eingeben und Return druecken'), thumb=R(ICON_SEARCH)))

	oc.add(InputDirectoryObject(key=Callback(Search, user_id=nsid, title=title),
		title=title, prompt=L('Suche') + ' ' + L('Fotos'), thumb=R(ICON_SEARCH)))	
	
	title='%s: Photostream'	% username							
	oc.add(DirectoryObject(key=Callback(Search_Work, query='#Photostream#', user_id=nsid), 
		title=title, summary=title, thumb=R('icon-stream.png')))
				
	title='%s: Albums'	% username		
	oc.add(DirectoryObject(key=Callback(MyAlbums, title=title, user_id=nsid, pagenr=1), 
		title=title, summary=title, thumb=R('icon-album.png')))
				
	title='%s: Galleries'	% username		
	oc.add(DirectoryObject(key=Callback(MyGalleries, title=title, user_id=nsid), title=title,
		summary=title, thumb=R('icon-gallery.png')))
				
	title='%s: Faves'	% username		
	oc.add(DirectoryObject(key=Callback(Search_Work, query='#Faves#', user_id=nsid), 
		title=title, summary=title, thumb=R('icon-fav.png')))

	return oc
			
#------------------------------------------------------------------------------------------
# Begrenzung der Anzahl auf 100 festgelegt. Keine Vorgabe in Einstellungen, da Flickr unterschiedlich mit
#	den Mengen umgeht (seitenweise, einzeln, ohne). Z.B. in galleries.getList nur 1 Seite - Mehr-Sprünge daher
#	mit max_count=100.
#	Flickr-Ausgabe im xml-Format.
@route(PREFIX + '/MyGalleries')
def MyGalleries(title, user_id, offset=0):
	Log('MyGalleries'); Log('offset: ' + str(offset))
	offset = int(offset)
	title_org = title
	max_count = 100									# Begrenzung fest wie Flickr Default
	
	oc_title2 = title
	if offset:
		oc_title2 = title_org + ' | %s...' % offset			
	oc = ObjectContainer(view_group="InfoList", title2=oc_title2, art=ObjectContainer.art) #, no_cache=True)
	oc = home(cont=oc, user_id=user_id)	# Home-Button
	
	path = BuildPath(method='flickr.galleries.getList', query_flickr='', user_id=user_id, pagenr=1)
				
	page, msg = RequestUrl(CallerName='MyGalleries', url=path, mode='raw')
	if page == '': 
		return ObjectContainer(header=L('Info'), message=msg)			
	Log(page[:100])
		
	cnt = stringextract('total="', '"', page)		# im  Header
	pages = stringextract('pages="', '"', page)
	Log('Galleries: %s, Seiten: %s' % (cnt, pages))
	if cnt == '0':
		msg = L('Keine Gallerien gefunden')
		return ObjectContainer(header=L('Info'), message=msg)
		
	records = blockextract('<gallery id', '', page)
	pagemax = int(len(records))
	Log('total: ' + str(pagemax))
	
	i=0 + offset
	loop_i = 0		# Schleifenzähler
	# Log(records[i])
	for r in records:
		title 		= stringextract('<title>', '</title>', records[i])
		title		= unescape(title)
		title		= title.decode(encoding="utf-8")
		url 		= stringextract('url="', '"', records[i])
		username 	= stringextract('username="', '"', records[i])
		username	= username.decode(encoding="utf-8")
		count_photos = stringextract('count_photos="', '"', records[i])
		summ = '%s: %s %s' % (username, count_photos, L('Fotos'))
		img_src = R(ICON_FLICKR)
		i=i+1; loop_i=loop_i+1
		if i >= pagemax:
			break
		if loop_i > max_count:
			break
		
		gallery_id = url.split('/')[-1]		# Bsp. 72157697209149355
		if url.endswith('/'):
			gallery_id = url.split('/')[-2]	# Url-Ende bei FlickrPeople ohne / 	
				
		Log(i); Log(url);Log(title);Log(img_src); Log(gallery_id);
		oc.add(DirectoryObject(key=Callback(Gallery_single, title=title,  gallery_id=gallery_id, user_id=user_id),
				title=title, summary=summ, thumb=img_src))
				
	Log(offset); Log(pagemax); 					# pagemax hier Anzahl Galleries
	tag = 'total: %s ' % pagemax + L('Galerien')
	name = title_org
	if (int(offset)+100) < int(pagemax):
		offset = min(int(offset) +100, pagemax)
		Log(offset)
		oc.add(DirectoryObject(key=Callback(MyGalleries, title=title_org, offset=offset), 
			title=name, summary=L('Mehr (+ 100)'), tagline=tag, thumb=R(ICON_MEHR_100))) 
	# weniger
	if int(offset) > 100:
		offset = max(int(offset)-100-max_count, 0)
		Log(offset)
		oc.add(DirectoryObject(key=Callback(MyGalleries, title=title_org, offset=offset), 		
			title=name, summary=L('Weniger (- 100)'), tagline=tag, thumb=R(ICON_WENIGER_100)))  
							
	return oc
	
#------------------------------------------------------------------------------------------
# Bezeichnung in Flickr-API: Photosets
#	Mehrere Seiten - anders als MyGalleries
#	Flickr-Ausgabe im xml-Format.
@route(PREFIX + '/MyAlbums')
def MyAlbums(title, user_id, pagenr):
	Log('MyAlbums'); Log('page: ' + str(pagenr))
	title_org = title
	
	path = BuildPath(method='flickr.photosets.getList', query_flickr='', user_id=user_id, pagenr=pagenr)
				
	page, msg = RequestUrl(CallerName='MyAlbums', url=path, mode='raw')
	if page == '': 
		return ObjectContainer(header=L('Info'), message=msg)			
	Log(page[:100])
		
	pages = stringextract('pages="', '"', page)		# im  Header, Anz. Seiten
	alben_max = stringextract('total="', '"', page)		# im  Header
	perpage = stringextract('perpage="', '"', page)		# im  Header
	thispagenr = stringextract('page="', '"', page)		# im  Header, sollte pagenr entsprechen
	Log('Alben: %s, Seite: %s von %s, perpage: %s' % (alben_max, thispagenr, pages, perpage))
	
	if  pages == '0' or '<rsp stat="ok">' not in page:			
		msg = L('Keine Alben gefunden')
		return ObjectContainer(header=L('Info'), message=msg)
		
	name = '%s %s/%s' % (L('Seite'), pagenr, pages)	
	oc = ObjectContainer(view_group="InfoList", title2=name, art=ObjectContainer.art) #, no_cache=True)
	client = Client.Platform
	if client == None:
		client = ''
	if client.find('Plex Home Theater'): 
		oc = home(cont=oc,user_id=user_id)				# Home-Button macht bei PHT das PhotoObject unbrauchbar
	Log('Client: ' + client) 
			
	records = blockextract('<photoset id', '', page)
	Log('records: ' + str(len(records)))
	
	for rec in records:
		title 		= stringextract('<title>', '</title>', rec)
		title		= title.decode(encoding="utf-8")
		photoset_id	= stringextract('id="', '"', rec)
		description = stringextract('description="', '"', rec)
		count_photos = stringextract('photos="', '"', rec)
		secret =  stringextract('secret=\"', '\"', rec) 
		serverid =  stringextract('server=\"', '\"', rec) 
		farmid =  stringextract('farm=\"', '\"', rec) 	
					
		# Url-Format: https://www.flickr.com/services/api/misc.urls.html
		# thumb_src = 'https://farm%s.staticflickr.com/%s/%s_%s_z.jpg' % (farmid, serverid, photoset_id, secret)  # m=small (240)
		# Anforderung Url-Set in BuildPath -> BuildExtras
		thumb_src = stringextract('url_z="', '"', rec)	# z=640
		
		summ = "%s %s" % (count_photos, L('Fotos'))
		if description:
			summ = '%s | %s' % (count_photos, description)
		img_src = R(ICON_FLICKR)
		
		Log(title);Log(photoset_id);Log(thumb_src);
		oc.add(DirectoryObject(key=Callback(MyAlbumsSingle, title=title, photoset_id=photoset_id, user_id=user_id),
				title=title, summary=summ, thumb=thumb_src))
				
	# auf mehr prüfen:
	Log(pagenr); Log(pages);
	page_next = int(pagenr) + 1
	tag = 'total: %s %s' % (alben_max, L('Alben'))
	if (int(pagenr)+1) <= int(pages):
		oc.add(DirectoryObject(key=Callback(MyAlbums, title=title_org, user_id=user_id, pagenr=int(pagenr) +1), 
			title=name, summary=L('Mehr (+ 1)'), tagline=tag, thumb=R(ICON_MEHR_1)))
	if (int(pagenr)+10) < int(pages):
		oc.add(DirectoryObject(key=Callback(MyAlbums, title=title_org, user_id=user_id, pagenr=int(pagenr) +10), 
			title=name, summary=L('Mehr (+ 10)'), tagline=tag, thumb=R(ICON_MEHR_10)))  
	if (int(pagenr)+100) < int(pages):
		oc.add(DirectoryObject(key=Callback(MyAlbums, title=title_org, user_id=user_id, pagenr=int(pagenr) +100), 
			title=name, summary=L('Mehr (+ 100)'), tagline=tag, thumb=R(ICON_MEHR_100))) 
	# weniger
	if  int(pagenr) > 1:
		oc.add(DirectoryObject(key=Callback(MyAlbums, title=title_org, user_id=user_id, pagenr=int(pagenr)-1), 
			title=name, summary=L('Weniger (- 1)'), tagline=tag, thumb=R(ICON_WENIGER_1)))  
	if int(pagenr) > 10:
		oc.add(DirectoryObject(key=Callback(MyAlbums, title=title_org, user_id=user_id, pagenr=int(pagenr)-10), 
			title=name, summary=L('Weniger (- 10)'), tagline=tag, thumb=R(ICON_WENIGER_10)))  
	if int(pagenr) > 100:
		oc.add(DirectoryObject(key=Callback(MyAlbums, title=title_org, user_id=user_id, pagenr=int(pagenr)-100), 		
			title=name, summary=L('Weniger (- 100)'), tagline=tag, thumb=R(ICON_WENIGER_100)))  
							
	return oc
	
#------------------------------------------------------------------------------------------
# Bezeichnung in Flickr-API: Photosets
#	Mehrere Seiten - anders als MyGalleries
#	Flickr-Ausgabe im xml-Format.
# Seitensteuerung durch BuildPages (-> ShowPhotoObject)
@route(PREFIX + '/MyAlbumsSingle')
def MyAlbumsSingle(title, photoset_id, user_id, pagenr=1):
	Log('MyAlbumsSingle')
	
	path = BuildPath(method='flickr.photosets.getPhotos', query_flickr='', user_id=user_id, pagenr=1) 
	path = path + "&photoset_id=%s"  % (photoset_id)
				
	page, msg = RequestUrl(CallerName='MyAlbumsSingle', url=path, mode='raw')
	if page == '': 
		return ObjectContainer(header=L('Info'), message=msg)			
	Log(page[:100])
	pagemax		= stringextract('pages="', '"', page)
	perpage 	=  stringextract('perpage="', '"', page)	
	Log(pagemax)
	
	searchname = '#MyAlbumsSingle#'
	oc = BuildPages(title=title, searchname=searchname, SEARCHPATH=path, pagemax=pagemax, perpage=perpage, 
		pagenr=1)

	return oc
	
####################################################################################################
# --------------------------
#  	FlickrPeople:  gesucht wird auf der Webseite mit dem Suchbegriff fuer Menue Flickr Nutzer.
#	Flickr liefert bei Fehlschlag den angemeldeten Nutzer zurück
# 	Exaktheit der Websuche nicht beeinflussbar.	
#
@route(PREFIX + '/FlickrPeople')
def FlickrPeople(pagenr=1):
	Log('FlickrPeople'); Log('FlickrPeople: ' + str(Prefs['FlickrPeople']))
	Log('pagenr: ' + str(pagenr))
	pagenr = int(pagenr)
	
	if Prefs['FlickrPeople']:
		username = Prefs['FlickrPeople'].replace(' ', '%20')		# Leerz. -> url-konform 
		path = 'https://www.flickr.com/search/people/?username=%s&page=%s' % (username, pagenr)
	else:
		msg = L('Einstellungen: Suchbegriff für Flickr Nutzer fehlt')
		
		return ObjectContainer(header=L('Info'), message=msg)			
	
	title2 = 'Flickr People ' + L('Seite') + ' ' +  str(pagenr)
	oc = ObjectContainer(view_group="InfoList", title2=title2, art = ObjectContainer.art)
	oc = home(cont=oc, user_id='')								# Home-Button
				
	page, msg = RequestUrl(CallerName='FlickrPeople', url=path, mode='raw')
	if page == '': 
		return ObjectContainer(header=L('Info'), message=msg)			
	Log(page[:100])
	
	total = 0
	#  totalItems[2]  enthält die Anzahl. Falls page zu groß (keine weiteren 
	#	Ergebnisse), enthalten sie 0.
	try:
		totalItems =  re.findall(r'totalItems":(\d+)\}\]', page)  # Bsp. "totalItems":7}]
		Log(totalItems)
		total = int(totalItems[0])
	except Exception as exception:
		Log(str(exception))
	Log("total: " + str(total))
	
	records = blockextract('_flickrModelRegistry":"search-contact-models"', 'flickrModelRegistry', page)
	Log(len(records))
	
	thumb=R('icon-my.png')	
	i = 0					# loop count
	for rec in records:
		# Log(rec)
		# pathAlias =  stringextract('pathAlias":"', '"', rec) # pathAlias kann fehlen
		nsid =  stringextract('id":"', '"', rec) 
		if '@N' not in nsid:
				continue			
		username =  stringextract('username":"', '"', rec) 
		username = username.decode(encoding="utf-8")
		username = unescape(username)
		realname =  stringextract('realname":"', '"', rec) 
		iconfarm =  stringextract('iconfarm":"', '"', rec) 
		iconserver =  stringextract('iconserver":"', '"', rec) 
		followersCount =  stringextract('followersCount":', ',', rec) 
		if followersCount == '':
			followersCount  = '0'
		photosCount =  stringextract('photosCount":', ',', rec) 
		if photosCount == '':									# # photosCount kann fehlen
			photosCount  = '0'
		iconserver =  stringextract('iconserver":"', '"', rec) 
		Log("username: %s, nsid: %s"	% (username, nsid))
		title = "%s | %s" % (username, realname)
		title = title.decode(encoding="utf-8")
		summ = "%s: %s" % (L('Fotos'), photosCount)
		summ = summ + " | %s: %s" % (L('Followers'), followersCount)
		oc.add(DirectoryObject(key=Callback(MyMenu, username=username, user_id=nsid), 
			title=username, summary=summ, thumb=thumb))	
		i = i + 1
			
	if i == 0: 
		msg = Prefs['FlickrPeople'] + ': ' + L('kein Treffer')
		Log(msg)
		return ObjectContainer(header=L('Info'), message=msg)	
		
	# plus/minus 1 Seite:
	Log(pagenr * len(records)); Log(total)
	if (pagenr * len(records)) < total:
		title =  'FlickrPeople ' + L('Seite') + ' ' +  str(pagenr+1)
		oc.add(DirectoryObject(key=Callback(FlickrPeople, pagenr=pagenr+1), 
			title=title, summary=L('Mehr (+ 1)'),  thumb=R(ICON_MEHR_1)))	
	if 	pagenr > 1:	
		title =  'FlickrPeople ' + L('Seite') + ' ' +  str(pagenr-1)
		oc.add(DirectoryObject(key=Callback(FlickrPeople, pagenr=pagenr-1), 
			title=title, summary=L('Weniger (- 1)'),  thumb=R(ICON_WENIGER_1)))	
		
	return oc

####################################################################################################
# für Gallerie-Liste ohne user_id kein API-Call verfügbar - Auswertung der Webseite 
# Keine Sortierung durch Flickr möglich - i.G. zu MyGalleries (sort_groups)
@route(PREFIX + '/WebGalleries')
def WebGalleries(pagenr):
	Log('WebGalleries: pagenr=' + pagenr)
	if pagenr < 1:
		pagenr = 1
	path = GALLERY_PATH + 'page%s/' % (pagenr)		# Zusatz '?rb=1' nur in Watchdog erforderlich (302 Found)
	
	page, msg = RequestUrl(CallerName='WebGalleries: page %s' % pagenr, url=path, mode='raw')
	if page == '': 
		return ObjectContainer(header=L('Info'), message=msg)			
	Log(page[:50])
	
	gall_cnt = stringextract('class="Results">(', ' ', page) 		# Anzahl Galerien z.Z. 470 / 12 pro Seite
	pagemax = int(gall_cnt) / 12				# max. Seitenzahl = Anzahl Galerien / 12
	Log('pagemax: ' + str(pagemax)); 
	name = L('Seite') + ' ' +  str(pagenr) + L('von') + ' ' + str(pagemax)	
	oc = ObjectContainer(view_group="InfoList", title1=NAME, title2=name, art = ObjectContainer.art)
	oc = home(cont=oc, user_id='')								# Home-Button
	
	records = blockextract('gallery-hunk clearfix', '', page)  # oder gallery-case gallery-case-user	
	Log(len(records))
	for rec in records:					# Elemente pro Seite: 12
		# Log(rec)   		# bei Bedarf
		href = BASE + stringextract('href="', '">', rec) # Bsp. https://www.flickr.com/photos/flickr/galleries/72157697209149355/
		img_src = stringextract('src="', '"', rec)
		title = stringextract('title="', '"', rec)
		title = title.decode(encoding="utf-8", errors="ignore")
		nr_shown = stringextract('<p>', '</p>', rec)		# 1. Absatz: Anzahl, Bsp.: 15 photos
		nr_shown = mystrip(nr_shown) 
		gallery_id = href.split('/')[-2]		# Bsp. 72157697209149355
		Log(href);Log(img_src);Log(title);Log(nr_shown);Log(gallery_id);
		oc.add(DirectoryObject(key=Callback(Gallery_single, title=title, gallery_id=gallery_id, user_id=''),
				title=title, summary=nr_shown, thumb=img_src))
				
	# auf mehr prüfen:
	page_next = int(pagenr) + 1					# Pfad-Offset + 1
	path = GALLERY_PATH + 'page%s/' % (page_next)	
	Log(path); Log(pagenr); Log(gall_cnt); Log(pagemax)
	page = HTML.ElementFromURL(path)
	tag = 'total: %s' % gall_cnt + L('Galerien')
	liste = page.xpath("//*[@class='gallery-hunk clearfix']")  # oder <div class="gallery-case gallery-case-user">
	if len(liste) > 0:
		oc.add(DirectoryObject(key=Callback(WebGalleries, pagenr=int(pagenr)+1), 
			title=name, summary=L('Mehr (+ 1)'), tagline=tag, thumb=R(ICON_MEHR_1)))
		if (int(pagenr)+10) < pagemax:
			oc.add(DirectoryObject(key=Callback(WebGalleries, pagenr=int(pagenr)+10), 
				title=name, summary=L('Mehr (+ 10)'), tagline=tag, thumb=R(ICON_MEHR_10)))  
		if (int(pagenr)+100) < pagemax:
			oc.add(DirectoryObject(key=Callback(WebGalleries, pagenr=int(pagenr)+100), 
				title=name, summary=L('Mehr (+ 100)'), tagline=tag, thumb=R(ICON_MEHR_100))) 
	# weniger
	if  int(pagenr) > 1:
		oc.add(DirectoryObject(key=Callback(WebGalleries, pagenr=int(pagenr)-1), 
			title=name, summary=L('Weniger (- 1)'), tagline=tag, thumb=R(ICON_WENIGER_1)))  
		if int(pagenr) > 10:
			oc.add(DirectoryObject(key=Callback(WebGalleries, pagenr=int(pagenr)-10), 
				title=name, summary=L('Weniger (- 10)'), tagline=tag, thumb=R(ICON_WENIGER_10)))  
		if int(pagenr) > 100:
			oc.add(DirectoryObject(key=Callback(WebGalleries, pagenr=int(pagenr)-100), 		
				title=name, summary=L('Weniger (- 100)'), tagline=tag, thumb=R(ICON_WENIGER_100)))  	
	return oc
      
#------------------------------------------------------------------------------------------
# Erzeugt Foto-Objekte für WebGalleries + MyGalleries (Pfade -> Rückgabe im xml-Format).
# Die Thumbnails von Flickr werden nicht gebraucht - erzeugt Plex selbst aus den Originalen
# max. Anzahl Fotos in Galerie: 50 (https://www.flickr.com/help/forum/en-us/72157646468539299/)
#	z.Z. keine Steuerung mehr / weniger nötig
@route(PREFIX + '/Gallery_single')
def Gallery_single(title, gallery_id, user_id):		
	Log('Gallery_single: ' + gallery_id)
	oc = ObjectContainer(view_group="InfoList", title1=title, title2=title, art = ObjectContainer.art)
	client = Client.Platform
	if client == None:
		client = ''
	if client.find ('Plex Home Theater'): 
		oc = home(cont=oc, user_id=user_id)							# Home-Button macht bei PHT das PhotoObject unbrauchbar
	Log('Client: ' + client) 
		
	searchname = '#Gallery#'
	# pagenr hier weglassen - neu in BuildPages
	href = BuildPath(method='flickr.galleries.getPhotos', query_flickr='', user_id=user_id, pagenr='') 
	href = href + "&gallery_id=%s"  % (gallery_id)
	oc = BuildPages(title=title, searchname=searchname, SEARCHPATH=href, pagemax='?', perpage=1, 
		pagenr='?')

	return oc
		
####################################################################################################
# API-Format: https://api.flickr.com/services/rest/?method=flickr.photos.search&api_key=
#	24df437b03dd7bf070ba220aa717027e&text=Suchbegriff&page=3&format=rest
#	Rückgabeformat XML
# 
# Verwendet wird die freie Textsuche (s. API): Treffer möglich in Titel, Beschreibung + Tags
# Mehrere Suchbegriffe, getrennt durch Blanks, bewirken UND-Verknüpfung.
#
@route(PREFIX + '/Search')	
def Search(title, query=None, user_id=None, pagenr=1, **kwargs):
	Log('Search: ' + query); 
	# wir springen direkt - Ablauf:
	#	Search -> Search_Work -> BuildPages (Seitensteuerung) -> ShowPhotoObject
	ObjectContainer = Search_Work(query=query, user_id=user_id)	 
	return	ObjectContainer
	
# --------------------------	
@route(PREFIX + '/Search_Work')	
# Search_Work: ermöglicht die Flickr-Suchfunktion außerhalb der normalen Suchfunktion, z.B.
#	Photostream + Faves. Die normale Suchfunktion startet in Search, alle anderen hier.
# Ablauf: 
#	Search_Work -> BuildPages (Seitensteuerung) -> ShowPhotoObject
#
# query='#Suchbegriff#' möglich (MyMenu: MyPhotostream, MyFaves) - Behandl. in BuildPath
#  query='None' möglich (Photostream)
#
# URL's: viele Foto-Sets enthalten unterschiedliche Größen - erster Ansatz, Anforderung mit b=groß, 
#	schlug häufig fehl. Daher Anforderung mit einer Suffix-Liste (extras), siehe 
#	https://www.flickr.com/services/api/misc.urls.html, und Entnahme der "größten" URL. 
# 
def Search_Work(query, user_id, SEARCHPATH=''):		
	Log('Search_Work: ' + query); 		
	
	query_flickr = query.replace(' ', '%20')		# Leerz. -> url-konform 
	if query == '#Faves#':							# MyFaves
		SEARCHPATH = BuildPath(method='flickr.favorites.getList', query_flickr=query, user_id=user_id, pagenr='')
	else:
		# BuildPath liefert zusätzlich Dict['extras_list'] für Fotoauswahl (s.u.)
		SEARCHPATH = BuildPath(method='flickr.photos.search', query_flickr=query, user_id=user_id, pagenr='')
	Log(SEARCHPATH)
				  	
	if query == 'None':								# von Photostream
		searchname = L('Seite')		
	else:
		searchname = L('Suche') + ': ' + query + ' ' + L('Seite')
	if query.startswith('#') and query.endswith('#'):# von MyPhotostream / MyFaves
		searchname = query.replace('#', '')
		searchname =  L('Seite')					# Ergänzung in BuildPages
						
	oc = BuildPages(title=searchname, searchname=searchname, SEARCHPATH=SEARCHPATH, pagemax=1, perpage=1, pagenr='?')
		
	return oc
	
#---------------------------------------------------------------- 
@route(PREFIX + '/BuildPages')
# Ausgabesteuerung für Fotoseiten: Buttons für die einzelnen Seiten, einschl. Mehr/Weniger.
#	Falls nur 1 Seite vorliegt, wird ShowPhotoObject direkt angesteuert.
# Auslagerung ShowPhotoObject für PHT erforderlich (verträgt keine Steuer-Buttons) 
# searchname steuert Belegung von title2 des ObjectContainers - Eingefassung
#	 durch ## kennzeichnet: keine Suche
# perpage setzen wir wg. des PHT-Problems nicht bei der Fotoausgabe einer einzelnen 
#	Seite um - Flickr-Default hier 100.
# Bei Überschreitung der Seitenzahl (page) zeigt Flickr die letzte verfügbare Seite.
#
def BuildPages(title, searchname, SEARCHPATH, pagemax=1, perpage=1, pagenr=1):
	Log('BuildPages')
	Log('SEARCHPATH: %s' % (SEARCHPATH))
	Log(pagenr)
	title_org = title
	
	if pagenr == '?' or pagenr == '':							# Inhalt noch unbekannt
		page, msg = RequestUrl(CallerName='BuildPages', url=SEARCHPATH, mode='raw')
		if page == '': 
			return ObjectContainer(header=L('Info'), message=msg)			
		Log(page[:100])
		if  '<rsp stat="ok">' not in page or 'pages="0"' in page:			
			msg = 'Sorry, no hit.'
			return ObjectContainer(header=L('Info'), message=msg)

		pagemax		= stringextract('pages="', '"', page)
		photototal 	=  stringextract('total="', '"', page)		# z.Z. n.b.
		perpage 	=  stringextract('perpage="', '"', page)	# Flickr default: 100 pro Seite
		pagenr 		= 1											# Start mit Seite 
		Log('Flickr: pagemax %s, total %s, perpage %s' % (pagemax, photototal, perpage))
	
	pagenr = int(pagenr); pagemax = int(pagemax); 			
	maxPageContent = 500						# Maximum Flickr	
	if Prefs['maxPageContent']:					# Objekte pro Seite (Einstellungen)
		maxPageContent = int(Prefs['maxPageContent'])
		if maxPageContent <> int(perpage):
			Log('maxPageContent/perpage(%s) ungleich! Ev. Fotosuche' % perpage)
	if pagenr < 1:
		pagenr = 1
	pagenr = min(pagenr, pagemax)
	Log("Plugin: pagenr %d, maxPageContent %d, pagemax %d" % (pagenr, maxPageContent, pagemax))

	# Pfade ohne user_id möglich (z.B. Suche + Photostream  aus Main)
	try:
		user_id = re.search(u'user_id=(\d+)@N0(\d+)', SEARCHPATH).group(0)		#user_id=66956608@N06
		user_id = user_id.split('=')[1]
	except Exception as exception:
		Log(str(exception))
		user_id = ''
		
	# keine Suche - Bsp.  = '#Gallery#'	
	if searchname.startswith('#') and searchname.endswith('#'):	
		searchname = searchname.replace('#', '')
		searchname =  L('Seite')
	
	name = '%s %s/%s' % (searchname, pagenr, pagemax)	
	name = name.decode(encoding="utf-8", errors="ignore")
	oc = ObjectContainer(view_group="InfoList", title2=name, art = ObjectContainer.art)
	client = Client.Platform
	if client == None:
		client = ''
	if client.find ('Plex Home Theater'): 
		oc = home(cont=oc,user_id=user_id)				# Home-Button macht bei PHT das PhotoObject unbrauchbar
	Log('Client: ' + client) 
	
	pagemax = int(pagemax)
	if pagemax == 1:						# nur 1 Seite -> ShowPhotoObject direkt
		title = title + ' %s'  % 1			# Bsp. "scott wilson Seite 1"
		oc = ShowPhotoObject(title=title, path=SEARCHPATH)
		return oc 
			
	for i in range(pagemax):
		Log("i %d, pagenr %d" % (i, pagenr))
		title = L('Seite') + ': ' + str(pagenr)	
		# Anpassung SEARCHPATH an pagenr 
		path1 = SEARCHPATH.split('&page=')[0]	# vor + nach page trennen	
		path2 = SEARCHPATH.split('&page=')[1]
		pos = path2.find('&')					# akt. pagenr abschneiden
		path2 = path2[pos:]
		path = path1 + '&page=%s' %  str(pagenr) + path2 # Teil1 + Teil2 wieder verbinden
		# Log(path);  # Log(path1); Log(path2);
		oc.add(DirectoryObject(key=Callback(ShowPhotoObject, title=title, path=path),
			title=title, thumb=R('icon-next.png')))
			
		pagenr = pagenr + 1 
		if i >= maxPageContent-1:				# Limit Objekte pro Seite
			break			
		if pagenr >= pagemax+1:					# Limit Plugin-Seiten gesamt
			break	
			
	# auf mehr prüfen:	
	# Begrenzung max/min s.o.	
	Log(pagenr); Log(pagemax); Log(maxPageContent);
	tag = 'total: %s ' % pagemax + L('Seiten')
	if pagenr  <= pagemax:
		pagenr_next = pagenr
		title = L('Mehr (+ 1)')
		oc.add(DirectoryObject(key=Callback(BuildPages, title=title_org, searchname=searchname, SEARCHPATH=SEARCHPATH, 
			pagemax=pagemax, pagenr=pagenr_next), title=title, thumb=R(ICON_MEHR_1)))
	if pagenr + (9 * maxPageContent) <= pagemax:
		pagenr_next = pagenr + (10 * maxPageContent)
		title = L('Mehr (+ 10)')
		oc.add(DirectoryObject(key=Callback(BuildPages, title=title_org, searchname=searchname, SEARCHPATH=SEARCHPATH, 
			pagemax=pagemax, pagenr=pagenr_next), title=title, thumb=R(ICON_MEHR_10)))
	if pagenr + (99 * maxPageContent) <= pagemax:
		pagenr_next = pagenr + (100 * maxPageContent)
		title = L('Mehr (+ 100)')
		oc.add(DirectoryObject(key=Callback(BuildPages, title=title_org, searchname=searchname, SEARCHPATH=SEARCHPATH, 
			pagemax=pagemax, pagenr=pagenr_next), title=title, thumb=R(ICON_MEHR_100)))
	if pagenr + (499 * maxPageContent) <= pagemax:
		pagenr_next = pagenr + (500 * maxPageContent)
		title = L('Mehr (+ 500)')
		oc.add(DirectoryObject(key=Callback(BuildPages, title=title_org, searchname=searchname, SEARCHPATH=SEARCHPATH, 
			pagemax=pagemax, pagenr=pagenr_next), title=title, thumb=R(ICON_MEHR_500)))
	# weniger
	if  pagenr-1 > maxPageContent:			# maxPageContent = 1 Seite
		pagenr_next = pagenr - ( 2* maxPageContent)
		title = L('Weniger (- 1)')
		oc.add(DirectoryObject(key=Callback(BuildPages, title=title_org, searchname=searchname, SEARCHPATH=SEARCHPATH, 
			pagemax=pagemax, pagenr=pagenr_next), title=title, thumb=R(ICON_WENIGER_1)))
	if  pagenr-1 > (10 * maxPageContent):
		pagenr_next = pagenr - (10 * maxPageContent)
		title = L('Weniger (- 10)')
		oc.add(DirectoryObject(key=Callback(BuildPages, title=title_org, searchname=searchname, SEARCHPATH=SEARCHPATH, 
			pagemax=pagemax, pagenr=pagenr_next), title=title, thumb=R(ICON_WENIGER_10)))
	if  pagenr-1 > 100:
		pagenr_next =  pagenr - (100 * maxPageContent)
		title = L('Weniger (- 100)')
		oc.add(DirectoryObject(key=Callback(BuildPages, title=title_org, searchname=searchname, SEARCHPATH=SEARCHPATH, 
			pagemax=pagemax, pagenr=pagenr_next), title=title, thumb=R(ICON_WENIGER_100)))
	if  pagenr-1 > 500:
		pagenr_next =  pagenr - (500 * maxPageContent)
		title = L('Weniger (- 500)')
		oc.add(DirectoryObject(key=Callback(BuildPages, title=title_org, searchname=searchname, SEARCHPATH=SEARCHPATH, 
			pagemax=pagemax, pagenr=pagenr_next), title=title, thumb=R(ICON_WENIGER_500)))
				
	return oc
#---------------------------------------------------------------- 
@route(PREFIX + '/ShowPhotoObject')
#	ShowPhotoObject wegen PHT ausgelagert (veträgt beim PhotoObject keine weiteren
#		Menübuttons (Home, Mehr).
#	path muss die passende pagenr enthalten
#	An title wird die aktuelle Seitennummer (page) angehängt
def ShowPhotoObject(title, path):
	Log('ShowPhotoObject')
	# Log(path)
		
	page, msg = RequestUrl(CallerName='ShowPhotoObject', url=path, mode='raw')
	if page == '': 
		return ObjectContainer(header=L('Info'), message=msg)			
	Log(page[:100])								# Ergebnis im XML-Format, hier in strings verarbeitet
	pagenr		= stringextract('page="', '"', page)
	
	# Rückwärtssuche: user_id -> username + realname 
	#	1. user_id aus path ermitteln, 2.  Aufruf flickr.people.getInfo
	#	nur falls user_id bekannt - nicht bei den Publics (müsste via nsid bei
	#		jedem Satz ermittelt werden - zu zeitaufwendig bei 100 Sätzen)
	# 	Pfade ohne user_id möglich (z.B. Suche + Photostream  aus Main)
	try:
		user_id = re.search(u'user_id=(\d+)@N0(\d+)', path).group(0)		#user_id=66956608@N06
		user_id = user_id.split('=')[1]
	except Exception as exception:
		Log(str(exception))							
		user_id = ''

	username=''; realname=''; 
	if user_id and ('None' not in user_id):	 # 'None' = PHT-Dummy
		user_id,nsid,username,realname = GetUserID(user_id)		# User-Profil laden
	Log('user_id %s, username %s, realname %s'	% (user_id,username,realname))
		
	oc = ObjectContainer(view_group="InfoList", title2=title, art = ObjectContainer.art)
	client = Client.Platform
	if client == None:
		client = ''
	if client.find ('Plex Home Theater'): 
		oc = home(cont=oc,user_id=user_id, username=username)	# Home-Button macht bei PHT das PhotoObject unbrauchbar
	Log('Client: ' + client) 

	records = blockextract('<photo id', '', page)	# ShowPhotoObject:  nur '<photo id'-Blöcke zulässig 	
	Log('records: %s' % str(len(records)))
	extras_list = Dict['extras_list']
	Log(extras_list);   # Log(list)			# bei Bedarf
		
		
	image = 1
	for s in records:						
		pid =  stringextract('id=\"', '\"', s) 
		owner =  stringextract('owner=\"', '\"', s) 	
		secret =  stringextract('secret=\"', '\"', s) 
		serverid =  stringextract('server=\"', '\"', s) 
		farmid =  stringextract('farm=\"', '\"', s) 		
		title =  stringextract('title=\"', '\"', s)	
		
		if 	username:						# Ersatz owner durch username + realname	
			owner = username
			if realname:
				owner = "%s | %s" % (owner, realname)
		
		# Url-Format: https://www.flickr.com/services/api/misc.urls.html
		thumb_src = 'https://farm%s.staticflickr.com/%s/%s_%s_m.jpg' % (farmid, serverid, pid, secret)  # m=small (240)
		# Foto-Auswahl - jeweils das größte, je nach Voreinstellung (falls verfügbar):
		Imagesize = L('Bildgroesse') 
		if 'url_' in s:							# Favs ohne Url
			for i in range (len(extras_list)):			
				url_extra = extras_list[i]
				img_src = stringextract('%s=\"' % (url_extra), '\"', s) 
				suffix = url_extra[-2:] 		# z.B. _o von url_o, zusätzlich height + width ermitteln
				width = stringextract('width%s=\"' % (suffix), '\"', s)	  	# z.B. width_o
				height = stringextract('height%s=\"' % (suffix), '\"', s)  	# z.B. height_o
				# Log(url_extra); Log(img_src);Log(suffix);Log(width);Log(height);	# bei Bedarf
				if len(img_src) > 0:		# falls Format nicht vorhanden, weiter mit den kleineren Formaten
					Log(url_extra)
					break
			summ = owner + ' | ' + '%s: %s x %s' % (Imagesize, width, height)
		else:									# Favs-Url wie thumb_src ohne extra (m)
			img_src = 'https://farm%s.staticflickr.com/%s/%s_%s.jpg' % (farmid, serverid, pid, secret)
			summ = owner 						# falls ohne Größenangabe
			
		title = unescape(title)					# Web Client hat Probleme mit ausländ. Zeichen
		title = title.decode(encoding="utf-8")
		summ = summ.decode(encoding="utf-8")
		Log(title); Log(img_src); # Log(thumb_src);	Log(pid);Log(owner);	# bei Bedarf
		if img_src == '':			# Sicherung (PhotoObject braucht URL)
			continue		
	
		oc.add(PhotoObject(
			key=img_src,
			rating_key='%s.%s' % (Plugin.Identifier, 'Bild ' + str(image)),	# rating_key = eindeutige ID
			summary=summ,
			title=title,
			# thumb = thumb_src
			thumb = img_src			# Thumbnails unnötig - von Plex je nach Player selbst erzeugt.
			))
		image += 1

	return oc

#---------------------------------------------------------------- 
#  method: Flickr-API-Methode
#  pagenr muss Aufrufer beisteuern
def BuildPath(method, query_flickr, user_id, pagenr):
	Log('BuildPath: %s' % method)
	
	API_KEY = GetKey()	
	PATH = "https://api.flickr.com/services/rest/?method=%s&api_key=%s"  % (method,Dict['API_KEY'])	

	if user_id:									# None bei allg. Suche
		if 'None' not in user_id:				# PHT-Dummy
			# user_id = Dict['nsid']				# beliebige user_id aus FlickrPeople
			PATH =  PATH + "&user_id=%s" % (user_id)
		
	# Suchstring + Extras anfügen für Fotoabgleich - 
	#	s. https://www.flickr.com/services/api/flickr.photos.search.html
	if 'photos.search' in method or 'favorites.getList' in method or 'photosets.getList' in method or 'galleries.getPhotos'  in method:
		extras  = BuildExtras()					# einschl. Dict['extras_list'] für Fotoabgleich 
		if query_flickr.startswith('#') and query_flickr.endswith('#'):		# von MyPhotostream / MyFaves
			query_flickr = ''												# alle listen
		if 'photosets.getList' in method:									# primary_photo_extras statt extras
			PATH =  PATH + "&text=%s&page=%s&primary_photo_extras=%s&format=rest" % (query_flickr, pagenr, extras)
		else:
			PATH =  PATH + "&text=%s&page=%s&extras=%s&format=rest" % (query_flickr, pagenr, extras)
			
	if Prefs['sort_order']:					# Bsp. 1 / date-posted-desc
		val = Prefs['sort_order']
		nr = val.split('/')[0].strip	
		sortorder = val.split('/')[1].strip()
		PATH = '%s&sort=%s' % (PATH, sortorder)	
		
	if pagenr:
		PATH =  PATH + "&page=%s" % pagenr
	
	# per_page muss an letzter Stelle stehen (Änderung in BuildPages möglich)
	if Prefs['maxPageContent']:					# Objekte pro Seite
		PATH =  PATH + "&per_page=%s" % Prefs['maxPageContent']
	else:
		PATH =  PATH + "&per_page=%s" % 500		# API: Maximum
	Log(PATH) 
	return PATH    
#----------------------------------------------------------------  
def GetKey():
	if Dict['API_KEY']	== None:
		lines 		= Resource.Load('flickr_keys.txt')
		keys 		= lines.splitlines()
		API_KEY		= keys[0].split('=')[1]
		Dict['API_KEY']	= API_KEY.strip()
		# API_SECRET = keys[1].split('=')[1]
		# Dict['API_SECRET'] = API_SECRET.strip()
		Dict.Save()
		Log('flickr_keys.txt neu geladen')
	else:
		API_KEY		= Dict['API_KEY']
	
	return API_KEY
#----------------------------------------------------------------  
# Aufruf: MyMenu
# 3 Methoden: Suche nach user_id, Email, Username
def GetUserID(user):
	Log('GetUserID'); Log(str(user))
	
	API_KEY = GetKey()	
	if '@' in user:
		if '@N' in user:	# user_id (nsid)
			nsid_url = 'https://api.flickr.com/services/rest/?method=flickr.people.getInfo'
			nsid_url = nsid_url + '&user_id=%s' % user
		else:				# Email
			nsid_url = 'https://api.flickr.com/services/rest/?method=flickr.people.findByEmail'
			nsid_url = nsid_url + '&find_email=%s' % user
		url = nsid_url + '&api_key=%s' 	% (Dict['API_KEY'])
	else:
		nsid_url = 'https://api.flickr.com/services/rest/?method=flickr.people.findByUsername'
		url = nsid_url + '&api_key=%s&username=%s' 	% (Dict['API_KEY'], user)		
	page, msg = RequestUrl(CallerName='MyMenu: get nsid', url=url, mode='raw')
	Log(page[:100])
	if page == '': 
		return ObjectContainer(header=L('Info'), message=msg)
		
	if 'User not found'	in page:								# Flickr err code
		user_id = 'User not found'
	else:
		user_id		= stringextract('id="', '"', page)			# user_id / nsid i.d.R. identisch
	nsid 		= stringextract('nsid="', '"', page)
	username 	= stringextract('<username>', '</username>', page)
	realname 	= stringextract('<realname>', '</realname>', page)
	#	Dict['user_id'] = user_id								# Dicts nur für Flickr user (s. Mymenu)
	return user_id,nsid,username,realname
	
#----------------------------------------------------------------  
def BuildExtras():		# Url-Parameter für Bildgrößen - abh. von Einstellungen
	extras = "url_o,url_k,url_h,url_l,url_c,url_z"	# URL-Anforderung, sortiert von groß nach klein - Default
	# Breiten: o = Original, k=2048, h=1600, l=1024, c=800, z=640
	pref_max_width = Prefs['max_width']
	# pref_max_width = 1600		# Test
	if pref_max_width == "Originalbild":
		extras = "url_o,url_k,url_h,url_l,url_c,url_z"
	if pref_max_width == "2048":
		extras = "url_k,url_h,url_l,url_c,url_z"
	if pref_max_width == "1600":
		extras = "url_h,url_l,url_c,url_z"
	if pref_max_width == "1024":
		extras = "url_l,url_c,url_z"	
	if pref_max_width == "800":
		extras = "url_c,url_z"
	if pref_max_width == "640":
		extras = "url_z"
	
	Log(pref_max_width); Log(extras)
	extras_list = extras.split(",")						# Für Foto-Auswahl  in Suchergebnis
	Dict['extras_list'] = extras_list
	
	return extras
	
####################################################################################################
#	Hilfsfunktonen
#----------------------------------------------------------------  
@route(PREFIX + '/SearchUpdate')
def SearchUpdate(title, start, oc=None):		
	Log('SearchUpdate')
	
	if start=='true':									# Aufruf beim Pluginstart
		if Prefs['InfoUpdate'] == True:					# Hinweis auf neues Update beim Start des Plugins 
			oc,available = presentUpdate(oc,start)
			if available == 'no_connect':
				msgH = L('Fehler'); 
				msg = L('Github ist nicht errreichbar') +  ' - ' +  L('Bitte die Update-Anzeige abschalten')		
				# return ObjectContainer(header=msgH, message=msg)	# skip - das blockt das Startmenü
							
			if 	available == 'true':					# Update präsentieren
				return oc
		
		Log('InfoUpdate = False, no Check')				# Menü Plugin-Update zeigen														
		title = L('Plugin Update') + " | " + L('Plugin Version:') + VERSION + ' - ' + VDATE 	 
		summary=L('Suche nach neuen Updates starten')
		tagline=L('Bezugsquelle') + ': ' + REPO_URL			
		oc.add(DirectoryObject(key=Callback(SearchUpdate, title='Plugin-Update', start='false'), 
			title=title, summary=summary, tagline=tagline, thumb=R(ICON_MAIN_UPDATER)))
		return oc
		
	else:					# start=='false', Aufruf aus Menü Plugin-Update
		oc = ObjectContainer(title2=title, art=ObjectContainer.art)	
		oc,available = presentUpdate(oc,start)
		if available == 'no_connect':
			msgH = L('Fehler'); 
			msg = L('Github ist nicht errreichbar') 		
			return ObjectContainer(header=msgH, message=msg)
		else:
			return oc	
			
#-----------------------------
def presentUpdate(oc,start):
	Log('presentUpdate')
	ret = updater.update_available(VERSION)			# bei Github-Ausfall 3 x None
	Log(ret)
	int_lv = ret[0]			# Version Github
	int_lc = ret[1]			# Version aktuell
	latest_version = ret[2]	# Version Github, Format 1.4.1

	if ret[0] == None or ret[0] == False:
		return oc, 'no_connect'
		
	zip_url = ret[5]	# erst hier referenzieren, bei Github-Ausfall None
	url = zip_url
	summ = ret[3]			# History, replace ### + \r\n in get_latest_version, summ -> summary, 
	tag = summ.decode(encoding="utf-8", errors="ignore")  # History -> tag
	Log(latest_version); Log(int_lv); Log(int_lc); Log(tag); Log(zip_url); 
	
	if int_lv > int_lc:								# 2 Update-Button: "installieren" + "abbrechen"
		available = 'true'
		title = L('neues Update vorhanden') +  ' - ' + L('jetzt installieren')
		summary = L('Plugin Version:') + " " + VERSION + ', Github Version: ' + latest_version

		oc.add(DirectoryObject(key=Callback(updater.update, url=url , ver=latest_version), 
			title=title, summary=summary, tagline=tag, thumb=R(ICON_UPDATER_NEW)))
			
		if start == 'false':						# Option Abbrechen nicht beim Start zeigen
			oc.add(DirectoryObject(key = Callback(Main), title = L('Update abbrechen'),
				summary = L('weiter im aktuellen Plugin'), thumb = R(ICON_UPDATER_NEW)))
	else:											# Plugin aktuell -> Main
		available = 'false'
		if start == 'false':						# beim Start unterdrücken
			oc.add(DirectoryObject(key = Callback(Main), 	
				title = L('Plugin aktuell') + " | Home",
				summary = 'Plugin Version ' + VERSION + ' ' + L('ist die neueste Version'),
				tagline = tag, thumb = R(ICON_OK)))			

	return oc,available
	
#----------------------------------------------------------------  
# RequestUrl bei Bedarf erweitern 
def RequestUrl(CallerName, url, mode='raw'):
	page=''; msg=''
	try:															
		Log("RequestUrl: called from %s, mode=%s" % (CallerName, mode))	
		if mode	== 'raw':
			page = HTTP.Request(url, cacheTime=1).content
		if mode	== 'html':
			page = HTML.ElementFromURL(url)
		if mode	== 'xml':
			page = XML.ElementFromURL(url)
		if 'phx fehler:' in page:					# Bsp. phx fehler: template "rubrik_overview_jso" not found
			msg = page
			page = ''
	except Exception as exception:
		msg = "RequestUrl: %s: " % CallerName  + repr(exception) 
		msg = msg + ' | ' + url				 			 	 
		Log(msg)
		page=''
		
	return page, msg
#----------------------------------------------------------------  
# Bsp.: # href = stringextract('', '', rec)	
def stringextract(mFirstChar, mSecondChar, mString):  	# extrahiert Zeichenkette zwischen 1. + 2. Zeichenkette
	pos1 = mString.find(mFirstChar)						# return '' bei Fehlschlag
	ind = len(mFirstChar)
	#pos2 = mString.find(mSecondChar, pos1 + ind+1)		
	pos2 = mString.find(mSecondChar, pos1 + ind)		# ind+1 beginnt bei Leerstring um 1 Pos. zu weit
	rString = ''

	if pos1 >= 0 and pos2 >= 0:
		rString = mString[pos1+ind:pos2]	# extrahieren 
		
	#Log(mString); Log(mFirstChar); Log(mSecondChar); 	# bei Bedarf
	#Log(pos1); Log(ind); Log(pos2);  Log(rString); 
	return rString
#----------------------------------------------------------------  
def teilstring(zeile, startmarker, endmarker):  		# return '' bei Fehlschlag
  # die übergebenen Marker bleiben Bestandteile der Rückgabe (werden nicht abgeschnitten)
  pos2 = zeile.find(endmarker, 0)
  pos1 = zeile.rfind(startmarker, 0, pos2)
  if pos1 & pos2:
    teils = zeile[pos1:pos2+len(endmarker)]	# Versatz +5 schneidet die begrenzenden Suchstellen ab 
  else:
    teils = ''
  #Log(pos1) Log(pos2) 
  return teils
#----------------------------------------------------------------  
def blockextract(blockmark, blockendmark, mString):  # extrahiert Blöcke begrenzt durch blockmark aus mString
	#   Block wird durch blockendmark begrenzt, falls belegt 
	#	blockmark bleibt Bestandteil der Rückgabe
	#	Verwendung, wenn xpath nicht funktioniert (Bsp. Tabelle EPG-Daten www.dw.com/de/media-center/live-tv/s-100817)
	rlist = []				
	if 	blockmark == '' or 	mString == '':
		Log('blockextract: blockmark or mString leer')
		return rlist
	
	pos = mString.find(blockmark)
	if 	mString.find(blockmark) == -1:
		Log('blockextract: blockmark nicht in mString enthalten')
		# Log(pos); Log(blockmark);Log(len(mString));Log(len(blockmark));
		return rlist
		
	pos2 = 1
	while pos2 > 0:
		pos1 = mString.find(blockmark)						
		ind = len(blockmark)
		pos2 = mString.find(blockmark, pos1 + ind)		
		
		if blockendmark:
			pos3 = mString.find(blockendmark, pos1 + ind)
			ind_end = len(blockendmark)
			block = mString[pos1:pos3+ind_end]	# extrahieren einschl.  blockmark + blockendmark
			# Log(block)			
		else:
			block = mString[pos1:pos2]			# extrahieren einschl.  blockmark
			# Log(block)		
		mString = mString[pos2:]	# Rest von mString, Block entfernt
		rlist.append(block)
		# Log(rlist)
	# Log(rlist)		
	return rlist  
#----------------------------------------------------------------  
def repl_dop(liste):	# Doppler entfernen, im Python-Script OK, Problem in Plex - s. PageControl
	mylist=liste
	myset=set(mylist)
	mylist=list(myset)
	mylist.sort()
	return mylist
#----------------------------------------------------------------  
def transl_umlaute(line):	# Umlaute übersetzen, wenn decode nicht funktioniert
	line_ret = line
	line_ret = line_ret.replace("Ä", "Ae", len(line_ret))
	line_ret = line_ret.replace("ä", "ae", len(line_ret))
	line_ret = line_ret.replace("Ü", "Ue", len(line_ret))
	line_ret = line_ret.replace('ü', 'ue', len(line_ret))
	line_ret = line_ret.replace("Ö", "Oe", len(line_ret))
	line_ret = line_ret.replace("ö", "oe", len(line_ret))
	line_ret = line_ret.replace("ß", "ss", len(line_ret))	
	return line_ret
#----------------------------------------------------------------  
def repl_char(cut_char, line):	# problematische Zeichen in Text entfernen, wenn replace nicht funktioniert
	line_ret = line				# return line bei Fehlschlag
	pos = line_ret.find(cut_char)
	while pos >= 0:
		line_l = line_ret[0:pos]
		line_r = line_ret[pos+len(cut_char):]
		line_ret = line_l + line_r
		pos = line_ret.find(cut_char)
		#Log(cut_char); Log(pos); Log(line_l); Log(line_r); Log(line_ret)	# bei Bedarf	
	return line_ret
#----------------------------------------------------------------  	
def unescape(line):	# HTML-Escapezeichen in Text entfernen, bei Bedarf erweitern. ARD auch &#039; statt richtig &#39;
	line_ret = (line.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
		.replace("&#39;", "'").replace("&#039;", "'").replace("&quot;", '"').replace("&#x27;", "'")
		.replace("&ouml;", "ö").replace("&auml;", "ä").replace("&uuml;", "ü").replace("&szlig;", "ß")
		.replace("&Ouml;", "Ö").replace("&Auml;", "Ä").replace("&Uuml;", "Ü").replace("&apos;", "'")
		.replace("&copy;", "®"))
		
	# Log(line_ret)		# bei Bedarf
	return line_ret	
#----------------------------------------------------------------  	
def mystrip(line):	# Ersatz für unzuverlässige strip-Funktion
	line_ret = line	
	line_ret = line.replace('\t', '').replace('\n', '').replace('\r', '')
	line_ret = line_ret.strip()	
	# Log(line_ret)		# bei Bedarf
	return line_ret
#----------------------------------------------------------------  	
def cleanhtml(line): # ersetzt alle HTML-Tags zwischen < und >  mit 1 Leerzeichen
	cleantext = line
	cleanre = re.compile('<.*?>')
	cleantext = re.sub(cleanre, ' ', line)
	return cleantext
#----------------------------------------------------------------  	
# Locale-Probleme - Lösung czukowski
def L(string):		
	local_string = Locale.LocalString(string)
	local_string = str(local_string).decode()
	# Log(string); Log(local_string)
	return local_string
#----------------------------------------------------------------  	

