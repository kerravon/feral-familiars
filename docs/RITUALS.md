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

When gifting, the **SENDER** pays the ritual fee (tax).
- **Essences:** 2% of total amount (Min 1).
- **Spirits:** 
  - Common: 1 Essence
  - Uncommon: 3 Essences
  - Rare: 5 Essences
  - Legendary: 13 Essences

## 🧪 Trading (Transmute)
`/transmute user`

When trading, the **RECIPIENT** pays the ritual fee (tax) for each item received.
- **Essences:** 5% of total (Min 1).
- **Spirits:**
  - Common: 2 Essences
  - Uncommon: 5 Essences
  - Rare: 10 Essences
  - Legendary: 25 Essences

*Note: All fees can be paid using any essence type of the player's choice.*

## 🔥 Resonance & Passives
Once a familiar is created and `/summoned`, you must ignite its resonance to benefit from its passive powers.

### Activation
- **Method:** `/familiar [name]` -> Click **Ignite Resonance**.
- **Duration:** **4 Hours**.
- **Frequency:** Once per day per familiar.
- **Triggers:** **Unlimited** during the 4-hour window.

### Modes
Players can switch between two resonance modes at any time:
1.  **ECHO (Default):** Grants a chance to gain an extra essence of the **same type** as the one captured.
2.  **PULSE:** Grants a chance to gain an extra essence of a **random different element**.
