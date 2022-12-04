from .data import OoT_Data

ootData = OoT_Data()

ootEnumRoomShapeType = [
    # ("Custom", "Custom", "Custom"),
    ("ROOM_SHAPE_TYPE_NORMAL", "Normal", "Normal"),
    ("ROOM_SHAPE_TYPE_IMAGE", "Image", "Image"),
    ("ROOM_SHAPE_TYPE_CULLABLE", "Cullable", "Cullable"),
]

ootRoomShapeStructs = [
    "RoomShapeNormal",
    "RoomShapeImage",
    "RoomShapeCullable",
]

ootRoomShapeEntryStructs = [
    "RoomShapeDListsEntry",
    "RoomShapeDListsEntry",
    "RoomShapeCullableEntry",
]


ootEnumSceneMenu = [
    ("General", "General", "General"),
    ("Lighting", "Lighting", "Lighting"),
    ("Cutscene", "Cutscene", "Cutscene"),
    ("Exits", "Exits", "Exits"),
    ("Alternate", "Alternate", "Alternate"),
]

ootEnumRenderScene = [
    ("General", "General", "General"),
    ("Alternate", "Alternate", "Alternate"),
]

ootEnumSceneMenuAlternate = [
    ("General", "General", "General"),
    ("Lighting", "Lighting", "Lighting"),
    ("Cutscene", "Cutscene", "Cutscene"),
    ("Exits", "Exits", "Exits"),
]

ootEnumRoomMenu = [
    ("General", "General", "General"),
    ("Objects", "Objects", "Objects"),
    ("Alternate", "Alternate", "Alternate"),
]

ootEnumRoomMenuAlternate = [
    ("General", "General", "General"),
    ("Objects", "Objects", "Objects"),
]

ootEnumHeaderMenu = [
    ("Child Night", "Child Night", "Child Night"),
    ("Adult Day", "Adult Day", "Adult Day"),
    ("Adult Night", "Adult Night", "Adult Night"),
    ("Cutscene", "Cutscene", "Cutscene"),
]

ootEnumHeaderMenuComplete = [
    ("Child Day", "Child Day", "Child Day"),
    ("Child Night", "Child Night", "Child Night"),
    ("Adult Day", "Adult Day", "Adult Day"),
    ("Adult Night", "Adult Night", "Adult Night"),
    ("Cutscene", "Cutscene", "Cutscene"),
]

ootEnumLightGroupMenu = [
    ("Dawn", "Dawn", "Dawn"),
    ("Day", "Day", "Day"),
    ("Dusk", "Dusk", "Dusk"),
    ("Night", "Night", "Night"),
]

ootEnumLinkIdle = [
    ("Custom", "Custom", "Custom"),
    ("0x00", "Default", "Default"),
    ("0x01", "Sneezing", "Sneezing"),
    ("0x02", "Wiping Forehead", "Wiping Forehead"),
    ("0x04", "Yawning", "Yawning"),
    ("0x07", "Gasping For Breath", "Gasping For Breath"),
    ("0x09", "Brandish Sword", "Brandish Sword"),
    ("0x0A", "Adjust Tunic", "Adjust Tunic"),
    ("0xFF", "Hops On Epona", "Hops On Epona"),
]

# Make sure to add exceptions in utility.py - selectMeshChildrenOnly
ootEnumEmptyType = [
    ("None", "None", "None"),
    ("Scene", "Scene", "Scene"),
    ("Room", "Room", "Room"),
    ("Actor", "Actor", "Actor"),
    ("Transition Actor", "Transition Actor", "Transition Actor"),
    ("Entrance", "Entrance", "Entrance"),
    ("Water Box", "Water Box", "Water Box"),
    ("Cull Group", "Custom Cull Group", "Cull Group"),
    ("LOD", "LOD Group", "LOD Group"),
    ("Cutscene", "Cutscene", "Cutscene"),
    # ('Camera Volume', 'Camera Volume', 'Camera Volume'),
]

ootEnumCloudiness = [
    ("Custom", "Custom", "Custom"),
    ("0x00", "Sunny", "Sunny"),
    ("0x01", "Cloudy", "Cloudy"),
]

ootEnumCameraMode = [
    ("Custom", "Custom", "Custom"),
    ("0x00", "Default", "Default"),
    ("0x10", "Two Views, No C-Up", "Two Views, No C-Up"),
    ("0x20", "Rotating Background, Bird's Eye C-Up", "Rotating Background, Bird's Eye C-Up"),
    ("0x30", "Fixed Background, No C-Up", "Fixed Background, No C-Up"),
    ("0x40", "Rotating Background, No C-Up", "Rotating Background, No C-Up"),
    ("0x50", "Shooting Gallery", "Shooting Gallery"),
]

ootEnumMapLocation = [
    ("Custom", "Custom", "Custom"),
    ("0x00", "Hyrule Field", "Hyrule Field"),
    ("0x01", "Kakariko Village", "Kakariko Village"),
    ("0x02", "Graveyard", "Graveyard"),
    ("0x03", "Zora's River", "Zora's River"),
    ("0x04", "Kokiri Forest", "Kokiri Forest"),
    ("0x05", "Sacred Forest Meadow", "Sacred Forest Meadow"),
    ("0x06", "Lake Hylia", "Lake Hylia"),
    ("0x07", "Zora's Domain", "Zora's Domain"),
    ("0x08", "Zora's Fountain", "Zora's Fountain"),
    ("0x09", "Gerudo Valley", "Gerudo Valley"),
    ("0x0A", "Lost Woods", "Lost Woods"),
    ("0x0B", "Desert Colossus", "Desert Colossus"),
    ("0x0C", "Gerudo's Fortress", "Gerudo's Fortress"),
    ("0x0D", "Haunted Wasteland", "Haunted Wasteland"),
    ("0x0E", "Market", "Market"),
    ("0x0F", "Hyrule Castle", "Hyrule Castle"),
    ("0x10", "Death Mountain Trail", "Death Mountain Trail"),
    ("0x11", "Death Mountain Crater", "Death Mountain Crater"),
    ("0x12", "Goron City", "Goron City"),
    ("0x13", "Lon Lon Ranch", "Lon Lon Ranch"),
    ("0x14", "Dampe's Grave & Windmill", "Dampe's Grave & Windmill"),
    ("0x15", "Ganon's Castle", "Ganon's Castle"),
    ("0x16", "Grottos & Fairy Fountains", "Grottos & Fairy Fountains"),
]

