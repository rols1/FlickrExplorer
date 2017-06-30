# -*- coding: utf-8 -*-
import string
import os 			# u.a. Behandlung von Pfadnamen
import re			# u.a. Reguläre Ausdrücke, z.B. in CalculateDuration
import datetime
import locale

import updater


# +++++ Plex-Plugin-Flickr +++++
VERSION =  '0.4.4'		
VDATE = '30.06.2017'

''' 


####################################################################################################
'''

# (c) 2016 by Roland Scholz, rols1@gmx.de
#	
# 
#     
# 
# Licensed under the GPL, Version 3.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#  
#    http://www.gnu.org/licenses/gpl-3.0-standalone.html
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


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
ICON_WENIGER_1		= "icon-weniger_1.png"
ICON_WENIGER_10  	= "icon-weniger_10.png"
ICON_WENIGER_100 	= "icon-weniger_100.png"

ICON_WORK 			= "icon-work.png"

ICON_GALLERY 		= "icon-gallery.png"

ICON_MAIN_UPDATER	= 'plugin-update.png'		
ICON_UPDATER_NEW 	= 'plugin-update-new.png'
ICON_PREFS = 'plugin-preferences.png'

REPO_NAME 			= 'Plex-Plugin-Flickr'
GITHUB_REPOSITORY 	= 'rols1/' + REPO_NAME
myhost 				= 'http://127.0.0.1:32400'

BASE 				= "https://www.flickr.com"
GALLERY_PATH 		= "https://www.flickr.com/photos/flickr/galleries/"
PHOTO_PATH 			= "https://www.flickr.com/photos/"


def Start():
	Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
	Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
	Plugin.AddViewGroup("Pictures", viewMode="Pictures", mediaType="photos")
	
	ObjectContainer.art        = R(ART)  # Hintergrund
	ObjectContainer.title1     = NAME

	HTTP.CacheTime = CACHE_1HOUR # Debugging: falls Logdaten ausbleiben, Browserdaten löschen

#----------------------------------------------------------------
# handler bindet an das bundle
@route(PREFIX)
@handler(PREFIX, NAME, thumb = ICON_FLICKR)		# Thumb = Pluginsymbol
def Main():
	Log('Funktion Main'); Log(PREFIX); Log(VERSION); Log(VDATE)
	Log('Client: '); Log(Client.Platform)
	oc = ObjectContainer(view_group="InfoList", art=ObjectContainer.art)	
						
	name = "Flickr"													
	# folgendes DirectoryObject ist Deko für das nicht sichtbare InputDirectoryObject dahinter:
	oc.add(DirectoryObject(key=Callback(Main),title='Suche: im Suchfeld eingeben', 
		summary='', tagline='Fotos', thumb=R(ICON_SEARCH)))
	oc.add(InputDirectoryObject(key=Callback(Search, s_type='picture', title=u'%s' % L('Search Picture')),
		title=u'%s' % L('Suche'), prompt=u'%s' % L('Search Picture'), thumb=R(ICON_SEARCH)))
		
	oc.add(DirectoryObject(key=Callback(Galleries_all, pagenr=1), title='Galerien',
		summary='', tagline='Galerien', thumb=R(ICON_GALLERY)))

	repo_url = 'https://github.com/{0}/releases/'.format(GITHUB_REPOSITORY)
	call_update = False
	if Prefs['pref_info_update'] == True:				# Hinweis auf neues Update beim Start des Plugins 
		ret = updater.update_available(VERSION)
		int_lv = ret[0]			# Version Github
		int_lc = ret[1]			# Version aktuell
		latest_version = ret[2]	# Version Github, Format 1.4.1
		
		if int_lv > int_lc:								# Update-Button "installieren" zeigen
			call_update = True
			title = 'neues Update vorhanden - jetzt installieren'
			summary = 'Plugin aktuell: ' + VERSION + ', neu auf Github: ' + latest_version
			url = 'https://github.com/{0}/releases/download/{1}/{2}.bundle.zip'.format(GITHUB_REPOSITORY, latest_version, REPO_NAME)
			oc.add(DirectoryObject(key=Callback(updater.update, url=url , ver=latest_version), 
				title=title, summary=summary, tagline=cleanhtml(summary), thumb=R(ICON_UPDATER_NEW)))
	if call_update == False:							# Update-Button "Suche" zeigen	
		title = 'Plugin-Update | akt. Version: ' + VERSION + ' vom ' + VDATE	
		summary='Suche nach neuen Updates starten'
		tagline='Bezugsquelle: ' + repo_url			
		oc.add(DirectoryObject(key=Callback(SearchUpdate, title='Plugin-Update'), 
			title=title, summary=summary, tagline=tagline, thumb=R(ICON_MAIN_UPDATER)))
		
	oc.add(DirectoryObject(key = Callback(Main_Options, title='Einstellungen'), title = 'Einstellungen', 
		summary = 'Fotosuche: maximale Bildbreite', 
		thumb = R(ICON_PREFS)))
	return oc
	
