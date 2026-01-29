import json
import os

# Define stat lists for categorization
ESSENCE_SKILL_STATS = [
    "Assault", "Brutality", "Combative", "Crusher", "Detonate",
    "Efficacy", "Flow", "Fracture", "Infliction", "Inspiring",
    "Medicant", "Pursuit", "Suppression", "Twilight"
]
SECONDARY_STATS = [
    "Attack Boost", "Physical DMG Boost", "Heat DMG Boost",
    "Electric DMG Boost", "Cryo DMG Boost", "Nature DMG Boost",
    "Critical Rate Boost", "HP Boost", "Originium Arts Boost",
    "Ultimate Gain Boost", "Arts DMG Boost", "Ultimate Gain Efficiency Boost",
    "Treatment Efficiency Boost", "Arts Intensity Boost", "Arts Boost"
]
ATTRIBUTE_STATS = [
    "Agility Boost", "Strength Boost", "Will Boost",
    "Intellect Boost", "Main Attribute Boost"
]

WEAPON_TYPE_MAP = {
    "Sword": "Sword",
    "Claymores": "Great Sword",
    "Lance": "Polearm",
    "Pistol": "Handcannon",
    "Wand": "Arts Unit"
}

def main():
    # Define paths
    base_path = './EndfieldData'
    table_cfg_path = os.path.join(base_path, 'TableCfg')
    i18n_path = os.path.join(base_path, 'i18n')
    output_path = './weaponData.json'

    # Load necessary files
    print("Loading data files...")
    try:
        with open(os.path.join(table_cfg_path, 'WeaponBasicTable.json'), 'r') as f:
            weapon_basic_table = json.load(f)
        
        with open(os.path.join(i18n_path, 'I18nTextTable_EN.json'), 'r') as f:
            i18n_en_table = json.load(f)

        with open(os.path.join(table_cfg_path, 'EquipItemTable.json'), 'r') as f:
            equip_item_table = json.load(f)

        with open(os.path.join(table_cfg_path, 'SkillPatchTable.json'), 'r') as f:
            skill_patch_table = json.load(f)

    except FileNotFoundError as e:
        print(f"Error: {e}. Make sure you are running this script from the correct directory.")
        return

    # The i18n table is already a lookup dictionary
    i18n_lookup = i18n_en_table

    processed_weapons = []
    print(f"Processing {len(weapon_basic_table)} weapons...")

    for weapon_id, weapon_data in weapon_basic_table.items():
        # Get name and description
        name = i18n_lookup.get(str(weapon_data['engName']['id']), '')
        description = i18n_lookup.get(str(weapon_data['weaponDesc']['id']), '')

        # Process skills and attributes
        skills = []
        attributes = []
        for skill_id in weapon_data.get('weaponSkillList', []):
            skill_info = {}
            if skill_id in skill_patch_table:
                skill_patch_data = skill_patch_table[skill_id]["SkillPatchDataBundle"][0]
                skill_info['name'] = i18n_lookup.get(str(skill_patch_data['skillName']['id']), skill_id)
                skill_info['description'] = i18n_lookup.get(str(skill_patch_data['description']['id']), '')
                
                if 'blackboard' in skill_patch_data:
                    for attr in skill_patch_data['blackboard']:
                        attributes.append({
                            'key': attr.get('key'),
                            'value': attr.get('value')
                        })
                skills.append(skill_info)
            else:
                skills.append({'name': skill_id, 'description': 'Definition not found'})


        # Categorize skills
        essence_skill_stat = None
        secondary_stats = []
        attribute_stats = []

        for skill in skills:
            skill_name = skill['name']

            # Find Essence Skill Stat
            if not essence_skill_stat:
                for stat in ESSENCE_SKILL_STATS:
                    if skill_name.startswith(stat):
                        essence_skill_stat = stat
                        break

            # Find Secondary Stats
            for stat in SECONDARY_STATS:
                if stat in skill_name:
                    secondary_stats.append(stat)

            # Find Attribute Stats
            for stat in ATTRIBUTE_STATS:
                if stat in skill_name:
                    attribute_stats.append(stat)

        processed_weapon = {
            'id': weapon_id,
            'name': name,
            'description': description,
            'rarity': weapon_data.get('rarity'),
            'type': WEAPON_TYPE_MAP.get(weapon_data.get('weaponType'), weapon_data.get('weaponType')),
            'skills': skills,
            'attributes': attributes,
            'essenceSkillStat': essence_skill_stat,
            'secondaryStats': list(set(secondary_stats)),
            'attributeStats': list(set(attribute_stats)),
            'logoUrl': ''  # Placeholder for logo URL
        }
        processed_weapons.append(processed_weapon)

    # Write the processed data to a new JSON file
    print(f"Writing processed data to {output_path}...")
    with open(output_path, 'w') as f:
        json.dump(processed_weapons, f, indent=2)

    print("Done.")
    
    # Write a summary of what was done
    summary = """
    Project: Arknights Endfield Weapon Data Processor

    This project processes the raw JSON data from the EndfieldData repository to create a structured database of weapons.

    What this script does:
    1.  Loads `WeaponBasicTable.json` for base weapon information.
    2.  Loads `I18nTextTable_EN.json` to map localization IDs to English text for names and descriptions.
    3.  Loads `SkillPatchTable.json` to find details about weapon skills and attributes.
    4.  It iterates through each weapon, extracts key information (ID, name, description, rarity, type), and resolves skill/attribute names and descriptions. It also extracts detailed attribute data (e.g., STR +16) from the 'blackboard' information within the skill data.
    5.  It categorizes skills into "Essence Skill Stats", "Secondary Stats", and "Attribute Stats" based on their names, and adds them to the `essenceSkillStat`, `secondaryStats`, and `attributeStats` fields, respectively.
    6.  A placeholder `logoUrl` field is added to each weapon entry for future use.
    7.  The final structured data is saved to `weaponData.json`.

    Next Steps:
    - You can now use the `weaponData.json` file to build your smart filter application.
    - The `logoUrl` fields can be manually or programmatically updated with links to weapon images.
    """
    with open('project_summary.txt', 'w') as f:
        f.write(summary)
    print("Project summary written to project_summary.txt")


if __name__ == '__main__':
    main()