ootEnumSkybox = [
    ("Custom", "Custom", "Custom"),
    ("0x00", "None", "None"),
    ("0x01", "Standard Sky", "Standard Sky"),
    ("0x02", "Hylian Bazaar", "Hylian Bazaar"),
    ("0x03", "Brown Cloudy Sky", "Brown Cloudy Sky"),
    ("0x04", "Market Ruins", "Market Ruins"),
    ("0x05", "Black Cloudy Night", "Black Cloudy Night"),
    ("0x07", "Link's House", "Link's House"),
    ("0x09", "Market (Main Square, Day)", "Market (Main Square, Day)"),
    ("0x0A", "Market (Main Square, Night)", "Market (Main Square, Night)"),
    ("0x0B", "Happy Mask Shop", "Happy Mask Shop"),
    ("0x0C", "Know-It-All Brothers' House", "Know-It-All Brothers' House"),
    ("0x0E", "Kokiri Twins' House", "Kokiri Twins' House"),
    ("0x0F", "Stable", "Stable"),
    ("0x10", "Stew Lady's House", "Stew Lady's House"),
    ("0x11", "Kokiri Shop", "Kokiri Shop"),
    ("0x13", "Goron Shop", "Goron Shop"),
    ("0x14", "Zora Shop", "Zora Shop"),
    ("0x16", "Kakariko Potions Shop", "Kakariko Potions Shop"),
    ("0x17", "Hylian Potions Shop", "Hylian Potions Shop"),
    ("0x18", "Bomb Shop", "Bomb Shop"),
    ("0x1A", "Dog Lady's House", "Dog Lady's House"),
    ("0x1B", "Impa's House", "Impa's House"),
    ("0x1C", "Gerudo Tent", "Gerudo Tent"),
    ("0x1D", "Environment Color", "Environment Color"),
    ("0x20", "Mido's House", "Mido's House"),
    ("0x21", "Saria's House", "Saria's House"),
    ("0x22", "Dog Guy's House", "Dog Guy's House"),
]

ootEnumSkyboxLighting = [
    # see ``LightMode`` enum in ``z64environment.h``
    ("Custom", "Custom", "Custom"),
    ("LIGHT_MODE_TIME", "Time Of Day", "Time Of Day"),
    ("LIGHT_MODE_SETTINGS", "Indoor", "Indoor"),
]

ootEnumAudioSessionPreset = [
    ("Custom", "Custom", "Custom"),
    ("0x00", "0x00", "0x00"),
]

