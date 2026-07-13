import random
import streamlit as st

# ==========================================
# 1. MASTER LOOT DATA BOILERPLATE
# ==========================================
REGIONS = {
    "1. Deep Core": {"chance": 2, "rarity": 4, "quantity": 0},      # Excellent, Legendary, Miniscule
    "2. Core Worlds": {"chance": 2, "rarity": 3, "quantity": 1},    # Excellent, Epic, Small
    "3. The Colonies": {"chance": 1, "rarity": 3, "quantity": 1},   # Good, Epic, Small
    "4. The Inner Rim": {"chance": 0, "rarity": 2, "quantity": 2},  # Average, Rare, Medium
    "5. Expansion Region": {"chance": 0, "rarity": 2, "quantity": 3},# Average, Rare, Large
    "6. Mid Rim": {"chance": -1, "rarity": 1, "quantity": 3},       # Meager, Uncommon, Large
    "7. Outer Rim": {"chance": -1, "rarity": 1, "quantity": 4},      # Meager, Uncommon, Huge
    "8. Hutt Space": {"chance": 1, "rarity": 2, "quantity": 4},     # Good, Rare, Huge
    "9. Corporate Sector": {"chance": 1, "rarity": 3, "quantity": 2},# Good, Epic, Medium
    "10. Unknown Regions (Dynamic)": {"chance": "var_unk", "rarity": 4, "quantity": "var_unk"},
    "11. Wild Space (Dynamic)": {"chance": "var_wild", "rarity": "var_wild", "quantity": 4}
}

FACTIONS = {
    "Imperial Control": {"chance": -1, "rarity": 1, "quantity": -1},
    "Rebellion / Galactic Republic": {"chance": 1, "rarity": 0, "quantity": 1},
    "Free Space": {"chance": 0, "rarity": -1, "quantity": 1},
    "Gang / Cartel Control": {"chance": 1, "rarity": 1, "quantity": 0}
}

PLANETS = {
    "Tech World": ["Weapon Schematic", "Prototype Weapon Mod", "Research Data Cache", "Advanced Cybernetics", "Targeting Computer"],
    "Ship Graveyard": ["Hyperdrive Part", "Hull Plating", "Shield Generator", "Wiring Harness", "Heavy Scrap Metal"],
    "Droid World": ["Droid Servo Arm", "Memory Core", "Behavior Matrix", "Ion Blaster", "Automated Repair Kit"],
    "Junk World": ["Jury-Rigged Blaster", "Reclaimed Power Cell", "Scrap Armor Plate", "Dent Electronic Components", "Vibro-Shiv"],
    "Force Sensitive": ["Kyber Crystal Shard", "Jedi Holocron", "Sith Holocron", "Ancient Sword Hilt", "Focusing Robes"],
    "Ancient Ruins": ["Pre-Republic Relic", "Ceremonial Armor Piece", "Priceless Antique Trinket", "Sith Lore Scroll"],
    "Agri-World": ["Emergency Medpac", "Specialized Stim-Shot", "Field Rations", "Tracking Scanner", "Heavy Wilderness Cloak"],
    "Mining World": ["Coaxium Fuel Canister", "Heavy Mining Laser", "Reinforced Hazard Suit", "Detonation Charge", "Industrial Plasma Cutter"]
}

UNIVERSAL_LOOT = {
    "Organic": ["Medicinal Herb Extract", "Bio-Toxin Venom", "Rigid Leather Hide", "Dense Plant Fiber", "Nutritious Seed Pod"],
    "Inorganic": ["Durasteel Ore Shard", "Unrefined Doonium", "Kyber Dust Granules", "Plastoid Composite Scrap", "Tibanna Gas Capsule"]
}

# ==========================================
# 2. APP INTERFACE LAYOUT
# ==========================================
st.set_page_config(page_title="Star Wars Loot Generator", page_icon="🌌", layout="centered")
st.title("🌌 Star Wars 3-Tier Loot Generator")
st.caption("A mathematically balanced, lore-accurate galactic drop engine.")

# Dropdowns for User Selections
col1, col2, col3 = st.columns(3)
with col1:
    selected_region = st.selectbox("1. Select Region", list(REGIONS.keys()))
with col2:
    selected_faction = st.selectbox("2. System Control", list(FACTIONS.keys()))
with col3:
    selected_planet = st.selectbox("3. Planet Flavor/Biome", list(PLANETS.keys()))

loot_type = st.radio("Loot Scaling Model", ["Individual Drop (d20 Dice Pool)", "Bulk Cargo Shipment (d100 Multiplier)"], horizontal=True)