#----------------------------------------------------------------
def home(cont):									# Home-Button, Aufruf: oc = home(cont=oc)			
	#title = 'Zurück zum Hauptmenü'.decode(encoding="utf-8", errors="ignore")
	title = 'Zurück zum Anfang'.decode(encoding="utf-8", errors="ignore")
	summary = 'Zurück zum Anfang'.decode(encoding="utf-8", errors="ignore")
	cont.add(DirectoryObject(key=Callback(Main),title=title, summary=summary, tagline=NAME, thumb=R('home.png')))

	return cont
	
####################################################################################################
@route(PREFIX + '/SearchUpdate')
def SearchUpdate(title):		#
	oc = ObjectContainer(view_group="InfoList", art=ObjectContainer.art)	

	ret = updater.update_available(VERSION)	
	Log(ret)
	if ret[0] == False:		
		msg = 'Updater: Github-Problem'
		msgH = 'update_available: False'
		Log(msg)
		return ObjectContainer(header=msgH, message=msg)

	int_lv = ret[0]			# Version Github
	int_lc = ret[1]			# Version aktuell
	latest_version = ret[2]	# Version Github, Format 1.4.1
	summ = ret[3]			# Plugin-Name
	tag = ret[4]			# History (last change) )
	
	url = 'https://github.com/{0}/releases/download/{1}/{2}.bundle.zip'.format(GITHUB_REPOSITORY, latest_version, REPO_NAME)
	Log(latest_version); Log(int_lv); Log(int_lc); Log(url); 
	
	if int_lv > int_lc:		# zum Testen drehen (akt. Plugin vorher sichern!)
		oc.add(DirectoryObject(
			key = Callback(updater.update, url=url , ver=latest_version), 
			title = 'Update vorhanden - jetzt installieren',
			summary = 'Plugin aktuell: ' + VERSION + ', neu auf Github: ' + latest_version,
			tagline = summ,
			thumb = R(ICON_UPDATER_NEW)))
			
		oc.add(DirectoryObject(
			key = Callback(Main), 
			title = 'Update abbrechen',
			summary = 'weiter im aktuellen Plugin',
			thumb = R(ICON_UPDATER_NEW)))
	else:	
		oc.add(DirectoryObject(
			#key = Callback(updater.menu, title='Update Plugin'), 
			key = Callback(Main), 
			title = 'Plugin ist aktuell', 
			summary = 'Plugin Version ' + VERSION + ' ist aktuell (kein Update vorhanden)',
			tagline = 'weiter zum aktuellen Plugin',
			thumb = R(ICON_OK)))
			
	return oc
	
####################################################################################################
@route(PREFIX + '/Main_Options')
# DumbTools (https://github.com/coder-alpha/DumbTools-for-Plex) getestet, aber nicht verwendet - wiederholte 
#	Aussetzer bei Aufrufen nach längeren Pausen (mit + ohne secure-Funktion)