ootEnumMusicSeq = [
    ("Custom", "Custom", "Custom"),
    ("0x02", "Hyrule Field", "Hyrule Field"),
    ("0x03", "Hyrule Field (Initial Segment From Loading Area)", "Hyrule Field (Initial Segment From Loading Area)"),
    ("0x04", "Hyrule Field (Moving Segment 1)", "Hyrule Field (Moving Segment 1)"),
    ("0x05", "Hyrule Field (Moving Segment 2)", "Hyrule Field (Moving Segment 2)"),
    ("0x06", "Hyrule Field (Moving Segment 3)", "Hyrule Field (Moving Segment 3)"),
    ("0x07", "Hyrule Field (Moving Segment 4)", "Hyrule Field (Moving Segment 4)"),
    ("0x08", "Hyrule Field (Moving Segment 5)", "Hyrule Field (Moving Segment 5)"),
    ("0x09", "Hyrule Field (Moving Segment 6)", "Hyrule Field (Moving Segment 6)"),
    ("0x0A", "Hyrule Field (Moving Segment 7)", "Hyrule Field (Moving Segment 7)"),
    ("0x0B", "Hyrule Field (Moving Segment 8)", "Hyrule Field (Moving Segment 8)"),
    ("0x0C", "Hyrule Field (Moving Segment 9)", "Hyrule Field (Moving Segment 9)"),
    ("0x0D", "Hyrule Field (Moving Segment 10)", "Hyrule Field (Moving Segment 10)"),
    ("0x0E", "Hyrule Field (Moving Segment 11)", "Hyrule Field (Moving Segment 11)"),
    ("0x0F", "Hyrule Field (Enemy Approaches)", "Hyrule Field (Enemy Approaches)"),
    ("0x10", "Hyrule Field (Enemy Near Segment 1)", "Hyrule Field (Enemy Near Segment 1)"),
    ("0x11", "Hyrule Field (Enemy Near Segment 2)", "Hyrule Field (Enemy Near Segment 2)"),
    ("0x12", "Hyrule Field (Enemy Near Segment 3)", "Hyrule Field (Enemy Near Segment 3)"),
    ("0x13", "Hyrule Field (Enemy Near Segment 4)", "Hyrule Field (Enemy Near Segment 4)"),
    ("0x14", "Hyrule Field (Standing Still Segment 1)", "Hyrule Field (Standing Still Segment 1)"),
    ("0x15", "Hyrule Field (Standing Still Segment 2)", "Hyrule Field (Standing Still Segment 2)"),
    ("0x16", "Hyrule Field (Standing Still Segment 3)", "Hyrule Field (Standing Still Segment 3)"),
    ("0x17", "Hyrule Field (Standing Still Segment 4)", "Hyrule Field (Standing Still Segment 4)"),
    ("0x18", "Dodongo's Cavern", "Dodongo's Cavern"),
    ("0x19", "Kakariko Village (Adult)", "Kakariko Village (Adult)"),
    ("0x1A", "Enemy Battle", "Enemy Battle"),
    ("0x1B", "Boss Battle 00", "Boss Battle 00"),
    ("0x1C", "Inside the Deku Tree", "Inside the Deku Tree"),
    ("0x1D", "Market", "Market"),
    ("0x1E", "Title Theme", "Title Theme"),
    ("0x1F", "Link's House", "Link's House"),
    ("0x20", "Game Over", "Game Over"),
    ("0x21", "Boss Clear", "Boss Clear"),
    ("0x22", "Item Get", "Item Get"),
    ("0x23", "Opening Ganon", "Opening Ganon"),
    ("0x24", "Heart Get", "Heart Get"),
    ("0x25", "Prelude Of Light", "Prelude Of Light"),
    ("0x26", "Inside Jabu-Jabu's Belly", "Inside Jabu-Jabu's Belly"),
    ("0x27", "Kakariko Village (Child)", "Kakariko Village (Child)"),
    ("0x28", "Great Fairy's Fountain", "Great Fairy's Fountain"),
    ("0x29", "Zelda's Theme", "Zelda's Theme"),
    ("0x2A", "Fire Temple", "Fire Temple"),
    ("0x2B", "Open Treasure Chest", "Open Treasure Chest"),
    ("0x2C", "Forest Temple", "Forest Temple"),
    ("0x2D", "Hyrule Castle Courtyard", "Hyrule Castle Courtyard"),
    ("0x2E", "Ganondorf's Theme", "Ganondorf's Theme"),
    ("0x2F", "Lon Lon Ranch", "Lon Lon Ranch"),
    ("0x30", "Goron City", "Goron City "),
    ("0x31", "Hyrule Field Morning Theme", "Hyrule Field Morning Theme"),
    ("0x32", "Spiritual Stone Get", "Spiritual Stone Get"),
    ("0x33", "Bolero of Fire", "Bolero of Fire"),
    ("0x34", "Minuet of Woods", "Minuet of Woods"),
    ("0x35", "Serenade of Water", "Serenade of Water"),
    ("0x36", "Requiem of Spirit", "Requiem of Spirit"),
    ("0x37", "Nocturne of Shadow", "Nocturne of Shadow"),
    ("0x38", "Mini-Boss Battle", "Mini-Boss Battle"),
    ("0x39", "Obtain Small Item", "Obtain Small Item"),
    ("0x3A", "Temple of Time", "Temple of Time"),
    ("0x3B", "Escape from Lon Lon Ranch", "Escape from Lon Lon Ranch"),
    ("0x3C", "Kokiri Forest", "Kokiri Forest"),
    ("0x3D", "Obtain Fairy Ocarina", "Obtain Fairy Ocarina"),
    ("0x3E", "Lost Woods", "Lost Woods"),
    ("0x3F", "Spirit Temple", "Spirit Temple"),
    ("0x40", "Horse Race", "Horse Race"),
    ("0x41", "Horse Race Goal", "Horse Race Goal"),
    ("0x42", "Ingo's Theme", "Ingo's Theme"),
    ("0x43", "Obtain Medallion", "Obtain Medallion"),
    ("0x44", "Ocarina Saria's Song", "Ocarina Saria's Song"),
    ("0x45", "Ocarina Epona's Song", "Ocarina Epona's Song"),
    ("0x46", "Ocarina Zelda's Lullaby", "Ocarina Zelda's Lullaby"),
    ("0x47", "Sun's Song", "Sun's Song"),
    ("0x48", "Song of Time", "Song of Time"),
    ("0x49", "Song of Storms", "Song of Storms"),
    ("0x4A", "Fairy Flying", "Fairy Flying"),
    ("0x4B", "Deku Tree", "Deku Tree"),
    ("0x4C", "Windmill Hut", "Windmill Hut"),
    ("0x4D", "Legend of Hyrule", "Legend of Hyrule"),
    ("0x4E", "Shooting Gallery", "Shooting Gallery"),
    ("0x4F", "Sheik's Theme", "Sheik's Theme"),
    ("0x50", "Zora's Domain", "Zora's Domain"),
    ("0x51", "Enter Zelda", "Enter Zelda"),
    ("0x52", "Goodbye to Zelda", "Goodbye to Zelda"),
    ("0x53", "Master Sword", "Master Sword"),
    ("0x54", "Ganon Intro", "Ganon Intro"),
    ("0x55", "Shop", "Shop"),
    ("0x56", "Chamber of the Sages", "Chamber of the Sages"),
    ("0x57", "File Select", "File Select"),
    ("0x58", "Ice Cavern", "Ice Cavern"),
    ("0x59", "Open Door of Temple of Time", "Open Door of Temple of Time"),
    ("0x5A", "Kaepora Gaebora's Theme", "Kaepora Gaebora's Theme"),
    ("0x5B", "Shadow Temple", "Shadow Temple"),
    ("0x5C", "Water Temple", "Water Temple"),
    ("0x5D", "Ganon's Castle Bridge", "Ganon's Castle Bridge"),
    ("0x5E", "Ocarina of Time", "Ocarina of Time"),
    ("0x5F", "Gerudo Valley", "Gerudo Valley"),
    ("0x60", "Potion Shop", "Potion Shop"),
    ("0x61", "Kotake & Koume's Theme", "Kotake & Koume's Theme"),
    ("0x62", "Escape from Ganon's Castle", "Escape from Ganon's Castle"),
    ("0x63", "Ganon's Castle Under Ground", "Ganon's Castle Under Ground"),
    ("0x64", "Ganondorf Battle", "Ganondorf Battle"),
    ("0x65", "Ganon Battle", "Ganon Battle"),
    ("0x66", "Seal of Six Sages", "Seal of Six Sages"),
    ("0x67", "End Credits I", "End Credits I"),
    ("0x68", "End Credits II", "End Credits II"),
    ("0x69", "End Credits III", "End Credits III"),
    ("0x6A", "End Credits IV", "End Credits IV"),
    ("0x6B", "King Dodongo & Volvagia Boss Battle", "King Dodongo & Volvagia Boss Battle"),
    ("0x6C", "Mini-Game", "Mini-Game"),
]

ootEnumNightSeq = [
    ("Custom", "Custom", "Custom"),
    ("0x00", "Standard night [day and night cycle]", "0x00"),
    ("0x01", "Standard night [Kakariko]", "0x01"),
    ("0x02", "Distant storm [Graveyard]", "0x02"),
    ("0x03", "Howling wind and cawing [Ganon's Castle]", "0x03"),
    ("0x04", "Wind + night birds [Kokiri]", "0x04"),
    ("0x05", "Wind + crickets", "0x05"),
    ("0x06", "Wind", "0x06"),
    ("0x07", "Howling wind", "0x07"),
    ("0x08", "Wind + crickets", "0x08"),
    ("0x09", "Wind + crickets", "0x09"),
    ("0x0A", "Tubed howling wind [Wasteland]", "0x0A"),
    ("0x0B", "Tubed howling wind [Colossus]", "0x0B"),
    ("0x0C", "Wind", "0x0C"),
    ("0x0D", "Wind + crickets", "0x0D"),
    ("0x0E", "Wind + crickets", "0x0E"),
    ("0x0F", "Wind + birds", "0x0F"),
    ("0x10", "Wind + crickets", "0x10"),
    ("0x11", "?", "0x11"),
    ("0x12", "Wind + crickets", "0x12"),
    ("0x13", "Day music always playing", "0x13"),
    ("0x14", "Silence", "0x14"),
    ("0x16", "Silence", "0x16"),
    ("0x17", "High tubed wind + rain", "0x17"),
    ("0x18", "Silence", "0x18"),
    ("0x19", "Silence", "0x19"),
    ("0x1A", "High tubed wind + rain", "0x1A"),
    ("0x1B", "Silence", "0x1B"),
    ("0x1C", "Rain", "0x1C"),
    ("0x1D", "High tubed wind + rain", "0x1D"),
    ("0x1E", "Silence", "0x1E"),
    ("0x1F", "High tubed wind + rain ", "0x1F"),
]

