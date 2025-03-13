from classes.RommAPIHelper import RommAPIHelper
from classes.DeckRommSyncDatabase import DeckRommSyncDatabase
import json
import logging

class BackgroundWorker:
    def __init__(self, dbName, logger):
        self.background_logger = logger
        self.dbName = dbName
        db = DeckRommSyncDatabase(dbName)
        configObj = db.select_as_dict("config")        
        for config in configObj:            
            if config['config_key'] == 'romm_api_base_url':
                self.romMAPIBaseUrl = config['config_value']
            elif config['config_key'] == 'romm_username':
                self.romMUsername = config['config_value']
            elif config['config_key'] == 'romm_password':
                self.romMPassword = config['config_value']           

    def sync_rommCollections(self):
        # Write Log
        self.background_logger.info("Syncing RomM Collections - Starting")
        romm = RommAPIHelper(self.romMAPIBaseUrl)
        romm.login(self.romMUsername, self.romMPassword)
        db = DeckRommSyncDatabase(self.dbName)

        # Read Platforms from RomM
        platform_result = romm.getPlatforms()
        for platform in platform_result:
            # Insert Platforms
            db.insert("platforms_matching", ["romm_platform_id", "romm_platform_name"], (platform['id'], platform['name']))

        # Read Collections from RomM
        collection_result = romm.getCollections()

        # Go Through Collections and Insert them into the Database
        for collection in collection_result:          
            db.insert("collections", ["collections_id", "name", "rom_count", "cover", "collection_sync"], 
                    (collection['id'],
                    collection['name'],
                    collection['rom_count'],
                    collection['path_cover_l'],
                    0))
            
            # Read ROMs from Collection
            roms = collection['roms']
            for rom in roms:
                romObj = romm.getRomByID(rom)
                # Insert ROM
                db.insert("roms", ["roms_id", "collections_id", "name", "url_cover", "filename", "platform_fs_slug", "platform_id"],
                        (romObj['id'],
                        collection['id'],
                        romObj['name'],
                        romObj['url_cover'],
                        romObj['file_name_no_ext'],
                        romObj['platform_fs_slug'],
                        romObj['platform_id']))
        # Write Log
        self.background_logger.info("Syncing RomM Collections - Finished")


    def sync_copyRoms(self):
        # Write Log
        self.background_logger.info("Syncing ROMS - Starting")
        db = DeckRommSyncDatabase(self.dbName)

        # Get Collections to sync
        collections = db.select_as_dict("collections", ['*'], 'collection_sync = ?', (1,))
        
        # Get Steamdeck Path
        steamdeck_path = db.select_as_dict("config", ['config_value'], 'config_key = ?', ('steamdeck_retrodeck_path',))
        steamdeck_path = steamdeck_path[0].get("config_value")
        
        # DEBUG: Set Steamdeck Path manually
        # steamdeck_path = "./output/"

        for collection in collections:

            self.background_logger.info(f"Check Collection: {collection.get('name')}")

            # Create RomM API Helper
            romm = RommAPIHelper(self.romMAPIBaseUrl)
            romm.login(self.romMUsername, self.romMPassword)
            
            # Get Roms from Collection
            roms = db.select_as_dict("roms", ['*'], 'collections_id = ? and sync_status = ?', (collection.get("collections_id"), 0))
            for rom in roms:
                roms_id = rom.get("roms_id")
                filename = rom.get("filename")
                platform_id = rom.get("platform_id")
                
                # Get Rom-Matching
                platform_matching = db.select_as_dict("platforms_matching", ['*'], 'romm_platform_id = ?', (platform_id,))                
                steamdeck_platform_path = platform_matching[0].get("steamdeck_platform_name")
                
                # Debug Print
                # print(f"ROMS-ID: {roms_id}")
                # print(f"Filename: {filename}")
                # print(f"Platform-ID: {platform_id}")
                # print(f"Copy {filename} to {steamdeck_path}{steamdeck_platform_path}/{filename}")
                # print("--------------------")

                self.background_logger.info(f"ROMS-ID: {roms_id} | Copy {filename} to {steamdeck_path}{steamdeck_platform_path}/{filename}")

                # Download Rom
                romm.downloadRom(roms_id, filename, steamdeck_path + steamdeck_platform_path + "/")

                self.background_logger.info(f"ROM-ID: {roms_id} | Copy Finished")

                # Update Sync Status
                db.update("roms", {"sync_status": "1"}, "roms_id = ?", (roms_id,))
        # Write Log      
        self.background_logger.info("Syncing ROMS - Finished") 