def Main_Options(title):
	Log('Funktion Main_Options')	
	Log(Prefs['pref_max_width']); 
	
	# hier zeigt Plex die Einstellungen (Entwicklervorgabe in DefaultPrefs.json):
	# 	http://127.0.0.1:32400/:/plugins/com.plexapp.plugins.flickr/prefs
	#	geänderte Daten legt Plex persistent ab (nicht in DefaultPrefs.json) - Löschen nur 
	#	möglich mit Löschen des Caches (Entfernen ../Caches/com.plexapp.plugins.flickr)
	myplugin = Plugin.Identifier
	data = HTTP.Request("%s/:/plugins/%s/prefs" % (myhost, myplugin), # als Text, nicht als HTML-Element
						immediate=True).content 
	
	# Zeilenaufbau
	#	1. Zeile "<?xml version='1.0' encoding='utf-8'?>"
	#	2. Zeile (..identifier="com.plexapp.plugins.ardmediathek2016"..) 
	#   ab 3.Zeile Daten
	# Log(data)
	myprefs = data.splitlines() 
	Log(myprefs)
	myprefs = myprefs[2:-1]		# letzte Zeile + Zeilen 1-2 entfernen 
		
	oc = ObjectContainer(no_cache=True, view_group="InfoList", title1='Einstellungen')
	oc = home(cont=oc)				# Home-Button - in den Untermenüs Rücksprung hierher zu Einstellungen 
	for i in range (len(myprefs)):
		do = DirectoryObject()
		element = myprefs[i]		# Muster: <Setting secure="false" default="true" value="true" label=...
		Log(element)
		secure = stringextract('secure=\"', '\"', element)		# nicht verwendet
		default = stringextract('default=\"', '\"', element)	# Vorgabe
		id = stringextract('id=\"', '\"', element)
		value = stringextract('value=\"', '\"', element)		# akt. Wert (hier nach dem Setzen nicht mehr aktuell)
		pref_value = Prefs[id]									# akt. Wert via Prefs - OK
		label = stringextract('label=\"', '\"', element)
		values = stringextract('values=\"', '\"', element)
		mytype = stringextract('type=\"', '\"', element)
		Log(secure);Log(default);Log(label);Log(values);Log(mytype); Log(id);
		Log(pref_value);
		if mytype == 'bool':										# lesbare Anzeige (statt bool, true, false)
			#oc_type = '| JA / NEIN | aktuell: '
			if str(pref_value).lower() == 'true':
				oc_wert = 'JA'
				oc_type = '| für NEIN  klicken | aktuell: '
			else:
				oc_wert = 'NEIN'
				oc_type = '| für JA  klicken | aktuell: '
		if mytype == 'enum':
			#oc_type = '|  Aufzählung | aktuell: '
			oc_type = '|  für Liste klicken | aktuell: '
			oc_wert = pref_value
		if mytype == 'text':
			oc_type = '| Texteingabe | aktuell: '
			oc_wert = pref_value
		title = u'%s  %s  %s' % (label, oc_type, oc_wert)
		title = title.decode(encoding="utf-8", errors="ignore")
		Log(title); Log(mytype)

		if mytype == 'bool':
			Log('mytype == bool')	
			do.key = Callback(Set, key=id, value=not Prefs[id], oc_wert=not Prefs[id]) 	# Wert direkt setzen (groß/klein egal)		
		if mytype == 'enum':
			do.key = Callback(ListEnum, id=id, label=label, values=values)			# Werte auflisten
		elif mytype == 'text':														# Eingabefeld für neuen Wert (Player-abhängig)
			oc = home(cont=oc)							# Home-Button	
			oc.add(InputDirectoryObject(key=Callback(SetText, id=id), title=title), title=title)
			continue
			
		do.title = title
		oc.add(do)			
		
	return oc
#------------
@route(PREFIX + '/ListEnum')
def ListEnum(id, label, values):
	Log(ListEnum); Log(id); 
	label = label.decode(encoding="utf-8", errors="ignore")
	oc = ObjectContainer(no_cache=True, view_group="InfoList", title1=label)	
	title = 'zurück zu den Einstellungen'.decode(encoding="utf-8", errors="ignore")		# statt Home-Button	
	oc.add(DirectoryObject(key = Callback(Main_Options, title=title), title = title, 
		summary = title, 
		thumb = R(ICON_PREFS)))
	values = values.split('|') 
	Log(values);
	for i in range(len(values)):
		pref = values[i]
		oc_wert = pref
		Log('value: ' + str(i) + ' Wert: ' + oc_wert)
		oc.add(DirectoryObject(key=Callback(Set, key=id, value=i, oc_wert=oc_wert), title = u'%s' % (pref)))				
	return oc
#------------
@route(PREFIX + '/SetText')
def SetText(query, id):
	return Set(key=id, value=query, oc_wert=oc_wert)