ootEnumGlobalObject = [
    ("Custom", "Custom", "Custom"),
    ("OBJECT_INVALID", "None", "None"),
    ("OBJECT_GAMEPLAY_FIELD_KEEP", "Overworld", "gameplay_field_keep"),
    ("OBJECT_GAMEPLAY_DANGEON_KEEP", "Dungeon", "gameplay_dangeon_keep"),
]

ootEnumNaviHints = [
    ("Custom", "Custom", "Custom"),
    ("0x00", "None", "None"),
    ("0x01", "Overworld", "elf_message_field"),
    ("0x02", "Dungeon", "elf_message_ydan"),
]

ootEnumTransitionAnims = [
    ("Custom", "Custom", "Custom"),
    ("0x00", "Spiky", "Spiky"),
    ("0x01", "Triforce", "Triforce"),
    ("0x02", "Slow Black Fade", "Slow Black Fade"),
    ("0x03", "Slow Day/White, Slow Night/Black Fade", "Slow Day/White, Slow Night/Black Fade"),
    ("0x04", "Fast Day/Black, Slow Night/Black Fade", "Fast Day/Black, Slow Night/Black Fade"),
    ("0x05", "Fast Day/White, Slow Night/Black Fade", "Fast Day/White, Slow Night/Black Fade"),
    ("0x06", "Very Slow Day/White, Slow Night/Black Fade", "Very Slow Day/White, Slow Night/Black Fade"),
    ("0x07", "Very Slow Day/White, Slow Night/Black Fade", "Very Slow Day/White, Slow Night/Black Fade"),
    ("0x0E", "Slow Sandstorm Fade", "Slow Sandstorm Fade"),
    ("0x0F", "Fast Sandstorm Fade", "Fast Sandstorm Fade"),
    ("0x20", "Iris Fade", "Iris Fade"),
    ("0x2C", "Shortcut Transition", "Shortcut Transition"),
]

