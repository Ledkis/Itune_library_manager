# -*- coding: utf-8 -*-
"""
Created on Sat Jul 19 18:52:24 2014

@author: Utilisateur
"""

import os
import plistlib
import pickle
              
class Itune_library_manager:
    def __init__(self, itune_library_path = "iTunes Music Library"):
        self.itune_library_path = itune_library_path
        
        self.init_itune_library(itune_library_path)
        self.init_track_list()
        self.init_playlist_list()
        
        self.init_all_tracks_attr()
        self.init_library_attr()
        
        self.init_all_playlist_attr()
        
    def save_library_in_binary_format(self):
        
        file_name , fileExtension = os.path.splitext(self.itune_library_path)
        file = open(file_name + ".plk" , 'wb')
        pickle.dump(self.itune_library, file)
        file.close()
        
        print("Library saved : %s"%file_name+ ".plk")
        
    ###########################################################################
    #                        ## Initialisation ##                             #
    ###########################################################################
        
    def init_itune_library(self, itune_library_path):
        fileName, fileExtension = os.path.splitext(itune_library_path)
        
        try:
            if fileExtension in ['.plk', '']:
                try:
                    self.init_itune_library_from_binary(fileName+'.plk')
                except:
                    self.init_itune_library_from_xml(fileName+'.xml')
            else:
                self.init_itune_library_from_xml(itune_library_path)
                
        except:
            self.itune_library = {}
            print("The itune music library hasn't been initialized")
                
            
    def init_itune_library_from_binary(self, itune_library_path):
        """Time initialiation time is way faster from a binary format.
        """
        file = open(itune_library_path, 'rb')
        self.itune_library = pickle.load(file)
        file.close()
        print("Initialized from binary")
        
    def init_itune_library_from_xml(self, itune_library_path):
        self.itune_library = plistlib.readPlist(itune_library_path)
        print("Initialized from xml")


    def init_track_list(self):
        if self.itune_library != {}:
            self.track_list = list(self.itune_library['Tracks'].values()) 
        else:
            self.track_list = {}
            
    def init_playlist_list(self):
        if self.itune_library != {} :
            self.playlist_list = list(self.itune_library['Playlists']) 
        else:
            self.playlist_list = {}
            
        
            
    
        
    def init_all_tracks_attr(self):
        track_attr_list = set()        
        for track in self.track_list:
            for attr in track.keys():
                track_attr_list.add(attr)
        
        self.track_attr_list = list(sorted(track_attr_list))
    
    def init_library_attr(self):
        self.library_keys = list(sorted(self.itune_library.keys()))
        
    
    def init_all_playlist_attr(self):
        playlist_attr_list = set()        
        for playlist in self.playlist_list:
            for attr in playlist.keys():
                playlist_attr_list.add(attr)
        
        self.playlist_attr_list = list(sorted(playlist_attr_list))              
                  
    ###########################################################################
    #                       ## Playlist Managment ##                          #
    ###########################################################################              
                  
                  
    def get_all_playlist_name(self):
        return [playlist['Name'] for playlist in self.playlist_list]
        
    
    def get_playlist(self, playlist_name):
        for playlist in self.playlist_list:
            if playlist_name == playlist['Name']:
                return playlist
        print("The playlist %s does not exist"%playlist_name)
        return None
        
        
    def get_playlist_track_list(self, playlist = None, playlist_name = None):
        if playlist is None:
            if playlist_name is not None:
                playlist = self.get_playlist(playlist_name)
            else:
                print("No playlist or playlist name given")
                return

        if playlist is None:
            return
        track_id_list = [el['Track ID'] for el in playlist['Playlist Items']]
        
        track_list = self.get_song_list_from_track_id_list(track_id_list)
        
        
        
        return track_list
                  
    ###########################################################################
    #                       ## Track Managment ##                             #
    ###########################################################################            
                  
                  
    def filter_track_list(self, attr, value, track_list = None):
        if track_list is None:
            track_list = self.track_list
        song_list = []
        for track in track_list:
            try:
                if track[attr] == value:
                    song_list.append(track)
            except KeyError:
                pass
        return song_list
        
    def get_all_attr(self, attr, track_list = None, sort = True):
        if track_list is None:
            track_list = self.track_list
        attr_val_list = set()
        for track in track_list:
            try:
                value = track[attr]
                attr_val_list.add(value)
            except KeyError:
                pass
        if sort:
            attr_val_list = sorted(attr_val_list)
            
        return list(attr_val_list)
        
    def get_song_list_from_track_id_list(self,
                                         track_id_list,
                                         track_list = None):
        if track_list is None:
            track_list = self.track_list
            
        song_list = []
        for track in track_list:
            try:
                track_id = track['Track ID']
                if track_id in track_id_list:
                    track_pos = track_id_list.index(track_id)
                    track['pos'] = track_pos
                    song_list.append(track)
            except KeyError:
                pass
            
        song_list = sorted(song_list, key=lambda track : track['pos'])
        return song_list
    
    def sort_by_attr(self,
                     attr,
                     track_list = None,
                     min_value = None,
                     max_res = None,
                     reverse = False):
        
        if track_list is None:
            track_list = self.track_list
        song_list = []
        
        for track in track_list:
            try:
                value = track[attr]
                if min_value is not None:
                    if value >= min_value:
                        song_list.append(track)
                else:
                    song_list.append(track)
            except KeyError:
                pass
        
        song_list = list(sorted(song_list,
                                key=lambda song : song[attr], 
                                reverse = reverse))
        if max_res is not None:
            if reverse:
                song_list = song_list[:max_res]
            else:
                song_list = song_list[-max_res:]
            
        return song_list
    
    
    def diplay_track(self,
                     track,
                     attr_list= [ 
                                 'Artist', 
                                 'Name',
                                 'Album',
                                 'Play Count',
                                 #'Play Date UTC', 
                                 #'Skip Count',
                                 #'Skip Date',
                                 ],
                     condensed = True,
                     friendly = False,
                     l = 30):
        n = 20
        if not condensed : print("-"*n)
            
        s = ""
        if friendly:
            s = self.get_friendly_track_name(track)
        else:
            for attr in attr_list:
                try: 
                    r = attr
                    a_l = int(l/2)
                    if len(r) > a_l:
                        r = r[0:a_l-3]+ "..."
                    
                    attr_val = track[attr]
                    r += ": %s"%attr_val
                        
                    if len(r) > l:
                        r = r[0:l-3]+ "..."
                    r = r.ljust(l)
                    if condensed :
                        s += " | " + r
                    else : 
                        s+= "\n" + r
                except KeyError:
                    pass
        print(s)
        if not condensed : print("-"*n)
                
    def diplay_track_list(self,
                          track_list,
                          attr_list = None,
                          condensed=True,
                          friendly = False,
                          l=30):
        if track_list is None:
            print('Nothing to display')            
            return
        n = 30
        print("-"*n)
        for track in track_list:
            display_params = {"condensed":condensed,
                              "l":l,
                              "friendly":friendly}
            if attr_list is not None:
                display_params['attr_list'] = attr_list
            self.diplay_track(track, **display_params)
            
        print("-"*n)
            
            
    def get_friendly_track_name(self, track):
        
        name = artist = ""
        try:
            name = track['Name']
        except:
            pass
        try:
            artist = track['Artist']
        except:
            pass
        
        return "%s %s"%(artist, name)
        
        

    def youtube_search(self, track_list, search = True):
        
        try:
            import webbrowser
        except:
            print('You need the webbrowser for that')
            return
        
        track_list_name = [self.get_friendly_track_name(track) 
                                    for track in track_list]
        
        base_url = "http://www.youtube.com/results?search_query="
        
        search_query_list = ["+".join(track_name.split())
                        for track_name in track_list_name]
        
        url_list = [base_url+query for query in search_query_list]
        
        for url in url_list:
            if search:
                webbrowser.open(url)
                
        if not search:
            print('The search is on false mode')
            
        return url_list
         
         
