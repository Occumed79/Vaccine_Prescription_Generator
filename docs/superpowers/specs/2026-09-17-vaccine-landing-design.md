# Vaccine Prescription Generator Landing Experience

## Goal

Rebuild `Vaccine_Prescription_Generator` from the working `Pricing_Agreement_Generator` application shell while removing all pricing-agreement-specific functionality and replacing the landing-page motion system with a vaccine-specific animated scene.

## Source Application

Use `Occumed79/Pricing_Agreement_Generator` as the structural reference for:

- Streamlit application setup and full-screen landing-to-app transition
- dark Occu-Med visual system
- glass frame treatment
- responsive full-viewport layout
- existing Occu-Med logo asset and its current presentation
- Render/Python deployment pattern

Do not carry over pricing-agreement-specific business logic, templates, wording, service/price lists, currency handling, agreement generation behavior, or the floating pricing-sheet animation.

## Landing Page Visual Concept

The landing page should feature the provided stylized vaccine vial artwork as the main visual scene.

### Composition

- Keep the vaccine vials arranged in a horizontal lineup rather than floating independently around the screen.
- Preserve the current Occu-Med logo exactly as used in the pricing generator.
- Use a dark black/navy glass background consistent with the pricing generator's visual family.
- Do not introduce photorealistic floors, physical studio environments, giant decorative cards, or unrelated UI panels.

### Radiation / Bloom Effect

Each vial should emit a subtle animated aura matched to its own color.

- purple vial -> purple aura
- green vial -> green aura
- blue vial -> blue aura
- cyan vial -> cyan aura
- additional vial colors should use their own dominant hue

The aura should slowly breathe rather than flash: gradual scale, blur, and opacity changes that create a contained radiation-like glow around each vial.

### Animated Particle Field

Add a true animated particle layer behind and around the vial lineup.

- many small particles at different apparent depths
- varied particle size, opacity, blur, and velocity
- slow upward and lateral drift
- occasional brighter particles that bloom briefly
- particles near a vial should visually pick up that vial's nearby color
- motion should remain subtle enough that the vials and logo stay dominant

Particles should be generated/rendered as a lightweight browser animation layer rather than baked into a static image.

### Glass / Atmosphere

Retain the elegant glass frame / border language from the pricing generator, but do not reuse the floating pricing agreements. Background illumination may use low-opacity gradients and haze to blend the individual vial colors into the surrounding scene.

## Application Behavior

- Landing page remains full viewport.
- Clicking/tapping the landing experience enters the vaccine generator application, using the same simple landing-to-app transition pattern as the pricing generator.
- Main application should be vaccine-prescription specific and contain no pricing-agreement terminology or agreement-generation behavior.
- Responsive behavior must preserve the vial lineup and avoid overflow on smaller screens.
- Respect `prefers-reduced-motion`: reduce or disable particle movement and aura pulsing for users who request less motion.

## Asset Handling

- Reuse the authoritative `assets/occu-med-logo.png` from the pricing generator unchanged.
- Add the provided vaccine vial artwork to the vaccine repository under `assets/`.
- Do not regenerate or stylistically alter the supplied vial artwork as part of implementation.

## Technical Structure

Create the vaccine app using the same broad separation as the pricing app:

- `app.py`: vaccine generator application and main routing
- `ui_experience.py`: shared dark/glass styling plus vaccine landing scene
- `assets/`: Occu-Med logo and vaccine vial assets
- Render/runtime/requirements files adapted to the vaccine app

The landing animation should be implemented with HTML/CSS/JavaScript inside the Streamlit component layer. Use CSS for aura/bloom animation and a lightweight canvas or DOM particle system for moving particles.

## Verification

Before considering the change complete:

- Python files compile cleanly.
- Streamlit app starts without import/runtime errors.
- Landing page fills the viewport and transitions into the app.
- No pricing-agreement-specific UI remains.
- Occu-Med logo renders from the repository asset.
- Vaccine vial assets render in a horizontal lineup.
- Each vial has a color-matched subtle animated aura.
- Particle field visibly moves and remains performant.
- Reduced-motion mode is respected.
- Layout remains usable on common desktop and mobile widths.