# The order of this list matters (normal OoT scene order as defined by ``scene_table.h``)
ootEnumSceneID = [
    ("Custom", "Custom", "Custom"),
    ("SCENE_YDAN", "Inside the Deku Tree (Ydan)", "Ydan"),
    ("SCENE_DDAN", "Dodongo's Cavern (Ddan)", "Ddan"),
    ("SCENE_BDAN", "Inside Jabu Jabu's Belly (Bdan)", "Bdan"),
    ("SCENE_BMORI1", "Forest Temple (Bmori1)", "Bmori1"),
    ("SCENE_HIDAN", "Fire Temple (Hidan)", "Hidan"),
    ("SCENE_MIZUSIN", "Water Temple (Mizusin)", "Mizusin"),
    ("SCENE_JYASINZOU", "Spirit Temple (Jyasinzou)", "Jyasinzou"),
    ("SCENE_HAKADAN", "Shadow Temple (Hakadan)", "Hakadan"),
    ("SCENE_HAKADANCH", "Bottom of the Well (Hakadanch)", "Hakadanch"),
    ("SCENE_ICE_DOUKUTO", "Ice Cavern (Ice Doukuto)", "Ice Doukuto"),
    ("SCENE_GANON", "Ganon's Tower (Ganon)", "Ganon"),
    ("SCENE_MEN", "Gerudo Training Ground (Men)", "Men"),
    ("SCENE_GERUDOWAY", "Thieves' Hideout (Gerudoway)", "Gerudoway"),
    ("SCENE_GANONTIKA", "Inside Ganon's Castle (Ganontika)", "Ganontika"),
    ("SCENE_GANON_SONOGO", "Ganon's Tower (Collapsing) (Ganon Sonogo)", "Ganon Sonogo"),
    ("SCENE_GANONTIKA_SONOGO", "Inside Ganon's Castle (Collapsing) (Ganontika Sonogo)", "Ganontika Sonogo"),
    ("SCENE_TAKARAYA", "Treasure Chest Shop (Takaraya)", "Takaraya"),
    ("SCENE_YDAN_BOSS", "Gohma's Lair (Ydan Boss)", "Ydan Boss"),
    ("SCENE_DDAN_BOSS", "King Dodongo's Lair (Ddan Boss)", "Ddan Boss"),
    ("SCENE_BDAN_BOSS", "Barinade's Lair (Bdan Boss)", "Bdan Boss"),
    ("SCENE_MORIBOSSROOM", "Phantom Ganon's Lair (Moribossroom)", "Moribossroom"),
    ("SCENE_FIRE_BS", "Volvagia's Lair (Fire Bs)", "Fire Bs"),
    ("SCENE_MIZUSIN_BS", "Morpha's Lair (Mizusin Bs)", "Mizusin Bs"),
    ("SCENE_JYASINBOSS", "Twinrova's Lair & Iron Knuckle Mini-Boss Room (Jyasinboss)", "Jyasinboss"),
    ("SCENE_HAKADAN_BS", "Bongo Bongo's Lair (Hakadan Bs)", "Hakadan Bs"),
    ("SCENE_GANON_BOSS", "Ganondorf's Lair (Ganon Boss)", "Ganon Boss"),
    ("SCENE_GANON_FINAL", "Ganondorf's Death Scene (Tower Escape Exterior) (Ganon Final)", "Ganon Final"),
    ("SCENE_ENTRA", "Market Entrance (Child - Day) (Entra)", "Entra"),
    ("SCENE_ENTRA_N", "Market Entrance (Child - Night) (Entra N)", "Entra N"),
    ("SCENE_ENRUI", "Market Entrance (Ruins) (Enrui)", "Enrui"),
    ("SCENE_MARKET_ALLEY", "Back Alley (Day) (Market Alley)", "Market Alley"),
    ("SCENE_MARKET_ALLEY_N", "Back Alley (Night) (Market Alley N)", "Market Alley N"),
    ("SCENE_MARKET_DAY", "Market (Child - Day) (Market Day)", "Market Day"),
    ("SCENE_MARKET_NIGHT", "Market (Child - Night) (Market Night)", "Market Night"),
    ("SCENE_MARKET_RUINS", "Market (Ruins) (Market Ruins)", "Market Ruins"),
    ("SCENE_SHRINE", "Temple of Time Exterior (Day) (Shrine)", "Shrine"),
    ("SCENE_SHRINE_N", "Temple of Time Exterior (Night) (Shrine N)", "Shrine N"),
    ("SCENE_SHRINE_R", "Temple of Time Exterior (Ruins) (Shrine R)", "Shrine R"),
    ("SCENE_KOKIRI_HOME", "Know-It-All Brothers' House (Kokiri Home)", "Kokiri Home"),
    ("SCENE_KOKIRI_HOME3", "Twins' House (Kokiri Home3)", "Kokiri Home3"),
    ("SCENE_KOKIRI_HOME4", "Mido's House (Kokiri Home4)", "Kokiri Home4"),
    ("SCENE_KOKIRI_HOME5", "Saria's House (Kokiri Home5)", "Kokiri Home5"),
    ("SCENE_KAKARIKO", "Carpenter Boss's House (Kakariko)", "Kakariko"),
    ("SCENE_KAKARIKO3", "Back Alley House (Man in Green) (Kakariko3)", "Kakariko3"),
    ("SCENE_SHOP1", "Bazaar (Shop1)", "Shop1"),
    ("SCENE_KOKIRI_SHOP", "Kokiri Shop (Kokiri Shop)", "Kokiri Shop"),
    ("SCENE_GOLON", "Goron Shop (Golon)", "Golon"),
    ("SCENE_ZOORA", "Zora Shop (Zoora)", "Zoora"),
    ("SCENE_DRAG", "Kakariko Potion Shop (Drag)", "Drag"),
    ("SCENE_ALLEY_SHOP", "Market Potion Shop (Alley Shop)", "Alley Shop"),
    ("SCENE_NIGHT_SHOP", "Bombchu Shop (Night Shop)", "Night Shop"),
    ("SCENE_FACE_SHOP", "Happy Mask Shop (Face Shop)", "Face Shop"),
    ("SCENE_LINK_HOME", "Link's House (Link Home)", "Link Home"),
    ("SCENE_IMPA", "Back Alley House (Dog Lady) (Impa)", "Impa"),
    ("SCENE_MALON_STABLE", "Stable (Malon Stable)", "Malon Stable"),
    ("SCENE_LABO", "Impa's House (Labo)", "Labo"),
    ("SCENE_HYLIA_LABO", "Lakeside Laboratory (Hylia Labo)", "Hylia Labo"),
    ("SCENE_TENT", "Carpenters' Tent (Tent)", "Tent"),
    ("SCENE_HUT", "Gravekeeper's Hut (Hut)", "Hut"),
    ("SCENE_DAIYOUSEI_IZUMI", "Great Fairy's Fountain (Upgrades) (Daiyousei Izumi)", "Daiyousei Izumi"),
    ("SCENE_YOUSEI_IZUMI_TATE", "Fairy's Fountain (Healing Fairies) (Yousei Izumi Tate)", "Yousei Izumi Tate"),
    ("SCENE_YOUSEI_IZUMI_YOKO", "Great Fairy's Fountain (Spells) (Yousei Izumi Yoko)", "Yousei Izumi Yoko"),
    ("SCENE_KAKUSIANA", "Grottos (Kakusiana)", "Kakusiana"),
    ("SCENE_HAKAANA", "Grave (Redead) (Hakaana)", "Hakaana"),
    ("SCENE_HAKAANA2", "Grave (Fairy's Fountain) (Hakaana2)", "Hakaana2"),
    ("SCENE_HAKAANA_OUKE", "Royal Family's Tomb (Hakaana Ouke)", "Hakaana Ouke"),
    ("SCENE_SYATEKIJYOU", "Shooting Gallery (Syatekijyou)", "Syatekijyou"),
    ("SCENE_TOKINOMA", "Temple of Time (Tokinoma)", "Tokinoma"),
    ("SCENE_KENJYANOMA", "Chamber of the Sages (Kenjyanoma)", "Kenjyanoma"),
    ("SCENE_HAIRAL_NIWA", "Castle Hedge Maze (Day) (Hairal Niwa)", "Hairal Niwa"),
    ("SCENE_HAIRAL_NIWA_N", "Castle Hedge Maze (Night) (Hairal Niwa N)", "Hairal Niwa N"),
    ("SCENE_HIRAL_DEMO", "Cutscene Map (Hiral Demo)", "Hiral Demo"),
    ("SCENE_HAKASITARELAY", "Dampé's Grave & Windmill (Hakasitarelay)", "Hakasitarelay"),
    ("SCENE_TURIBORI", "Fishing Pond (Turibori)", "Turibori"),
    ("SCENE_NAKANIWA", "Castle Courtyard (Nakaniwa)", "Nakaniwa"),
    ("SCENE_BOWLING", "Bombchu Bowling Alley (Bowling)", "Bowling"),
    ("SCENE_SOUKO", "Lon Lon Ranch House & Tower (Souko)", "Souko"),
    ("SCENE_MIHARIGOYA", "Guard House (Miharigoya)", "Miharigoya"),
    ("SCENE_MAHOUYA", "Granny's Potion Shop (Mahouya)", "Mahouya"),
    ("SCENE_GANON_DEMO", "Ganon's Tower Collapse & Battle Arena (Ganon Demo)", "Ganon Demo"),
    ("SCENE_KINSUTA", "House of Skulltula (Kinsuta)", "Kinsuta"),
    ("SCENE_SPOT00", "Hyrule Field (Spot00)", "Spot00"),
    ("SCENE_SPOT01", "Kakariko Village (Spot01)", "Spot01"),
    ("SCENE_SPOT02", "Graveyard (Spot02)", "Spot02"),
    ("SCENE_SPOT03", "Zora's River (Spot03)", "Spot03"),
    ("SCENE_SPOT04", "Kokiri Forest (Spot04)", "Spot04"),
    ("SCENE_SPOT05", "Sacred Forest Meadow (Spot05)", "Spot05"),
    ("SCENE_SPOT06", "Lake Hylia (Spot06)", "Spot06"),
    ("SCENE_SPOT07", "Zora's Domain (Spot07)", "Spot07"),
    ("SCENE_SPOT08", "Zora's Fountain (Spot08)", "Spot08"),
    ("SCENE_SPOT09", "Gerudo Valley (Spot09)", "Spot09"),
    ("SCENE_SPOT10", "Lost Woods (Spot10)", "Spot10"),
    ("SCENE_SPOT11", "Desert Colossus (Spot11)", "Spot11"),
    ("SCENE_SPOT12", "Gerudo's Fortress (Spot12)", "Spot12"),
    ("SCENE_SPOT13", "Haunted Wasteland (Spot13)", "Spot13"),
    ("SCENE_SPOT15", "Hyrule Castle (Spot15)", "Spot15"),
    ("SCENE_SPOT16", "Death Mountain Trail (Spot16)", "Spot16"),
    ("SCENE_SPOT17", "Death Mountain Crater (Spot17)", "Spot17"),
    ("SCENE_SPOT18", "Goron City (Spot18)", "Spot18"),
    ("SCENE_SPOT20", "Lon Lon Ranch (Spot20)", "Spot20"),
    ("SCENE_GANON_TOU", "Ganon's Castle Exterior (Ganon Tou)", "Ganon Tou"),
    ("SCENE_TEST01", "Jungle Gym (Test01)", "Test01"),
    ("SCENE_BESITU", "Ganondorf Test Room (Besitu)", "Besitu"),
    ("SCENE_DEPTH_TEST", "Depth Test (Depth Test)", "Depth Test"),
    ("SCENE_SYOTES", "Stalfos Mini-Boss Room (Syotes)", "Syotes"),
    ("SCENE_SYOTES2", "Stalfos Boss ROom (Syotes2)", "Syotes2"),
    ("SCENE_SUTARU", "Sutaru (Sutaru)", "Sutaru"),
    ("SCENE_HAIRAL_NIWA2", "Castle Hedge Maze (Early) (Hairal Niwa2)", "Hairal Niwa2"),
    ("SCENE_SASATEST", "Sasatest (Sasatest)", "Sasatest"),
    ("SCENE_TESTROOM", "Treasure Chest Room (Testroom)", "Testroom"),
]

