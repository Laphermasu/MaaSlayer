import json
import uuid

card_names = [
    "Bash", "Defend", "Strike", "Anger", "Armaments", "Body Slam", "Clash", "Cleave",
    "Clothesline", "Flex", "Havoc", "Headbutt", "Heavy Blade", "Iron Wave", "Perfected Strike",
    "Pommel Strike", "Shrug It Off", "Sword Boomerang", "Thunderclap", "True Grit", "Twin Strike",
    "Warcry", "Wild Strike", "Battle Trance", "Blood for Blood", "Bloodletting", "Burning Pact",
    "Carnage", "Combust", "Dark Embrace", "Disarm", "Dropkick", "Dual Wield", "Entrench", "Evolve",
    "Feel No Pain", "Fire Breathing", "Flame Barrier", "Ghostly Armor", "Hemokinesis", "Infernal Blade",
    "Inflame", "Intimidate", "Metallicize", "Power Through", "Pummel", "Rage", "Rampage", "Reckless Charge",
    "Rupture", "Searing Blow", "Second Wind", "Seeing Red", "Sentinel", "Sever Soul", "Shockwave",
    "Spot Weakness", "Uppercut", "Whirlwind", "Barricade", "Berserk", "Bludgeon", "Brutality", "Corruption",
    "Demon Form", "Double Tap", "Exhume", "Feed", "Fiend Fire", "Immolate", "Impervious", "Juggernaut",
    "Limit Break", "Offering", "Reaper", "Defend", "Neutralize", "Strike", "Survivor", "Acrobatics",
    "Backflip", "Bane", "Blade Dance", "Cloak and Dagger", "Dagger Spray", "Dagger Throw", "Deadly Poison",
    "Deflect", "Dodge and Roll", "Flying Knee", "Outmaneuver", "Piercing Wail", "Poisoned Stab", "Prepared",
    "Quick Slash", "Slice", "Sneaky Strike", "Sucker Punch", "Accuracy", "All-Out Attack", "Backstab",
    "Blur", "Bouncing Flask", "Calculated Gamble", "Caltrops", "Catalyst", "Choke", "Concentrate",
    "Crippling Cloud", "Dash", "Distraction", "Endless Agony", "Escape Plan", "Eviscerate", "Expertise",
    "Finisher", "Flechettes", "Footwork", "Heel Hook", "Infinite Blades", "Leg Sweep", "Masterful Stab",
    "Noxious Fumes", "Predator", "Reflex", "Riddle with Holes", "Setup", "Skewer", "Tactician",
    "Terror", "Well-Laid Plans", "A Thousand Cuts", "Adrenaline", "After Image", "Alchemize",
    "Bullet Time", "Burst", "Corpse Explosion", "Die Die Die", "Doppelganger", "Envenom",
    "Glass Knife", "Grand Finale", "Malaise", "Nightmare", "Phantasmal Killer", "Storm of Steel",
    "Tools of the Trade", "Unload", "Wraith Form", "Defend", "Dualcast", "Strike", "Zap",
    "Ball Lightning", "Barrage", "Beam Cell", "Charge Battery", "Claw", "Cold Snap", "Compile Driver",
    "Coolheaded", "Go for the Eyes", "Hologram", "Leap", "Rebound", "Recursion", "Stack",
    "Steam Barrier", "Streamline", "Sweeping Beam", "TURBO", "Aggregate", "Auto-Shields",
    "Blizzard", "Boot Sequence", "Bullseye", "Capacitor", "Chaos", "Chill", "Consume",
    "Darkness", "Defragment", "Doom and Gloom", "Double Energy", "Equilibrium", "FTL",
    "Force Field", "Fusion", "Genetic Algorithm", "Glacier", "Heatsinks", "Hello World",
    "Loop", "Melter", "Overclock", "Recycle", "Reinforced Body", "Reprogram", "Rip and Tear",
    "Scrape", "Self Repair", "Skim", "Static Discharge", "Storm", "Sunder", "Tempest",
    "White Noise", "All for One", "Amplify", "Biased Cognition", "Buffer", "Core Surge",
    "Creative AI", "Echo Form", "Electrodynamics", "Fission", "Hyperbeam", "Machine Learning",
    "Meteor Strike", "Multi-Cast", "Rainbow", "Reboot", "Seek", "Thunder Strike",
    "Eruption", "Strike", "Vigilance", "Bowling Bash", "Consecrate", "Crescendo",
    "Crush Joints", "Cut Through Fate", "Empty Body", "Empty Fist", "Evaluate",
    "Flurry of Blows", "Flying Sleeves", "Follow-Up", "Halt", "Just Lucky", "Pressure Points",
    "Prostrate", "Protect", "Sash Whip", "Third Eye", "Tranquility", "Battle Hymn",
    "Carve Reality", "Collect", "Conclude", "Deceive Reality", "Empty Mind", "Fasting",
    "Fear No Evil", "Foreign Influence", "Foresight", "Indignation", "Inner Peace",
    "Like Water", "Meditate", "Mental Fortress", "Nirvana", "Perseverance", "Pray",
    "Reach Heaven", "Rushdown", "Sanctity", "Sands of Time", "Signature Move", "Simmering Fury",
    "Study", "Swivel", "Talk to the Hand", "Tantrum", "Wallop", "Wave of the Hand", "Weave",
    "Wheel Kick", "Windmill Strike", "Worship", "Wreath of Flame", "Alpha", "Blasphemy",
    "Brilliance", "Conjure Blade", "Deus Ex Machina", "Deva Form", "Devotion", "Establishment",
    "Judgment", "Lesson Learned", "Master Reality", "Omniscience", "Ragnarok", "Scrawl",
    "Spirit Shield", "Vault", "Wish", "Bandage Up", "Blind", "Dark Shackles", "Deep Breath",
    "Discovery", "Dramatic Entrance", "Enlightenment", "Finesse", "Flash of Steel", "Forethought",
    "Good Instincts", "Impatience", "Jack of All Trades", "Madness", "Mind Blast", "Panacea",
    "Panic Button", "Purity", "Swift Strike", "Trip", "Apotheosis", "Chrysalis",
    "Hand of Greed", "Magnetism", "Master of Strategy", "Mayhem", "Metamorphosis",
    "Panache", "Sadistic Nature", "Secret Technique", "Secret Weapon", "The Bomb",
    "Thinking Ahead", "Transmutation", "Violence", "Apparition", "Become Almighty",
    "Beta", "Bite", "Expunger", "Fame and Fortune", "Insight", "J.A.X.", "Live Forever",
    "Miracle", "Omega", "Ritual Dagger", "Safety", "Shiv", "Smite", "Through Violence",
    "Clumsy", "Decay", "Doubt", "Injury", "Normality", "Pain", "Parasite", "Regret",
    "Shame", "Writhe", "Ascender's Bane", "Curse of the Bell", "Necronomicurse",
    "Pride", "Burn", "Dazed", "Slimed", "Void", "Wound"
]

json_data = {
    "cards": [
        {
            "exhausts": False,
            "is_playable": True,
            "cost": 1,
            "name": name,
            "type": "SKILL",
            "ethereal": False,
            "upgrades": 0,
            "rarity": "BASIC",
        }
        for name in card_names
    ]
}

# 将数据写入 JSON 文件
with open("cards.json", "w", encoding="utf-8") as f:
    json.dump(json_data, f, indent=2, ensure_ascii=False)

print("JSON 文件 cards.json 生成完成！")
