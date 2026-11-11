# Visual Assets Inventory & Specification

This document inventories all visual assets present in the website directory, providing their technical specifications, contextual meaning, and recommended integration across the landing page and marketing channels.

---

## Asset Catalog

### 1. `KaffanImage.jpeg`
- **File Dimensions**: 2048 × 2048 px (Square)
- **File Size**: ~1.6 MB
- **Color Profile**: RGB, warm neutral studio lighting
- **Depiction**: Primary product presentation. Features neatly folded, clean white cotton Kaffan garments displayed on an elegant dark wooden or stone surface with soft ambient lighting, showcasing the dignity and purity of the product.
- **Landing Page Role**:
  - Hero visual badge / floating card.
  - Primary product teaser in the introductory section.
  - Open Graph / Social Media preview image (`og:image`).

---

### 2. `Kaffan3piece.jpeg`
- **File Dimensions**: 2048 × 2048 px (Square)
- **File Size**: ~1.5 MB
- **Color Profile**: RGB
- **Depiction**: Men's complete 3-piece Kaffan layout. Shows the three distinct cut components (Lifafa, Izar, and Qamees) folded with precision and presented together to demonstrate what the customer receives in the set.
- **Landing Page Role**:
  - Primary image for the "Men's Kaffan Set" product card.
  - Visual reference in the sizing and pieces breakdown section.

---

### 3. `TiedKaffan.jpeg`
- **File Dimensions**: 2048 × 2048 px (Square)
- **File Size**: ~1.5 MB
- **Color Profile**: RGB
- **Depiction**: Demonstration of the completed shroud (Takfeen) after wrapping, illustrating the traditional tying ribbons at the head, waist, and feet. Represents the solemn, dignified final presentation according to Sunnah.
- **Landing Page Role**:
  - Primary image for the "Women's Kaffan Set" product card or Sunnah Guide section.
  - Illustrative hero banner for "The Sunnah of Takfeen" educational breakdown.

---

### 4. `Unstitched.jpeg`
- **File Dimensions**: 2048 × 2048 px (Square)
- **File Size**: ~1.3 MB
- **Color Profile**: RGB
- **Depiction**: Pure unstitched cotton rolls / draped fabric bolt, emphasizing the natural purity, absence of synthetic fibers, and authentic unstitched character mandated by Islamic tradition.
- **Landing Page Role**:
  - Supporting visual in the "Fabric & Craftsmanship" / "Purity Guaranteed" section.
  - Background overlay or card graphic for institutional supply.

---

### 5. `macroTexture.jpeg`
- **File Dimensions**: 2048 × 2048 px (Square)
- **File Size**: ~1.9 MB
- **Color Profile**: RGB
- **Depiction**: Extreme close-up macro shot of the cotton fabric weave. Reveals the breathable, tight, opaque plain-weave texture, demonstrating that the fabric is non-sheer, tear-resistant, and high thread-count.
- **Landing Page Role**:
  - Highlighting fabric quality, durability, and soft touch in the "Fabric Guarantee" block.
  - Reassuring customers regarding non-transparency (a crucial requirement in Islamic burials).

---

### 6. `KaffansMan.png`
- **File Dimensions**: 1254 × 1254 px (Square)
- **File Size**: ~671 KB
- **Format**: PNG with transparency
- **Depiction**: Visual diagram / schematic for the Men's 3-piece shroud. Outlines the 3 garments (Lifafa, Izar, Qamees) with geometric cutouts and measurement references for quick understanding.
- **Landing Page Role**:
  - Embedded directly inside the Men's Tab of the Sizing Guide (`#sizes`).
  - Visual aid for funeral coordinators and families to verify garment cuts before wrapping.

---

### 7. `KaffanLadies.png`
- **File Dimensions**: 800 × 800 px (Square)
- **File Size**: ~178 KB
- **Format**: PNG with transparency
- **Depiction**: Visual diagram / schematic for the Women's 5-piece shroud. Depicts the 5 essential components (Lifafa, Qamees, Izar, Khimar/Aurni head covering, and Seenah-band chest wrap) with dimensions.
- **Landing Page Role**:
  - Embedded directly inside the Women's Tab of the Sizing Guide (`#sizes`).
  - Essential reference clarifying the placement and sequence of the 5 female burial garments.

---

## Best Practices for Frontend Integration

1. **Responsive Sizing & Modern Attributes**:
   - Always supply `loading="lazy"` and `decoding="async"` for below-the-fold images to maintain fast Largest Contentful Paint (LCP).
   - Set `fetchpriority="high"` on the main Hero image (`KaffanImage.jpeg`).
   - Use explicit `width` and `height` attributes to avoid Cumulative Layout Shift (CLS).
2. **Accessible Descriptions (`alt` text)**:
   - Provide culturally respectful, descriptive `alt` text explaining the garment pieces rather than generic labels.
   - Example: `alt="Wasim Trader Men's Kaffan Set showing 3 folded pure white cotton pieces"`
3. **Aspect Ratio Containers**:
   - Wrap product cards and diagrams in clean `aspect-ratio: 1/1` containers with subtle borders and shadows to preserve crisp framing across mobile and desktop viewports.