ootSceneIDToName = {
    "SCENE_YDAN": "ydan",
    "SCENE_DDAN": "ddan",
    "SCENE_BDAN": "bdan",
    "SCENE_BMORI1": "Bmori1",
    "SCENE_HIDAN": "HIDAN",
    "SCENE_MIZUSIN": "MIZUsin",
    "SCENE_JYASINZOU": "jyasinzou",
    "SCENE_HAKADAN": "HAKAdan",
    "SCENE_HAKADANCH": "HAKAdanCH",
    "SCENE_ICE_DOUKUTO": "ice_doukutu",
    "SCENE_GANON": "ganon",
    "SCENE_MEN": "men",
    "SCENE_GERUDOWAY": "gerudoway",
    "SCENE_GANONTIKA": "ganontika",
    "SCENE_GANON_SONOGO": "ganon_sonogo",
    "SCENE_GANONTIKA_SONOGO": "ganontikasonogo",
    "SCENE_TAKARAYA": "takaraya",
    "SCENE_YDAN_BOSS": "ydan_boss",
    "SCENE_DDAN_BOSS": "ddan_boss",
    "SCENE_BDAN_BOSS": "bdan_boss",
    "SCENE_MORIBOSSROOM": "moribossroom",
    "SCENE_FIRE_BS": "FIRE_bs",
    "SCENE_MIZUSIN_BS": "MIZUsin_bs",
    "SCENE_JYASINBOSS": "jyasinboss",
    "SCENE_HAKADAN_BS": "HAKAdan_bs",
    "SCENE_GANON_BOSS": "ganon_boss",
    "SCENE_GANON_FINAL": "ganon_final",
    "SCENE_ENTRA": "entra",
    "SCENE_ENTRA_N": "entra_n",
    "SCENE_ENRUI": "enrui",
    "SCENE_MARKET_ALLEY": "market_alley",
    "SCENE_MARKET_ALLEY_N": "market_alley_n",
    "SCENE_MARKET_DAY": "market_day",
    "SCENE_MARKET_NIGHT": "market_night",
    "SCENE_MARKET_RUINS": "market_ruins",
    "SCENE_SHRINE": "shrine",
    "SCENE_SHRINE_N": "shrine_n",
    "SCENE_SHRINE_R": "shrine_r",
    "SCENE_KOKIRI_HOME": "kokiri_home",
    "SCENE_KOKIRI_HOME3": "kokiri_home3",
    "SCENE_KOKIRI_HOME4": "kokiri_home4",
    "SCENE_KOKIRI_HOME5": "kokiri_home5",
    "SCENE_KAKARIKO": "kakariko",
    "SCENE_KAKARIKO3": "kakariko3",
    "SCENE_SHOP1": "shop1",
    "SCENE_KOKIRI_SHOP": "kokiri_shop",
    "SCENE_GOLON": "golon",
    "SCENE_ZOORA": "zoora",
    "SCENE_DRAG": "drag",
    "SCENE_ALLEY_SHOP": "alley_shop",
    "SCENE_NIGHT_SHOP": "night_shop",
    "SCENE_FACE_SHOP": "face_shop",
    "SCENE_LINK_HOME": "link_home",
    "SCENE_IMPA": "impa",
    "SCENE_MALON_STABLE": "malon_stable",
    "SCENE_LABO": "labo",
    "SCENE_HYLIA_LABO": "hylia_labo",
    "SCENE_TENT": "tent",
    "SCENE_HUT": "hut",
    "SCENE_DAIYOUSEI_IZUMI": "daiyousei_izumi",
    "SCENE_YOUSEI_IZUMI_TATE": "yousei_izumi_tate",
    "SCENE_YOUSEI_IZUMI_YOKO": "yousei_izumi_yoko",
    "SCENE_KAKUSIANA": "kakusiana",
    "SCENE_HAKAANA": "hakaana",
    "SCENE_HAKAANA2": "hakaana2",
    "SCENE_HAKAANA_OUKE": "hakaana_ouke",
    "SCENE_SYATEKIJYOU": "syatekijyou",
    "SCENE_TOKINOMA": "tokinoma",
    "SCENE_KENJYANOMA": "kenjyanoma",
    "SCENE_HAIRAL_NIWA": "hairal_niwa",
    "SCENE_HAIRAL_NIWA_N": "hairal_niwa_n",
    "SCENE_HIRAL_DEMO": "hiral_demo",
    "SCENE_HAKASITARELAY": "hakasitarelay",
    "SCENE_TURIBORI": "turibori",
    "SCENE_NAKANIWA": "nakaniwa",
    "SCENE_BOWLING": "bowling",
    "SCENE_SOUKO": "souko",
    "SCENE_MIHARIGOYA": "miharigoya",
    "SCENE_MAHOUYA": "mahouya",
    "SCENE_GANON_DEMO": "ganon_demo",
    "SCENE_KINSUTA": "kinsuta",
    "SCENE_SPOT00": "spot00",
    "SCENE_SPOT01": "spot01",
    "SCENE_SPOT02": "spot02",
    "SCENE_SPOT03": "spot03",
    "SCENE_SPOT04": "spot04",
    "SCENE_SPOT05": "spot05",
    "SCENE_SPOT06": "spot06",
    "SCENE_SPOT07": "spot07",
    "SCENE_SPOT08": "spot08",
    "SCENE_SPOT09": "spot09",
    "SCENE_SPOT10": "spot10",
    "SCENE_SPOT11": "spot11",
    "SCENE_SPOT12": "spot12",
    "SCENE_SPOT13": "spot13",
    "SCENE_SPOT15": "spot15",
    "SCENE_SPOT16": "spot16",
    "SCENE_SPOT17": "spot17",
    "SCENE_SPOT18": "spot18",
    "SCENE_SPOT20": "spot20",
    "SCENE_GANON_TOU": "ganon_tou",
    "SCENE_TEST01": "test01",
    "SCENE_BESITU": "besitu",
    "SCENE_DEPTH_TEST": "depth_test",
    "SCENE_SYOTES": "syotes",
    "SCENE_SYOTES2": "syotes2",
    "SCENE_SUTARU": "sutaru",
    "SCENE_HAIRAL_NIWA2": "hairal_niwa2",
    "SCENE_SASATEST": "sasatest",
    "SCENE_TESTROOM": "testroom",
}