#------------
@route(PREFIX + '/Set')
def Set(key, value, oc_wert):
	Log('Set: key, value ' + key + ', ' + value); 
	#oc_wert = value
	if str(value).lower() == 'true':
		oc_wert = 'JA'
	if str(value).lower() == 'false':
		oc_wert = 'NEIN'

	oc = ObjectContainer(no_cache=True, view_group="InfoList", title1='eingestellt auf: ' + oc_wert)	
	title = 'zurück zu den Einstellungen'.decode(encoding="utf-8", errors="ignore")		# statt Home-Button	
	oc.add(DirectoryObject(key = Callback(Main_Options, title=title), title = title, 
		summary = title, 
		thumb = R(ICON_PREFS)))
	
	# Bsp.: http://127.0.0.1:32400/:/plugins/com.plexapp.plugins.flickr/prefs/set?pref_max_width=1600
	HTTP.Request("%s/:/plugins/%s/prefs/set?%s=%s" % (myhost, Plugin.Identifier, key, value), immediate=True)
	#return ObjectContainer()
	return oc
#--------------------------------
def ValidatePrefs():
	Log('ValidatePrefs')
	#Dict.Save()	# n.b. - Plex speichert in Funktion Set, benötigt trotzdem Funktion ValidatePrefs im Plugin
	return
	
####################################################################################################
@route(PREFIX + '/Galleries_all')
def Galleries_all(pagenr):
	Log('Galleries_all: pagenr=' + pagenr)
	if pagenr < 1:
		pagenr = 1
	path = "https://www.flickr.com/photos/flickr/galleries/page%s/" % (pagenr)
	path = GALLERY_PATH + 'page%s/' % (pagenr)
	page = HTML.ElementFromURL(path)
	s = XML.StringFromElement(page)
	#gall_cnt = stringextract('class=\"Results\">', '</div>', s) 	# Anzahl Galerien z.Z. 470 / 12 pro Seite
	gall_cnt = stringextract('class=\"Results\">(', ' ', s) 		# Anzahl Galerien z.Z. 470 / 12 pro Seite
	pagemax = int(gall_cnt) / 12				# max. Seitenzahl = Anzahl Galerien / 12
	name = 'Galerien (%s), Seite %s von %s' % (gall_cnt, pagenr, pagemax)
	name = name.decode(encoding="utf-8", errors="ignore")
	oc = ObjectContainer(view_group="InfoList", title1=NAME, title2=name, art = ObjectContainer.art)
	oc = home(cont=oc)								# Home-Button
	
	list = page.xpath("//*[@class='gallery-hunk clearfix']")  # oder <div class="gallery-case gallery-case-user">	
	Log(page); Log(list)
	for element in list:					# Elemente pro Seite: 12
		s = HTML.StringFromElement(element)
		# Log(element); 	Log(s)   		# bei Bedarf
		href = BASE + stringextract('href=\"', '\">', s) 
		img_src = stringextract('src=\"', '\"', s)
		img_alt = stringextract('alt=\"', '\"', s)
		img_alt = img_alt.decode(encoding="utf-8", errors="ignore")
		nr_shown = stringextract('<p>', '</p>', s)		# 1. Absatz: Anz. gesehener Fotos
		nr_shown = mystrip(nr_shown) 
		Log(href);Log(img_src);Log(img_alt);Log(nr_shown);
		oc.add(DirectoryObject(key=Callback(Gallery_single, title=img_alt, path=href),
				title=img_alt, summary=nr_shown, tagline='', thumb=img_src))
				
	# auf mehr prüfen:
	page_next = int(pagenr) + 1					# Pfad-Offset + 1
	path = GALLERY_PATH + 'page%s/' % (page_next)	
	Log(path); Log(pagenr); Log(gall_cnt); Log(pagemax)
	page = HTML.ElementFromURL(path)
	list = page.xpath("//*[@class='gallery-hunk clearfix']")  # oder <div class="gallery-case gallery-case-user">
	if len(list) > 0:
		oc.add(DirectoryObject(key=Callback(Galleries_all, pagenr=int(pagenr)+1), 
			title=name, summary='Mehr (+ 1)', tagline='', thumb=R(ICON_MEHR_1)))
		if (int(pagenr)+10) < pagemax:
			oc.add(DirectoryObject(key=Callback(Galleries_all, pagenr=int(pagenr)+10), 
				title=name, summary='Mehr (+ 10)', tagline='', thumb=R(ICON_MEHR_10)))  
		if (int(pagenr)+100) < pagemax:
			oc.add(DirectoryObject(key=Callback(Galleries_all, pagenr=int(pagenr)+100), 
				title=name, summary='Mehr (+ 100)', tagline='', thumb=R(ICON_MEHR_100))) 
	# weniger
	if  int(pagenr) > 1:
		oc.add(DirectoryObject(key=Callback(Galleries_all, pagenr=int(pagenr)-1), 
			title=name, summary='Weniger (- 1)', tagline='', thumb=R(ICON_WENIGER_1)))  
		if int(pagenr) > 10:
			oc.add(DirectoryObject(key=Callback(Galleries_all, pagenr=int(pagenr)-10), 
				title=name, summary='Weniger (- 10)', tagline='', thumb=R(ICON_WENIGER_10)))  
		if int(pagenr) > 100:
			oc.add(DirectoryObject(key=Callback(Galleries_all, pagenr=int(pagenr)-100), 		
				title=name, summary='Weniger (- 100)', tagline='', thumb=R(ICON_WENIGER_100)))  	
	return oc
      