lib = Itune_library_manager()
def exemple_of_uses():
    global lib
    
    
    l = 50

    print("#"*l)
    print("Exemple of use")
    print("#"*l)
    
    print("\n"+"_"*l+"\n")
    
    # Playlist    
    
    print("#"*l)
    print("Playlist Managment")
    print("#"*l)
    
    
    print("\n"+"_"*l+"\n")
    
    r = lib.get_all_playlist_name()
    print("All playlist names : ")
    print(" | ".join(r))
    # Usefull if we want don't know the playlist names
    

    print("\n"+"_"*l+"\n")

    p_name = '.. COOL'
    r = lib.get_playlist_track_list(playlist_name=p_name)
    print("Track list of playlist %s : "%p_name)
    lib.diplay_track_list(r)
    
    
    print("\n"+"_"*l+"\n")
    
    p_name = '.. COOL'
    r = lib.get_playlist_track_list(playlist_name=p_name)
    r = lib.sort_by_attr('Play Count', max_res = 3, track_list = r)
    print("The 3 most played song of the %s playlist : "%p_name)
    lib.diplay_track_list(r)
    
    
    print("\n"+"_"*l+"\n")
    

    # Songs
    
    print("#"*l)
    print("Song Managment")
    print("#"*l)
    
    print("\n"+"_"*l+"\n")
    
    print("All tracks attributs : ")
    r = print(" | ".join(lib.track_attr_list))
    # Usefull to know all the atribute we can use to filter the tracks
    
    
    print("\n"+"_"*l+"\n")
    
    print("The 5 most played song : ")
    r = lib.sort_by_attr('Play Count', max_res = 5)
    lib.diplay_track_list(r)
    
    
    print("\n"+"_"*l+"\n")
    
    print("The 5 most played funk song : ")
    r = lib.filter_track_list('Genre', 'Funk')
    r = lib.sort_by_attr('Play Count',  track_list = r, max_res = 5)
    lib.diplay_track_list(r)
    
    
    print("\n"+"_"*l+"\n")
    
    r = lib.get_all_attr('Genre')
    print("Number of different musical genre : %s"%len(r))
    
    
    print("\n"+"_"*l+"\n")
    
    r = lib.get_all_attr('Artist')
    print("Number of different Artist : %s"%len(r))
    
    
    print("\n"+"_"*l+"\n")
    
    r = lib.sort_by_attr('Play Date UTC', max_res = 5)
    attr_list= [ 
                 'Artist', 
                 'Name',
                 'Play Date UTC', 
                ]
    print("The 5 last played song : ")
    lib.diplay_track_list(r, attr_list=attr_list, l = 40)
    # l specifie the width of each rows of the displayed result
    # attr_list specifie the labels of each rows
    
    print("\n"+"_"*l+"\n")
    
    r = lib.filter_track_list('Artist', 'Gramatik')
    r = lib.sort_by_attr('Play Count', max_res = 5, track_list = r)
    print("The 5 most played Gramatik song : ")
    lib.diplay_track_list(r)
    
    
    print("\n"+"_"*l+"\n")
    
    r = lib.filter_track_list('Artist', 'Gramatik')
    r = lib.filter_track_list('Album', 'No Shortcuts', track_list = r)
    r = lib.sort_by_attr('Play Count', max_res = 5, track_list = r)
    print("The 5 most played Gramatik song of album No Shortcuts: ")
    lib.diplay_track_list(r ,friendly = True)
    # With friendly = True it is esaier to copy - past on youtube or somewhere
    # else
    
    
    # youtube search
    
    print("#"*l)
    print("Yooutube search")
    print("#"*l)
    
    p_name = '.. COOL'
    r = lib.get_playlist_track_list(playlist_name=p_name)
    r = lib.sort_by_attr('Play Count', max_res = 3, track_list = r)
    print("Youtube search of the 3 most played song of the %s playlist : "
                                                                    %p_name)
    urls = lib.youtube_search(r, search = True)
    print(" | ".join(urls))
        
    
    
            
if __name__ == "__main__":
    exemple_of_uses()
    
    
    