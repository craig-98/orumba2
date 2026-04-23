# Mobile Optimization Plan & Progress

✅ **Analysis Complete** - Scanned CSS/HTML for @media/classes.

## Current Issues
- Navbar tight on <480px phones
- Hero vh heights bad on iOS Safari
- Typography fixed sizes
- Cards/grids stack late (@768px)
- Inline styles override theme

## Execution Plan (3 Steps)
**Step 1: Mobile.css Base** 
- Mobile-first resets, clamp typography, touch targets
- Import in _header.html

**Step 2: Navbar Mobile Refine**
- Edit navbar-fixed.css: @480px font/gap/padding clamp
- Hamburger touch area 48px+

**Step 3: Page Updates**
- Hero: clamp height, text
- Cards: grid 1-col @600px
- Test: Chrome DevTools iPhone SE

**Dependent Files:**
- static/css/mobile.css (new)
- navbar-fixed.css
- templates/_header.html
- Major pages (home, about*, government*)

**Followup:**
- `python run_server.py` running
- Test on phone/emulator
- Update TODO-Mobile.md

Approve plan?