#-------------
# Die Thumbnails von Flickr werden nicht gebraucht - erzeugt Plex selbst aus den Originalen
# max. Anzahl Fotos in Galerie: 50 (https://www.flickr.com/help/forum/en-us/72157646468539299/)
#	z.Z. keine Steuerung mehr / weniger nötig
@route(PREFIX + '/Gallery_single')
def Gallery_single(path, title):		
	Log('Gallery_single: ' + path)
	oc = ObjectContainer(view_group="InfoList", title1=title, title2=title, art = ObjectContainer.art)
	client = Client.Platform
	if client == None:
		client = ''
	if client.find ('Plex Home Theater'): 
		oc = home(cont=oc)							# Home-Button macht bei PHT das PhotoObject unbrauchbar
	Log('Client: ' + client) 
	
	page = HTML.ElementFromURL(path)
	Log(page); 
	
	# list = page.xpath("//*[@class='photo_container pc_s']")		# Thumbnails
	list = page.xpath("//*[@class='photo_container pc_z']")			# Org.-Größe
	Log(page); Log(list)
	
	image = 1
	for element in list:	
		s = HTML.StringFromElement(element)
		phid =  stringextract('data-photo-id=\"', '\">', s)				 # ID z.Z. nicht benötigt			 
		flickr_gallary__href = BASE + stringextract('href=\"', '\"', s)   # -> Web-Galerie auf Flickr
		title =  stringextract('title=\"', '\"', s)
		
		# Thumbnails unnötig - von Plex je nach Player selbst erzeugt. Besser vom Original herunter skaliert
		#	als vom ev zu kleinen Thumb hoch skaliert und verzerrt
		# img_prev_src = stringextract('img src=\"', '\"', s)  
		img_src = stringextract('src=\"', '\"', s)
		width = stringextract('width=\"', '\"', s)
		height = stringextract('height=\"', '\"', s)
		# summ = 'Größe: ' + width + 'x' + height
		summ = 'Bildgröße (Breite x Höhe):  %s x %s' % (width, height)
		title = title.decode(encoding="utf-8", errors="ignore")
		summ = summ .decode(encoding="utf-8", errors="ignore")
		Log(title);Log(img_src);Log(summ); 	

		oc.add(PhotoObject(	
			key=img_src,		# bei Verwendung von url: No service found for URL..
			rating_key='%s.%s' % (Plugin.Identifier, 'Bild ' + str(image)),	# rating_key = eindeutige ID
			summary=summ,
			title=title,
			thumb =	img_src,
			))
		image += 1
	
	return oc
		
####################################################################################################
# API-Format (unsigniert):	https://api.flickr.com/services/rest/?method=flickr.photos.search&api_key=
#	24df437b03dd7bf070ba220aa717027e&text=eltville&page=3&format=rest
#	Rückgabeformat XML
@route(PREFIX + '/Search')	
def Search(query=None, title=L('Search'), s_type='video', pagenr=1, **kwargs):
	Log('Search: ' + query); 
	ObjectContainer = Search_Work(query=query, pagenr=pagenr)	# wir springen direkt - Search_Work prozessiert vor + zurück 
	return	ObjectContainer
	