ootEnumCamTransition = [
    ("Custom", "Custom", "Custom"),
    ("0x00", "0x00", "0x00"),
    # ("0x0F", "0x0F", "0x0F"),
    # ("0xFF", "0xFF", "0xFF"),
]

# see curRoom.unk_03
ootEnumRoomBehaviour = [
    ("Custom", "Custom", "Custom"),
    ("0x00", "Default", "Default"),
    ("0x01", "Dungeon Behavior (Z-Target, Sun's Song)", "Dungeon Behavior (Z-Target, Sun's Song)"),
    ("0x02", "Disable Backflips/Sidehops", "Disable Backflips/Sidehops"),
    ("0x03", "Disable Color Dither", "Disable Color Dither"),
    ("0x04", "(?) Horse Camera Related", "(?) Horse Camera Related"),
    ("0x05", "Disable Darker Screen Effect (NL/Spins)", "Disable Darker Screen Effect (NL/Spins)"),
]

ootEnumExitIndex = [
    ("Custom", "Custom", "Custom"),
    ("Default", "Default", "Default"),
]

ootEnumSceneSetupPreset = [
    ("Custom", "Custom", "Custom"),
    ("All Scene Setups", "All Scene Setups", "All Scene Setups"),
    ("All Non-Cutscene Scene Setups", "All Non-Cutscene Scene Setups", "All Non-Cutscene Scene Setups"),
]

ootEnumCSWriteType = [
    ("Custom", "Custom", "Provide the name of a cutscene header variable"),
    ("Embedded", "Embedded", "Cutscene data is within scene header (deprecated)"),
    ("Object", "Object", "Reference to Blender object representing cutscene"),
]

ootEnumCSListType = [
    ("Textbox", "Textbox", "Textbox"),
    ("FX", "Scene Trans FX", "Scene Trans FX"),
    ("Lighting", "Lighting", "Lighting"),
    ("Time", "Time", "Time"),
    ("PlayBGM", "Play BGM", "Play BGM"),
    ("StopBGM", "Stop BGM", "Stop BGM"),
    ("FadeBGM", "Fade BGM", "Fade BGM"),
    ("Misc", "Misc", "Misc"),
    ("0x09", "Cmd 09", "Cmd 09"),
    ("Unk", "Unknown Data", "Unknown Data"),
]

ootEnumCSListTypeIcons = [
    "ALIGN_BOTTOM",
    "COLORSET_10_VEC",
    "LIGHT_SUN",
    "TIME",
    "PLAY",
    "SNAP_FACE",
    "IPO_EASE_IN_OUT",
    "OPTIONS",
    "EVENT_F9",
    "QUESTION",
]

ootEnumCSListTypeListC = {
    "Textbox": "CS_TEXT_LIST",
    "FX": "CS_SCENE_TRANS_FX",
    "Lighting": "CS_LIGHTING_LIST",
    "Time": "CS_TIME_LIST",
    "PlayBGM": "CS_PLAY_BGM_LIST",
    "StopBGM": "CS_STOP_BGM_LIST",
    "FadeBGM": "CS_FADE_BGM_LIST",
    "Misc": "CS_MISC_LIST",
    "0x09": "CS_CMD_09_LIST",
    "Unk": "CS_UNK_DATA_LIST",
}

ootEnumCSListTypeEntryC = {
    "Textbox": None,  # special case
    "FX": None,  # no list entries
    "Lighting": "CS_LIGHTING",
    "Time": "CS_TIME",
    "PlayBGM": "CS_PLAY_BGM",
    "StopBGM": "CS_STOP_BGM",
    "FadeBGM": "CS_FADE_BGM",
    "Misc": "CS_MISC",
    "0x09": "CS_CMD_09",
    "Unk": "CS_UNK_DATA",
}

ootEnumCSTextboxType = [("Text", "Text", "Text"), ("None", "None", "None"), ("LearnSong", "Learn Song", "Learn Song")]

ootEnumCSTextboxTypeIcons = ["FILE_TEXT", "HIDE_ON", "FILE_SOUND"]

ootEnumCSTextboxTypeEntryC = {
    "Text": "CS_TEXT_DISPLAY_TEXTBOX",
    "None": "CS_TEXT_NONE",
    "LearnSong": "CS_TEXT_LEARN_SONG",
}