# ==========================================
# 3. CORE MATHEMATICAL GENERATOR ENGINE
# ==========================================
if st.button("🔴 ROLL FOR LOOT", type="primary", use_container_width=True):
    
    # --- Step A: Process Dynamic Region Ranges ---
    reg_data = REGIONS[selected_region].copy()
    if selected_region == "10. Unknown Regions (Dynamic)":
        reg_data["chance"] = random.choice([0, 1, 2]) # None to Excellent
        reg_data["quantity"] = random.choice([0, 1, 2]) # Miniscule to Medium
    elif selected_region == "11. Wild Space (Dynamic)":
        reg_data["chance"] = random.choice([-1, 0, 1]) # Meager to Good
        reg_data["rarity"] = random.choice([0, 1, 2]) # Common to Rare

    fac_data = FACTIONS[selected_faction]

    # --- Step B: Calculate Final Tier Positions (With Floor Safeguards & Overflow) ---
    final_modifiers = {}
    for stat in ["chance", "rarity", "quantity"]:
        base_tier = reg_data[stat]
        faction_shift = fac_data[stat]
        
        # Check for Overflow Rule (+10% Bonus if pushing past max tier via active upgrade)
        overflow_bonus = 0
        if base_tier >= 4 and faction_shift > 0:
            overflow_bonus = 10
            final_tier = base_tier
        else:
            final_tier = base_tier + faction_shift
            # Enforce Natural Floor Safeguard
            if final_tier < base_tier:
                final_tier = base_tier
        
        # Convert Tiers to Raw Percentage values
        if stat == "chance":
            percentages = {0: 0, 1: -10, 2: 0, 3: 5, 4: 10} # None, Meager, Average, Good, Excellent
            final_modifiers["chance"] = percentages.get(final_tier, 0) + overflow_bonus
        elif stat == "rarity":
            final_modifiers["rarity"] = (final_tier * 5) + overflow_bonus # 0=0%, 1=5%, 2=10%, 3=15%, 4=20%
        elif stat == "quantity":
            final_modifiers["quantity"] = final_tier # Keep tier integer for Dice Pool / Bracket assignment

    # --- Step C: Roll The Loot Chance (The Gatekeeper) ---
    base_drop_rate = 65 # Standard baseline drop rate
    final_drop_chance = base_drop_rate + final_modifiers["chance"]
    chance_roll = random.randint(1, 100)

    if REGIONS[selected_region]["chance"] == 0 and selected_region != "10. Unknown Regions (Dynamic)": 
        # Absolute hardcoded 'None' region setting handling
        st.error("❌ No Loot Dropped. (Region baseline dictates absolute zero item presence here).")
    elif chance_roll > final_drop_chance:
        st.warning(f"💨 The search came up empty! (Rolled {chance_roll} vs Required {final_drop_chance}% or lower)")
    else:
        # --- Step D: Roll Quantity (Dice Pool / Multiplier Blueprint) ---
        q_tier = final_modifiers["quantity"]
        
        st.success(f"🎉 Loot Found! (Drop Check Succeeded: Rolled {chance_roll} vs {final_drop_chance}%)")
        st.subheader("📦 Discovered Cargo / Items:")

        if "Individual" in loot_type:
            # Dice Pool Option: Tiers dictate number of d4 rolled
            dice_count = max(1, q_tier + 1)
            total_items = sum(random.randint(1, 4) for _ in range(dice_count))
            
            # Generate the specific items
            for i in range(total_items):
                # Roll Rarity on d100
                rarity_roll = random.randint(1, 100) + final_modifiers["rarity"]
                if rarity_roll >= 100: rarity, color = "LEGENDARY", "🔥"
                elif rarity_roll >= 96: rarity, color = "EPIC", "💜"
                elif rarity_roll >= 86: rarity, color = "RARE", "💙"
                elif rarity_roll >= 61: rarity, color = "UNCOMMON", "💚"
                else: rarity, color = "COMMON", "⚪"

                # Pick item flavor from planetary pool or universal crafting pools
                pool_choice = random.choice(["planet", "organic", "inorganic"])
                if pool_choice == "planet":
                    item_name = random.choice(PLANETS[selected_planet])
                elif pool_choice == "organic":
                    item_name = random.choice(UNIVERSAL_LOOT["Organic"])
                else:
                    item_name = random.choice(UNIVERSAL_LOOT["Inorganic"])

                st.markdown(f"{color} **[{rarity}]** {item_name}")
                
        else:
            # Bulk Cargo Option: Tiers dictate raw multiplier bracket on d100
            base_roll = random.randint(1, 100)
            multipliers = {0: 0.1, 1: 0.5, 2: 1.0, 3: 1.5, 4: 2.0}
            bracket = multipliers.get(q_tier, 1.0)
            total_tonnage = round(base_roll * bracket, 1)

            resource_type = random.choice(UNIVERSAL_LOOT["Organic"] + UNIVERSAL_LOOT["Inorganic"] + ["Raw Starship Scrap Metal"])
            st.metric(label="Bulk Shipment Volume Extracted", value=f"{total_tonnage} Tonnes", delta=resource_type)