# --------------------------	
@route(PREFIX + '/Search_Work')	
def Search_Work(query, pagenr):
	Log('Search_Work: ' + query); 
	if pagenr < 1:
		pagenr = 1
	# api_key zu Testzwecken aus https://github.com/ideatosrl/FlickrApi/blob/master/Test/CurlMock.php entnommen
	# Verwendet wird die freie Textsuche (s. API): Treffer möglich in Titel, Beschreibung + Tags
	# Mehrere Suchbegriffe, getrennt durch Blanks, bewirken UND-Verknüpfung
	# URL's: viele Foto-Sets enthalten unterschiedliche Größen - erster Ansatz, Anforderung mit b=groß, schlug häufig fehl.
	#	Daher Anforderung mit einer Suffix-Liste (extras) - s. https://www.flickr.com/services/api/misc.urls.html -
	#	und Entnahme der "größten" URL.  
	
	query_flickr = query.replace(' ', '%20')		# Leerz. -> url-konform 
	SEARCHPATH = "https://api.flickr.com/services/rest/?method=flickr.photos.search&api_key=a6d472134d5877b51a38070c7c631956"
	extras = "url_o,url_k,url_h,url_l,url_c,url_z"	# URL-Anforderung, sortiert von groß nach klein - Default
	# Breiten: o = Original, k=2048, h=1600, l=1024, c=800, z=640
	pref_max_width = Prefs['pref_max_width']
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
	extras_list = extras.split(",")						# Verarbeitung s.u.
	
	path =  SEARCHPATH + "&text=%s&page=%s&extras=%s&format=rest" % (query_flickr, pagenr, extras)
	Log(path) 
	page = HTML.ElementFromURL(path)
	s = XML.StringFromElement(page)
	pagemax = stringextract('pages=\"', '\"', s)
	photototal =  stringextract('total=\"', '\"', s)

	name = 'Suche: %s, Seite %s von %s (Fotos: %s)' % (query, pagenr, pagemax, photototal)
	name = name.decode(encoding="utf-8", errors="ignore")
	oc = ObjectContainer(view_group="InfoList", title1=NAME, title2=name, art = ObjectContainer.art)
	if  s.find('<photo id=') < 0:			
		msg_notfound = 'Leider kein Treffer.'
		title = msg_notfound.decode(encoding="utf-8", errors="ignore")
		summary = 'zurück zu ' + NAME.decode(encoding="utf-8", errors="ignore")		
		oc.add(DirectoryObject(key=Callback(Main), title=title, 
			summary=summary, tagline='TV', thumb=R('home.png')))
		return oc
	
	client = Client.Platform
	if client == None:
		client = ''
	if client.find ('Plex Home Theater'): 
		oc = home(cont=oc)							# Home-Button macht bei PHT das PhotoObject unbrauchbar
	Log('Client: ' + client) 
			
	list = page.xpath("//photo")
	Log(extras_list);   # Log(list)		# bei Bedarf
	image = 1
	for element in list:					# Voreinstellung 100 pro Seite
		s = XML.StringFromElement(element)
		pid =  stringextract('id=\"', '\"', s) 
		owner =  stringextract('owner=\"', '\"', s) 	
		secret =  stringextract('secret=\"', '\"', s) 
		serverid =  stringextract('server=\"', '\"', s) 
		farmid =  stringextract('farm=\"', '\"', s) 		
		title =  stringextract('title=\"', '\"', s)			
				 
		thumb_src = 'https://farm%s.staticflickr.com/%s/%s_%s_m.jpg' % (farmid, serverid, pid, secret) 
		# img_src = PHOTO_PATH + '%s/%s' % (owner, pid)		# funktioniert nicht - Service-API verwenden:
		# img_src = 'https://farm%s.staticflickr.com/%s/%s_%s_b.jpg' % (farmid, serverid, pid, secret)  # _{secret}_[mstzb].jpg

		# Foto-Auswahl - jeweils das größte, je nach Voreinstellung (falls verfügbar):
		for i in range (len(extras_list)):			
			url_extra = extras_list[i]
			img_src = stringextract('%s=\"' % (url_extra), '\"', s) 
			suffix = url_extra[-2:] 		# z.B. _o von url_o, zusätzlich height + width ermitteln
			width = stringextract('width%s=\"' % (suffix), '\"', s)	  	# z.B. width_o
			height = stringextract('height%s=\"' % (suffix), '\"', s)  	# z.B. height_o
			# Log(url_extra); Log(img_src);Log(suffix);Log(width);Log(height);	# bei Bedarf
			if len(img_src) > 0:		# falls Format nicht vorhanden, weiter mit den kleineren Formaten
				break
		
		# summ = 'Bild %s von %s' % (str(image), photototal)	macht PhotoObject selbst
		summ = 'Bildgröße (Breite x Höhe):  %s x %s' % (width, height)
		title = unescape(title)
		title = title.decode(encoding="utf-8", errors="ignore")
		summ = summ.decode(encoding="utf-8", errors="ignore")
		Log(img_src);Log(title); # Log(pid);Log(owner);	# bei Bedarf
		if img_src == '':	# Sicherung (PhotoObject braucht URL)
			continue
		
		oc.add(PhotoObject(
			key=img_src,
			rating_key='%s.%s' % (Plugin.Identifier, 'Bild ' + str(image)),	# rating_key = eindeutige ID
			summary=summ,
			title=title,
			thumb = thumb_src
			))
		image += 1
	
	# auf mehr prüfen:
	Log(pagenr); Log(pagemax); Log(photototal);
	page_next = int(pagenr) + 1
	if (int(pagenr)+1) <= int(pagemax):
		Log(int(pagenr) +1)
		oc.add(DirectoryObject(key=Callback(Search_Work, query=query, pagenr=int(pagenr) +1), 
			title=name, summary='Mehr (+ 1)', tagline='', thumb=R(ICON_MEHR_1)))
	if (int(pagenr)+10) < int(pagemax):
		oc.add(DirectoryObject(key=Callback(Search_Work, query=query, pagenr=int(pagenr) +10), 
			title=name, summary='Mehr (+ 10)', tagline='', thumb=R(ICON_MEHR_10)))  
	if (int(pagenr)+100) < int(pagemax):
		oc.add(DirectoryObject(key=Callback(Search_Work, query=query, pagenr=int(pagenr) +100), 
			title=name, summary='Mehr (+ 100)', tagline='', thumb=R(ICON_MEHR_100))) 
	# weniger
	if  int(pagenr) > 1:
		oc.add(DirectoryObject(key=Callback(Search_Work, query=query, pagenr=int(pagenr)-1), 
			title=name, summary='Weniger (- 1)', tagline='', thumb=R(ICON_WENIGER_1)))  
	if int(pagenr) > 10:
		oc.add(DirectoryObject(key=Callback(Search_Work, query=query, pagenr=int(pagenr)-10), 
			title=name, summary='Weniger (- 10)', tagline='', thumb=R(ICON_WENIGER_10)))  
	if int(pagenr) > 100:
		oc.add(DirectoryObject(key=Callback(Search_Work, query=query, pagenr=int(pagenr)-100), 		
			title=name, summary='Weniger (- 100)', tagline='', thumb=R(ICON_WENIGER_100)))  	
	return oc
      

