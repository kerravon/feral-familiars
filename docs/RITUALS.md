# 🧪 Rituals & Taxes

## ✨ Ritual (Familiar Creation)
`/ritual spirit_id essence_type`

To create a familiar, you must combine a captured **Spirit** with a specific number of **Essences** of a single type.

### Costs by Rarity
- **Common:** 10 Essences
- **Uncommon:** 20 Essences
- **Rare:** 40 Essences
- **Legendary:** 80 Essences

### 🕯️ Special: Restless Spirits
Restless spirits are unstable and require an infusion of **Arcane Essence** in addition to their base element to be bound:
- **Common:** +5 Arcane
- **Uncommon:** +10 Arcane
- **Rare:** +15 Arcane
- **Legendary:** +25 Arcane

## 🎁 Gifting (Bestow)
`/bestow user tax_payment essence_type amount`
`/bestow user tax_payment spirit_id`

When gifting, the **SENDER** pays the ritual fee (tax) into the **Well of Souls**.
- **Essences:** 3% of total amount (Min 1).
- **Spirits:** 
  - Common: 2 Essences
  - Uncommon: 5 Essences
  - Rare: 10 Essences
  - Legendary: 25 Essences

## 🧪 Trading (Transmute)
`/transmute user`

When trading, the **RECIPIENT** pays the ritual fee (tax) into the **Well of Souls** for each item received.
- **Essences:** 3% of total (Min 1).
- **Spirits:**
  - Common: 2 Essences
  - Uncommon: 5 Essences
  - Rare: 10 Essences
  - Legendary: 25 Essences

## 🌌 The Well of Souls (Guild Pot)
All ritual fees from gifting and trading are collected into the server's **Well of Souls**.
- **Commands:** `/vault` (View status), `/donate` (Contribute voluntarily).
- **Overflow Event:** When the total essence in the Well reaches its threshold (Default 1,000), it overflows, triggering a **Prismatic Surge**—a series of **8 immediate spawns** for everyone in the server!

## 🔥 Resonance & Passives
Once a familiar is created and `/summoned`, you must ignite its resonance to benefit from its passive powers.

### Activation
- **Method:** `/familiar [name]` -> Click **Ignite Resonance**.
- **Constraint:** The familiar **must be currently `/summoned`** to ignite resonance.
- **Duration:** **4 Hours**.
- **Global Limit:** A player can only ignite resonance **2 times per day** across their entire stable.
- **Familiar Limit:** Each specific familiar can only be ignited **once per day**.
- **Auto-End:** If you swap to a different familiar using `/summon`, any active resonance **immediately ends**.
- **Triggers:** **Unlimited** during the 4-hour window.

### Modes
Players can switch resonance modes at any time, provided they have reached the required Level:
1.  **ECHO (Level 1):** Grants a chance to gain an extra essence of the **same type** as the one captured, provided the element **matches the familiar** (Arcane familiars double any element).
2.  **PULSE (Level 5):** Grants a chance to gain an extra essence of a **random different element**.
3.  **ATTRACT (Level 8):** Grants a chance to gain an extra essence of a **player-chosen element** (Set via `/set-attract`).

## 📈 Feeding & Progression
Familiars gain XP and grow in power through binding and feeding.
- **XP per Level:** Requirements increase with level (e.g., 100 XP for Level 2, up to 4,000 XP for Level 10).
- **Growth Rolls:** Every level-up grants a permanent **+0.5% to +2.0%** bonus to the familiar's passive trigger chance.
- **Feeding Command:** `/feed [familiar] [essence] [amount]`
  - Matching Element: 10 XP/ea.
  - Arcane Essence: 20 XP/ea.
  - Other Essence: 2 XP/ea.