ootEnumCSTransitionType = [
    ("1", "To White +", "Also plays whiteout sound for certain scenes/entrances"),
    ("2", "To Blue", "To Blue"),
    ("3", "From Red", "From Red"),
    ("4", "From Green", "From Green"),
    ("5", "From White", "From White"),
    ("6", "From Blue", "From Blue"),
    ("7", "To Red", "To Red"),
    ("8", "To Green", "To Green"),
    ("9", "Set Unk", "gSaveContext.unk_1410 = 1, works with scene xn 11/17"),
    ("10", "From Black", "From Black"),
    ("11", "To Black", "To Black"),
    ("12", "To Dim Unk", "Fade gSaveContext.unk_1410 255>100, works with scene xn 11/17"),
    ("13", "From Dim", "Alpha 100>255"),
]

ootEnumDrawConfig = [
    ("Custom", "Custom", "Custom"),
    ("SDC_DEFAULT", "Default", "Default"),
    ("SDC_SPOT00", "Hyrule Field (Spot00)", "Spot00"),
    ("SDC_SPOT01", "Kakariko Village (Spot01)", "Spot01"),
    ("SDC_SPOT03", "Zora's River (Spot03)", "Spot03"),
    ("SDC_SPOT04", "Kokiri Forest (Spot04)", "Spot04"),
    ("SDC_SPOT06", "Lake Hylia (Spot06)", "Spot06"),
    ("SDC_SPOT07", "Zora's Domain (Spot07)", "Spot07"),
    ("SDC_SPOT08", "Zora's Fountain (Spot08)", "Spot08"),
    ("SDC_SPOT09", "Gerudo Valley (Spot09)", "Spot09"),
    ("SDC_SPOT10", "Lost Woods (Spot10)", "Spot10"),
    ("SDC_SPOT11", "Desert Colossus (Spot11)", "Spot11"),
    ("SDC_SPOT12", "Gerudo's Fortress (Spot12)", "Spot12"),
    ("SDC_SPOT13", "Haunted Wasteland (Spot13)", "Spot13"),
    ("SDC_SPOT15", "Hyrule Castle (Spot15)", "Spot15"),
    ("SDC_SPOT16", "Death Mountain Trail (Spot16)", "Spot16"),
    ("SDC_SPOT17", "Death Mountain Crater (Spot17)", "Spot17"),
    ("SDC_SPOT18", "Goron City (Spot18)", "Spot18"),
    ("SDC_SPOT20", "Lon Lon Ranch (Spot20)", "Spot20"),
    ("SDC_HIDAN", "Fire Temple (Hidan)", "Hidan"),
    ("SDC_YDAN", "Inside the Deku Tree (Ydan)", "Ydan"),
    ("SDC_DDAN", "Dodongo's Cavern (Ddan)", "Ddan"),
    ("SDC_BDAN", "Inside Jabu Jabu's Belly (Bdan)", "Bdan"),
    ("SDC_BMORI1", "Forest Temple (Bmori1)", "Bmori1"),
    ("SDC_MIZUSIN", "Water Temple (Mizusin)", "Mizusin"),
    ("SDC_HAKADAN", "Shadow Temple (Hakadan)", "Hakadan"),
    ("SDC_JYASINZOU", "Spirit Temple (Jyasinzou)", "Jyasinzou"),
    ("SDC_GANONTIKA", "Inside Ganon's Castle (Ganontika)", "Ganontika"),
    ("SDC_MEN", "Gerudo Training Ground (Men)", "Men"),
    ("SDC_YDAN_BOSS", "Gohma's Lair (Ydan Boss)", "Ydan Boss"),
    ("SDC_MIZUSIN_BS", "Morpha's Lair (Mizusin Bs)", "Mizusin Bs"),
    ("SDC_TOKINOMA", "Temple of Time (Tokinoma)", "Tokinoma"),
    ("SDC_KAKUSIANA", "Grottos (Kakusiana)", "Kakusiana"),
    ("SDC_KENJYANOMA", "Chamber of the Sages (Kenjyanoma)", "Kenjyanoma"),
    ("SDC_GREAT_FAIRY_FOUNTAIN", "Great Fairy Fountain", "Great Fairy Fountain"),
    ("SDC_SYATEKIJYOU", "Shooting Gallery (Syatekijyou)", "Syatekijyou"),
    ("SDC_HAIRAL_NIWA", "Castle Hedge Maze (Day) (Hairal Niwa)", "Hairal Niwa"),
    ("SDC_GANON_CASTLE_EXTERIOR", "Ganon's Castle Exterior (Ganon Tou)", "Ganon Tou"),
    ("SDC_ICE_DOUKUTO", "Ice Cavern (Ice Doukuto)", "Ice Doukuto"),
    ("SDC_GANON_FINAL", "Ganondorf's Death Scene (Tower Escape Exterior) (Ganon Final)", "Ganon Final"),
    ("SDC_FAIRY_FOUNTAIN", "Fairy Fountain", "Fairy Fountain"),
    ("SDC_GERUDOWAY", "Thieves' Hideout (Gerudoway)", "Gerudoway"),
    ("SDC_BOWLING", "Bombchu Bowling Alley (Bowling)", "Bowling"),
    ("SDC_HAKAANA_OUKE", "Royal Family's Tomb (Hakaana Ouke)", "Hakaana Ouke"),
    ("SDC_HYLIA_LABO", "Lakeside Laboratory (Hylia Labo)", "Hylia Labo"),
    ("SDC_SOUKO", "Lon Lon Ranch House & Tower (Souko)", "Souko"),
    ("SDC_MIHARIGOYA", "Guard House (Miharigoya)", "Miharigoya"),
    ("SDC_MAHOUYA", "Granny's Potion Shop (Mahouya)", "Mahouya"),
    ("SDC_CALM_WATER", "Calm Water", "Calm Water"),
    ("SDC_GRAVE_EXIT_LIGHT_SHINING", "Grave Exit Light Shining", "Grave Exit Light Shining"),
    ("SDC_BESITU", "Ganondorf Test Room (Besitu)", "Besitu"),
    ("SDC_TURIBORI", "Fishing Pond (Turibori)", "Turibori"),
    ("SDC_GANON_SONOGO", "Ganon's Tower (Collapsing) (Ganon Sonogo)", "Ganon Sonogo"),
    ("SDC_GANONTIKA_SONOGO", "Inside Ganon's Castle (Collapsing) (Ganontika Sonogo)", "Ganontika Sonogo"),
]