####################################################################################################
#	Hilfsfunktonen
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
#	line_ret = (line.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
#		.replace("&#39;", "'").replace("&#039;", "'").replace("&quot;", '"').replace("&nbsp;", " "))
	line_ret = line.replace('&auml;',"ä") 
	line_ret = line.replace('&ouml;',"ö") 
	line_ret = line.replace('&uuml;',"ü") 
	line_ret = line.replace('&szlig;',"ß")
	line_ret = line.replace('&Auml;',"Ä")  
	line_ret = line.replace('&Ouml;',"Ö")  
	line_ret = line.replace('&Uuml;',"Ü")  
	line_ret = line.replace('&#034;','"') 	#
	line_ret = line.replace('&quot;','"')  	# Entity Name zu &#034;
	line_ret = line.replace('\u00E9','é')
	line_ret = line.replace('&#039;',"'")  	# Bsp. ARD statt &#39; 
	line_ret = line.replace('&#39;',"'")  	#
	line_ret = line.replace('&#038;','&') 	#
	line_ret = line.replace('&amp;','&') 	# Entity Name zu &#038;
	line_ret = line.replace('&nbsp;',' ')
	line_ret = line.replace('&gt;','>')
	line_ret = line.replace('&lt;','<')	

	Log(line_ret)		# bei Bedarf
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

